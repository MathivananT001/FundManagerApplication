# MoneyLendingManager — Notification Service

## Overview
FastAPI microservice + Lambda handlers for SMS (SNS), push (FCM), bot reminders, and localization.

## Endpoints

| Method | Path | Description |
|--------|------|-------------|
| POST | `/notifications/send-sms` | Send localized SMS |
| POST | `/notifications/send-push` | Send push to user's devices |
| POST | `/notifications/send-bulk-sms` | Bulk SMS |
| POST | `/notifications/send-bulk-push` | Bulk push |
| POST | `/notifications/device-token` | Register FCM token |
| DELETE | `/notifications/device-token` | Deregister FCM token |
| GET | `/notifications/history/{user_id}` | Notification history |
| GET | `/notifications/localization/{lang}` | Get language bundle (en/ta) |

## Bot Agent Lambda Handlers

| Handler | Trigger | Description |
|---------|---------|-------------|
| `run_payment_reminders` | EventBridge daily | SMS reminders for overdue payments |
| `run_auction_reminders` | EventBridge every 30min | Push reminders for upcoming auctions |
| `report_pre_auction_attendance` | Invoked by Auction Service | Reports connected members |

## Setup
```bash
cp .env.example .env
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8003
```

## Run Tests
```bash
pytest tests/ -v
```
