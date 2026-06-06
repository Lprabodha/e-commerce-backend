# E-commerce Backend API

Python + AI Master Course project using FastAPI, SQLAlchemy, PostgreSQL, JWT auth, cart and order flows, plus a Hugging Face powered catalog chat assistant.

## Features

- JWT authentication with register and login
- Role-aware routes (customer and admin)
- Product catalog CRUD
- Cart management and checkout
- Order listing, detail, and status updates
- Chat assistant grounded on active products in the database
- Alembic migrations

## Tech stack

- FastAPI
- SQLAlchemy
- PostgreSQL with psycopg2
- Alembic
- Hugging Face Inference API via huggingface_hub

## Requirements

- Python 3.10+
- PostgreSQL

## Setup

1. Create and activate a virtual environment.

```bash
python -m venv venv
source venv/Scripts/activate
```

2. Install dependencies.

```bash
pip install -r requirements.txt
```

3. Create your env file.

```bash
cp .env.example .env
```

If you are on Windows cmd, use:

```bash
copy .env.example .env
```

4. Edit .env values.

Required values:

- DATABASE_URL
- SECRET_KEY
- HF_API_TOKEN

Optional values:

- ACCESS_TOKEN_EXPIRE_MINUTES, default 60
- HF_CHAT_MODEL, default deepseek-ai/DeepSeek-V4-Pro
- HF_CHAT_URL, default https://router.huggingface.co/v1/chat/completions

Example:

```env
DATABASE_URL=postgresql://postgres:postgres@localhost:5432/ecommerce
SECRET_KEY=replace-with-a-long-random-secret
ACCESS_TOKEN_EXPIRE_MINUTES=60
HF_API_TOKEN=hf_xxx
HF_CHAT_MODEL=deepseek-ai/DeepSeek-V4-Pro
HF_CHAT_URL=https://router.huggingface.co/v1/chat/completions
```

Note: the app automatically rewrites DATABASE_URL from postgresql:// to postgresql+psycopg2:// for SQLAlchemy.

## Database migrations

Run migrations after setting DATABASE_URL:

```bash
alembic upgrade head
```

Create a new migration:

```bash
alembic revision --autogenerate -m "describe change"
alembic upgrade head
```

## Run the app

```bash
fastapi dev
```

Alternative:

```bash
uvicorn main:app --reload
```

Open:

- API root: http://127.0.0.1:8000/
- Swagger UI: http://127.0.0.1:8000/docs
- ReDoc: http://127.0.0.1:8000/redoc

## API routes

| Method | Path                      | Description                    |
| ------ | ------------------------- | ------------------------------ |
| GET    | /                         | API status message             |
| GET    | /health/db                | Database connectivity check    |
| POST   | /auth/register            | Register a customer account    |
| POST   | /auth/login               | Login and get access token     |
| GET    | /users/me                 | Current authenticated user     |
| GET    | /users/                   | List users, admin only         |
| GET    | /users/{user_id}          | User profile, owner or admin   |
| POST   | /products                 | Create product, admin only     |
| GET    | /products                 | List active products           |
| GET    | /products/{product_id}    | Get active product by id       |
| PUT    | /products/{product_id}    | Update product, admin only     |
| DELETE | /products/{product_id}    | Delete product, admin only     |
| GET    | /cart                     | Read current user cart         |
| POST   | /cart/items               | Add item to cart               |
| DELETE | /cart/items/{product_id}  | Remove cart item               |
| POST   | /cart/checkout            | Checkout cart and create order |
| GET    | /orders/me                | List current user orders       |
| GET    | /orders/{order_id}        | Order detail, owner or admin   |
| PATCH  | /orders/{order_id}/status | Update status, admin only      |
| POST   | /chat                     | Chat with catalog assistant    |

## Chat endpoint

The chat assistant uses only active products from your database as context. If there are no active products, it returns a fallback reply.

Request body for POST /chat:

```json
{
  "customer_message": "I need a budget wireless mouse"
}
```

Response:

```json
{
  "reply": "Hello! ..."
}
```

If HF_API_TOKEN is missing, the route returns 503 with a clear message.

## Project structure

```text
e-commerce-backend/
  alembic/
  core/
  models/
  routes/
  schemas/
  services/
  main.py
  requirements.txt
  .env.example
  README.md
```
