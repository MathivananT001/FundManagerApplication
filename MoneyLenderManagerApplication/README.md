# MoneyLendingManager

A mobile-first chit fund (self-funding group) management platform for fund managers and their member groups. Built with Flutter (Android), FastAPI (Python), and AWS.

## Architecture

```
Flutter App → API Gateway (REST + WebSocket) → ECS Fargate Microservices → RDS MySQL + DynamoDB + S3
                                             → Lambda (Reports, Bot Agent)
```

## Services

| Service | Technology | Port | Description |
|---------|-----------|------|-------------|
| infrastructure | Terraform | — | VPC, RDS, DynamoDB, S3, IAM, API Gateway |
| auth-service | FastAPI | 8001 | Authentication via Cognito, profiles, roles |
| group-service | FastAPI | 8002 | Group lifecycle, members, financial calculations |
| notification-service | FastAPI + Lambda | 8003 | SMS, push, bot reminders, localization |
| payment-service | FastAPI | 8004 | Contributions, proof uploads, defaulter tracking |
| auction-service | FastAPI | 8005 | Live bidding via WebSocket, winner determination |
| report-service | Lambda | — | PDF/Excel report generation |
| flutter-app | Flutter | — | Android mobile client |

## Quick Start (Local)

```bash
# Start all backend services + MySQL
docker-compose up

# Run Flutter app
cd flutter-app
flutter pub get
flutter run --dart-define=API_BASE_URL=http://localhost:8001
```

## Key Business Rules

- Groups: 8–15 members + 1 bot agent
- Monthly auction: highest bidder wins the pot
- No bids → random selection from non-winners
- **Disbursement** = Monthly Auction Amount − Winning Bid − Manager Fee
- Fund manager manually confirms payments (no payment gateway in MVP)
- Bilingual: Tamil + English (server-driven localization)
- Currency: INR (₹)

## Documentation

- `aidlc-docs/construction/build-and-test/` — Build & test instructions
- `aidlc-docs/operations/` — Deployment, monitoring, production checklist
- Each service has its own `README.md`
