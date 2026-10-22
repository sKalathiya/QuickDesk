from fastapi import FastAPI
app = FastAPI()

@app.get("/hello")
def main():
    return {"message": "Hello World"}
