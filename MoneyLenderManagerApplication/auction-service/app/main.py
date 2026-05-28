"""Auction Service — FastAPI entry point."""
from fastapi import FastAPI
from app.routes.auctions import router as auctions_router

app = FastAPI(title="MoneyLendingManager Auction Service", version="1.0.0")
app.include_router(auctions_router, prefix="/auctions", tags=["auctions"])


@app.get("/health")
async def health():
    return {"status": "healthy"}
