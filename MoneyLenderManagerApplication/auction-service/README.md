# MoneyLendingManager — Auction Service

## Overview
FastAPI microservice for live auction lifecycle, real-time bidding via WebSocket, winner determination, and disbursement calculation.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/auctions` | Schedule a new auction |
| POST | `/auctions/{id}/open` | Open auction for bidding |
| POST | `/auctions/{id}/bid` | Place a bid (broadcasts via WebSocket) |
| POST | `/auctions/{id}/close` | Close auction, determine winner |
| GET | `/auctions/{id}` | Get auction details + bid history |
| GET | `/auctions/group/{group_id}` | List auctions for a group |
| GET | `/auctions/{id}/highest-bid` | Current highest bid |
| GET | `/auctions/upcoming` | Upcoming auctions (Bot Agent) |
| POST | `/auctions/ws/connect` | Register WebSocket connection |
| POST | `/auctions/ws/disconnect` | Remove WebSocket connection |

## Winner Determination
1. **Bids exist** → Highest bidder wins (US-013)
2. **No bids** → Random selection from non-winners (US-014)

## Disbursement Formula
```
disbursement = monthly_auction_amount - winning_bid - manager_fee
```

## Setup
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8005
```

## Run Tests
```bash
pytest tests/ -v
```
