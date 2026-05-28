"""Payment Service — FastAPI entry point."""
from fastapi import FastAPI
from app.routes.payments import router as payments_router

app = FastAPI(title="MoneyLendingManager Payment Service", version="1.0.0")
app.include_router(payments_router, prefix="/payments", tags=["payments"])


@app.get("/health")
async def health():
    return {"status": "healthy"}
