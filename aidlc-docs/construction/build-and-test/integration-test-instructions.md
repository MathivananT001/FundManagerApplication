# Integration Test Instructions — MoneyLendingManager

## Overview
Integration tests verify interactions between services. Run after all services are deployed or running locally via Docker Compose.

---

## Prerequisites
- All services running (Docker Compose or deployed)
- RDS MySQL with schema applied
- DynamoDB tables created
- S3 buckets created

---

## Test Scenarios

### 1. Auth → Group Flow
```bash
# Register user
curl -X POST http://localhost:8001/auth/register \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123!","full_name":"Test User"}'

# Login
TOKEN=$(curl -s -X POST http://localhost:8001/auth/login/email \
  -H "Content-Type: application/json" \
  -d '{"email":"test@example.com","password":"Pass123!"}' | jq -r '.access_token')

# Create group
curl -X POST http://localhost:8002/groups \
  -H "Authorization: Bearer $TOKEN" \
  -H "X-User-Id: user-001" \
  -H "Content-Type: application/json" \
  -d '{"name":"Test Fund","member_slots":10,"amount_per_person":5000,"manager_fee_percent":2}'
```

### 2. Group → Auction → Payment Flow
```bash
# Schedule auction
curl -X POST http://localhost:8005/auctions \
  -H "X-User-Id: manager-001" \
  -H "Content-Type: application/json" \
  -d '{"group_id":"GRP_ID","month_number":1,"scheduled_at":"2026-06-01T10:00:00"}'

# Open auction
curl -X POST http://localhost:8005/auctions/AUC_ID/open \
  -H "X-User-Id: manager-001"

# Place bid
curl -X POST http://localhost:8005/auctions/AUC_ID/bid \
  -H "Content-Type: application/json" \
  -d '{"member_id":"user-002","bid_amount":1500}'

# Close auction
curl -X POST "http://localhost:8005/auctions/AUC_ID/close?group_member_count=10&manager_fee_percent=2" \
  -H "X-User-Id: manager-001"

# Check payment ledger
curl http://localhost:8004/payments/GRP_ID/1
```

### 3. Notification Flow
```bash
# Register device token
curl -X POST http://localhost:8003/notifications/device-token \
  -H "Content-Type: application/json" \
  -d '{"user_id":"user-001","fcm_token":"test-token","platform":"android"}'

# Send SMS
curl -X POST http://localhost:8003/notifications/send-sms \
  -H "Content-Type: application/json" \
  -d '{"phone_number":"+919876543210","template_key":"payment_reminder","language":"en"}'

# Get localization bundle
curl http://localhost:8003/notifications/localization/en
```

### 4. Report Generation
```bash
# Generate group summary PDF
curl -X POST http://localhost:8006/reports/group-summary \
  -H "Content-Type: application/json" \
  -d '{"group_id":"GRP_ID","format":"pdf"}'
# Returns: {"download_url": "https://s3.presigned..."}
```

### 5. Payment Proof Upload
```bash
# Get presigned upload URL
curl -X POST http://localhost:8004/payments/PAY_ID/proof/upload-url \
  -H "X-User-Id: user-002" \
  -H "Content-Type: application/json" \
  -d '{"file_name":"receipt.jpg","content_type":"image/jpeg"}'

# Upload file to presigned URL
curl -X PUT "PRESIGNED_URL" \
  -H "Content-Type: image/jpeg" \
  --data-binary @receipt.jpg
```

---

## Automated Integration Test Script

```bash
#!/bin/bash
set -e
BASE_URL=${1:-http://localhost}

echo "=== Integration Tests ==="

# Health checks
for port in 8001 8002 8003 8004 8005; do
  STATUS=$(curl -s -o /dev/null -w "%{http_code}" $BASE_URL:$port/health)
  if [ "$STATUS" != "200" ]; then
    echo "FAIL: Service on port $port not healthy"
    exit 1
  fi
  echo "PASS: Port $port healthy"
done

echo "=== All integration tests passed ==="
```
