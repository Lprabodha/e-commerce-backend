from fastapi import FastAPI
from routes import users

app = FastAPI()

app.include_router(users.router)

@app.get("/")
def home():
    return {"message": "E-commerce API is running!"}
