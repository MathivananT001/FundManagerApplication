# Unit Test Instructions — MoneyLendingManager

## Test Framework
- **Backend**: pytest (Python)
- **Infrastructure**: terraform validate + plan
- **Flutter**: flutter_test

---

## 1. Infrastructure Tests

```bash
cd MoneyLenderManagerApplication/infrastructure
terraform init
terraform validate
terraform plan -var-file=environments/dev.tfvars  # Dry-run validation
```

---

## 2. Auth Service Tests

```bash
cd MoneyLenderManagerApplication/auth-service
pip install -r requirements.txt
pytest tests/ -v
```

**Test coverage:**
- Health endpoint
- Registration flow (mocked Cognito)
- Email login (success + failure)
- Phone OTP initiation
- Token refresh

---

## 3. Notification Service Tests

```bash
cd MoneyLenderManagerApplication/notification-service
pip install -r requirements.txt
pytest tests/ -v
```

**Test coverage:**
- Health endpoint
- Send SMS (mocked SNS)
- Send push (with/without device tokens)
- Register device token
- Get language bundle

---

## 4. Group Service Tests

```bash
cd MoneyLenderManagerApplication/group-service
pip install -r requirements.txt
pytest tests/ -v
```

**Test coverage:**
- Health endpoint
- Create group (success + invalid slots)
- Add member
- Archive group

---

## 5. Payment Service Tests

```bash
cd MoneyLenderManagerApplication/payment-service
pip install -r requirements.txt
pytest tests/ -v
```

**Test coverage:**
- Health endpoint
- Confirm payment
- Reject payment
- Get presigned upload URL
- Get overdue payments

---

## 6. Auction Service Tests

```bash
cd MoneyLenderManagerApplication/auction-service
pip install -r requirements.txt
pytest tests/ -v
```

**Test coverage:**
- Health endpoint
- Schedule auction
- Place bid (with WebSocket broadcast)
- Close auction (winner determination)

---

## 7. Report Service Tests

```bash
cd MoneyLenderManagerApplication/report-service
pip install -r requirements.txt
pytest tests/ -v
```

**Test coverage:**
- Generate group summary PDF
- Generate group summary Excel
- Generate auction history PDF

---

## 8. Flutter App Tests

```bash
cd MoneyLenderManagerApplication/flutter-app
flutter test
```

---

## Run All Backend Tests (Script)

```bash
#!/bin/bash
set -e
cd MoneyLenderManagerApplication

for svc in auth-service notification-service group-service payment-service auction-service report-service; do
  echo "=== Testing $svc ==="
  cd $svc
  pip install -r requirements.txt -q
  pytest tests/ -v
  cd ..
done

echo "=== All tests passed ==="
```
