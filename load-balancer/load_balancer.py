import threading
import time
import httpx
from fastapi import FastAPI, HTTPException
from contextlib import asynccontextmanager
import uvicorn

BACKENDS = [
    {"url": "http://localhost:8001", "connections": 0, "healthy": True},
    {"url": "http://localhost:8002", "connections": 0, "healthy": True},
    {"url": "http://localhost:8003", "connections": 0, "healthy": True},
]

lock = threading.Lock()
rr_index = 0
client = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global client
    client = httpx.AsyncClient(timeout=10)
    threading.Thread(target=health_check, daemon=True).start()
    yield
    await client.aclose()

app = FastAPI(lifespan=lifespan)

def get_round_robin():
    global rr_index
    with lock:
        healthy = [b for b in BACKENDS if b["healthy"]]
        if not healthy:
            return None
        backend = healthy[rr_index % len(healthy)]
        rr_index += 1
        return backend

def get_least_connections():
    with lock:
        healthy = [b for b in BACKENDS if b["healthy"]]
        if not healthy:
            return None
        return min(healthy, key=lambda b: b["connections"])

def health_check():
    while True:
        for backend in BACKENDS:
            try:
                r = httpx.get(f"{backend['url']}/health", timeout=2)
                backend["healthy"] = r.status_code == 200
            except:
                backend["healthy"] = False
        time.sleep(5)

@app.get("/rr")
async def round_robin():
    backend = get_round_robin()
    if not backend:
        raise HTTPException(status_code=503, detail="No healthy backends")
    with lock:
        backend["connections"] += 1
    try:
        r = await client.get(f"{backend['url']}/")
        return r.json()
    except Exception as e:
        backend["healthy"] = False
        raise HTTPException(status_code=502, detail="Backend failed")
    finally:
        with lock:
            backend["connections"] -= 1

@app.get("/lc")
async def least_connections():
    backend = get_least_connections()
    if not backend:
        raise HTTPException(status_code=503, detail="No healthy backends")
    with lock:
        backend["connections"] += 1
    try:
        r = await client.get(f"{backend['url']}/")
        return r.json()
    except Exception as e:
        backend["healthy"] = False
        raise HTTPException(status_code=502, detail="Backend failed")
    finally:
        with lock:
            backend["connections"] -= 1

@app.get("/status")
def status():
    return {"backends": BACKENDS}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)