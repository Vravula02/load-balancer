import uvicorn
from fastapi import FastAPI
import argparse
import asyncio
import random

app = FastAPI()

PORT = 8001

@app.get("/")
async def home():
    delay = random.uniform(0.01, 0.1)
    await asyncio.sleep(delay)
    return {"message": "Hello from backend!", "port": PORT}

@app.get("/health")
async def health():
    return {"status": "healthy", "port": PORT}

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--port", type=int, default=8001)
    args = parser.parse_args()
    PORT = args.port
    uvicorn.run(app, host="0.0.0.0", port=PORT)