from fastapi import FastAPI, Depends
from routes import users, auth, product

from core.database import Base, engine, get_db
from sqlalchemy import text


app = FastAPI()

app.include_router(users.router)
app.include_router(auth.router)
app.include_router(product.router)

@app.get("/")
def home():
    return {"message": "E-commerce API is running!"}

@app.get("/health/db")
def check_database(db=Depends(get_db)):
    db.execute(text("SELECT 1"))
    return {"ok": True, "database": "connected"}