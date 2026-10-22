from fastapi import FastAPI
from app.api.endpoints import auth
app = FastAPI(title="QuickDesk API", version="0.1.0")

@app.get("/hello")
def main():
    return {"message": "Hello World"}

app.include_router(auth.router, prefix="/api/v1")