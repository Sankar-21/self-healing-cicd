from fastapi import FastAPI

app = FastAPI()

@app.get("/")
def root():
    return {"status": "ok", "service": "self-healing-cicd"}

@app.get("/health")
def health():
    return {"healthy": True}

@app.get("/add")
def add(a: int, b: int):
    return {"result": a + b}