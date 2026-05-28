# MoneyLendingManager — Group Service

## Overview
FastAPI microservice for chit fund group lifecycle, member management, financial calculations, and archival.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/groups` | Create a new group (8-15 members) |
| GET | `/groups` | List groups by manager |
| GET | `/groups/{id}` | Get group details + members |
| PUT | `/groups/{id}` | Update group settings |
| POST | `/groups/{id}/activate` | Activate a DRAFT group |
| POST | `/groups/{id}/members` | Add member |
| DELETE | `/groups/{id}/members/{uid}` | Remove member |
| GET | `/groups/{id}/non-winners` | Get non-winner members |
| POST | `/groups/{id}/deadline` | Set payment deadline |
| POST | `/groups/{id}/archive` | Archive group to S3 |

## Financial Calculations
- **Targeting Amount** = member_slots × amount_per_person
- **Monthly Auction Amount** = targeting_amount ÷ member_slots

## Setup
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8002
```

## Run Tests
```bash
pytest tests/ -v
```
