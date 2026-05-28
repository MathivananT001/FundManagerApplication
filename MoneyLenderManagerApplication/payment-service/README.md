# MoneyLendingManager — Payment Service

## Overview
FastAPI microservice for contribution tracking, manual payment confirmation, proof attachments, and defaulter management.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/payments/{group_id}/{month}` | Contribution ledger |
| POST | `/payments/{id}/confirm` | Fund manager confirms payment |
| POST | `/payments/{id}/reject` | Fund manager rejects payment |
| POST | `/payments/{id}/proof/upload-url` | Get presigned URL for proof upload |
| GET | `/payments/{id}/attachments` | Get proof attachments with download URLs |
| GET | `/payments/{group_id}/unpaid/{month}` | Unpaid members dashboard |
| GET | `/payments/overdue` | All overdue payments (Bot Agent) |

## Key Design
- Fund manager confirmation is **mandatory** — proof is optional evidence only
- Proof uploads go directly from Flutter to S3 via presigned PUT URL
- No payment gateway (MVP) — members pay offline

## Setup
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8004
```

## Run Tests
```bash
pytest tests/ -v
```
