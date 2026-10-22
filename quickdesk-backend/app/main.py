from fastapi import FastAPI
from app.api.endpoints import auth
app = FastAPI()

@app.get("/hello")
def main():
    return {"message": "Hello World"}

app.include_router(auth.router)