"""Notification Service — FastAPI entry point."""
from fastapi import FastAPI
from app.routes.notifications import router as notification_router

app = FastAPI(title="MoneyLendingManager Notification Service", version="1.0.0")
app.include_router(notification_router, prefix="/notifications", tags=["notifications"])


@app.get("/health")
async def health():
    return {"status": "healthy"}
