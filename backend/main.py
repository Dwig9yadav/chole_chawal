from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.api import router as api_router

app = FastAPI(title="VoxAI Backend", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(api_router)


@app.get("/")
def root():
    return {"name": "VoxAI", "message": "Voice Study Assistant API is running"}
