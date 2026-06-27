from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from routes import users, auth, product, cart, orders, chat

from core.database import Base, engine, get_db
from core.config import CORS_ORIGINS
from sqlalchemy import text


app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(product.router)
app.include_router(cart.router)
app.include_router(orders.router)
app.include_router(chat.router)

@app.get("/")
def home():
    return {"message": "E-commerce API is running!"}

@app.get("/health/db")
def check_database(db=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True, "database": "connected"}