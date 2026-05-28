"""Group Service — FastAPI entry point."""
from fastapi import FastAPI
from app.routes.groups import router as groups_router

app = FastAPI(title="MoneyLendingManager Group Service", version="1.0.0")
app.include_router(groups_router, prefix="/groups", tags=["groups"])


@app.get("/health")
async def health():
    return {"status": "healthy"}
