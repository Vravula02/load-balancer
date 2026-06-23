import uvicorn
from fastapi import FastAPI
import argparse
import time
import random

app = FastAPI()

@app.get("/")
def home():
    # Simulate variable response time
    delay = random.uniform(0.01, 0.1)
    time.sleep(delay)
    return {"message": "Hello from backend!", "port": PORT}

@app.get("/health")
def health():
    return {"status": "healthy", "port": PORT}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    PORT = args.port
    uvicorn.run(app, host="0.0.0.0", port=PORT)