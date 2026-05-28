"""Auth Service — FastAPI entry point."""
from fastapi import FastAPI
from app.routes.auth import router as auth_router

app = FastAPI(title="MoneyLendingManager Auth Service", version="1.0.0")
app.include_router(auth_router, prefix="/auth", tags=["auth"])


@app.get("/health")
async def health():
    return {"status": "healthy"}
