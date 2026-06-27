from math import sqrt

from huggingface_hub import InferenceClient
from sqlalchemy import func, select
from sqlalchemy.orm import Session

from core.config import HF_API_TOKEN, HF_RECOMMENDER_MODEL
from models.cart import Cart, CartItem
from models.order import Order, OrderItem
from models.product import Product


_client: InferenceClient | None = None


def _get_client() -> InferenceClient:
    global _client

    if _client is None:
        if not HF_API_TOKEN:
            raise RuntimeError("Set HF_API_TOKEN in your .env")
        _client = InferenceClient(token=HF_API_TOKEN)

    return _client


def _active_products(db: Session) -> list[Product]:
    return list(
        db.scalars(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.id)
        )
    )


def _product_text(product: Product) -> str:
    category = (product.category or "Uncategorized").strip()
    description = (product.description or "").strip()

    return f"{product.name}. Category: {category}. Description: {description}"


def _normalize_embedding(raw_embedding) -> list[float]:
    if isinstance(raw_embedding, list) and raw_embedding and isinstance(raw_embedding[0], list):
        return [float(value) for value in raw_embedding[0]]

    return [float(value) for value in raw_embedding]


def _embed_text(client: InferenceClient, text: str) -> list[float]:
    raw = client.feature_extraction(text, model=HF_RECOMMENDER_MODEL)
    return _normalize_embedding(raw)


def _embed_products(
    client: InferenceClient,
    products: list[Product],
) -> dict[int, list[float]]:
    embeddings: dict[int, list[float]] = {}

    for product in products:
        embeddings[product.id] = _embed_text(client, _product_text(product))

    return embeddings


def _average_vectors(vectors: list[list[float]]) -> list[float]:
    if not vectors:
        return []

    size = len(vectors[0])

    return [
        sum(vector[index] for vector in vectors) / len(vectors)
        for index in range(size)
    ]


def _cosine_similarity(left: list[float], right: list[float]) -> float:
    if not left or not right or len(left) != len(right):
        return 0.0

    dot = sum(l * r for l, r in zip(left, right))
    left_norm = sqrt(sum(l * l for l in left))
    right_norm = sqrt(sum(r * r for r in right))

    if left_norm == 0 or right_norm == 0:
        return 0.0

    return dot / (left_norm * right_norm)


def _fallback_recommendations(
    products: list[Product],
    top_k: int,
) -> tuple[str, list[tuple[Product, float]]]:
    fallback = [
        (product, 0.0)
        for product in sorted(products, key=lambda p: p.id, reverse=True)[:top_k]
    ]

    return "cold_start_fallback", fallback


def _popularity_scores(db: Session) -> dict[int, float]:
    scores: dict[int, float] = {}

    ordered_rows = db.execute(
        select(OrderItem.product_id, func.sum(OrderItem.quantity).label("score"))
        .group_by(OrderItem.product_id)
    ).all()

    for product_id, score in ordered_rows:
        scores[int(product_id)] = float(score or 0)

    cart_rows = db.execute(
        select(CartItem.product_id, func.sum(CartItem.quantity).label("score"))
        .group_by(CartItem.product_id)
    ).all()

    for product_id, score in cart_rows:
        pid = int(product_id)
        scores[pid] = scores.get(pid, 0.0) + float(score or 0)

    return scores


def _rank_products(
    products: list[Product],
    embeddings: dict[int, list[float]],
    profile_vector: list[float],
    top_k: int,
    boost_scores: dict[int, float] | None = None,
    boost_scale: float = 0.0,
) -> list[tuple[Product, float]]:
    scored_items: list[tuple[Product, float]] = []

    for product in products:
        product_vector = embeddings.get(product.id)

        if not product_vector:
            continue

        semantic_score = _cosine_similarity(profile_vector, product_vector)

        boost = 0.0
        if boost_scores is not None:
            boost = boost_scale * boost_scores.get(product.id, 0.0)

        scored_items.append((product, semantic_score + boost))

    scored_items.sort(key=lambda item: item[1], reverse=True)
    return scored_items[:top_k]


def generate_customer_recommendations(
    db: Session,
    user_id: int,
    top_k: int,
) -> tuple[str, list[tuple[Product, float]]]:
    products = _active_products(db)

    if not products:
        return "no_active_products", []

    ordered_product_ids = db.scalars(
        select(OrderItem.product_id)
        .join(Order, Order.id == OrderItem.order_id)
        .where(Order.user_id == user_id)
    ).all()

    cart_product_ids = db.scalars(
        select(CartItem.product_id)
        .join(Cart, Cart.id == CartItem.cart_id)
        .where(Cart.user_id == user_id)
    ).all()

    interacted_ids = {
        int(pid)
        for pid in ordered_product_ids + cart_product_ids
        if pid is not None
    }

    if not interacted_ids:
        return _fallback_recommendations(products, top_k)

    products_by_id = {product.id: product for product in products}

    active_interacted_products = [
        products_by_id[pid]
        for pid in interacted_ids
        if pid in products_by_id
    ]

    if not active_interacted_products:
        return _fallback_recommendations(products, top_k)

    candidate_products = [
        product
        for product in products
        if product.id not in interacted_ids
    ]

    if not candidate_products:
        return "customer_ai_profile", []

    client = _get_client()

    embeddings = _embed_products(
        client,
        active_interacted_products + candidate_products,
    )

    profile_vectors = [
        embeddings[product.id]
        for product in active_interacted_products
        if product.id in embeddings
    ]

    profile_vector = _average_vectors(profile_vectors)

    if not profile_vector:
        return _fallback_recommendations(products, top_k)

    scored_items = _rank_products(
        products=candidate_products,
        embeddings=embeddings,
        profile_vector=profile_vector,
        top_k=top_k,
    )

    return "customer_ai_profile", scored_items


def generate_guest_recommendations(
    db: Session,
    top_k: int,
) -> tuple[str, list[tuple[Product, float]]]:
    products = _active_products(db)

    if not products:
        return "no_active_products", []

    popularity_scores = _popularity_scores(db)

    if not popularity_scores:
        return _fallback_recommendations(products, top_k)

    client = _get_client()

    products_by_id = {product.id: product for product in products}

    top_seed_ids = [
        product_id
        for product_id, _score in sorted(
            popularity_scores.items(),
            key=lambda item: item[1],
            reverse=True,
        )[:3]
        if product_id in products_by_id
    ]

    seed_products = [
        products_by_id[product_id]
        for product_id in top_seed_ids
    ]

    if not seed_products:
        return _fallback_recommendations(products, top_k)

    embeddings = _embed_products(client, products)

    seed_vectors = [
        embeddings[product.id]
        for product in seed_products
        if product.id in embeddings
    ]

    guest_profile = _average_vectors(seed_vectors)

    if not guest_profile:
        return _fallback_recommendations(products, top_k)

    scored_items = _rank_products(
        products=products,
        embeddings=embeddings,
        profile_vector=guest_profile,
        top_k=top_k,
        boost_scores=popularity_scores,
        boost_scale=0.01,
    )

    return "guest_ai_popularity", scored_items