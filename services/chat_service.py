from fastapi import Depends
from huggingface_hub import InferenceClient
from sqlalchemy import select
from sqlalchemy.orm import Session
from core.database import get_db


from core.config import HF_CHAT_MODEL, HF_CHAT_URL, HF_API_TOKEN
from models.product import Product

_client: InferenceClient | None = None

_SYSTEM_PROMPT = (
    "You are a friendly e-commerce assistant. Start with a short greeting. "
    "Answer only with facts from the provided product catalog. "
    "If the catalog does not contain enough information, say that clearly and ask one short follow-up question. "
    "Do not mention outside knowledge, links, policies, or internal notes."
)

def _build_catalog_context(
    db: Session,
    limit: int = 80
):
    
    products = list(
        db.scalars(
            select(Product)
            .where(Product.is_active == True)
            .order_by(Product.id)
            .limit(limit)
        )
    )
    
    
    if not products:
        return "No active products found in the catalog."
    
    lines: list[str] = []
    
    for product in products:
        price_text = str(product.price)
        description= (product.description or "").strip()
        category = (product.category or "Uncategorized").strip()
        
        line = (
            f"-id={product.id}; name={product.name} category={category};" # id=1; name=Mouse; category=Ele
            f"price={price_text}; stock={product.stock}; description={description}"
        )
        
        lines.append(line)
        
    return "\n".join(lines)


def get_chat_client():
    
    global _client
    
    if _client is None:
        if not HF_API_TOKEN:
            raise RuntimeError("Set HF_TOKEN in your .env file")

        _client = InferenceClient(token=HF_API_TOKEN, base_url=HF_CHAT_URL)
        
    return _client


def generate_chat_reply(
    db: Session,
    customer_message: str
):
    
    catalog_context = _build_catalog_context(db)
    
    if catalog_context == "No active products found in the catalog.":
        return "Hello! we do't have active products in the catalog right now"
    
    client = get_chat_client()
    
    completion = client.chat.completions.create(
        model=HF_CHAT_MODEL,
        messages=[
            {
                "role": "system",
                "content": f"{_SYSTEM_PROMPT}\n\nProduct catalog:\n{catalog_context}",
            },
            {
                "role": "user",
                "content": f"Customer question: {customer_message}",
            },
        ],
        temperature=0.7,
        max_tokens=256,
    )
    
    reply = completion.choices[0].message.content if completion.choices else ""
    
    return (reply or "").strip()
    