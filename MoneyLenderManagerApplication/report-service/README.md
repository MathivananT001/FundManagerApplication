# MoneyLendingManager — Report Service (Lambda)

## Overview
AWS Lambda functions that generate PDF and Excel reports, upload to S3, and return presigned download URLs.

## Lambda Handlers

| Handler | Description |
|---------|-------------|
| `handler.generate_group_summary_report` | Group overview (members, amounts, status) |
| `handler.generate_member_history_report` | Member contribution history across months |
| `handler.generate_auction_history_report` | All auctions for a group with winners/amounts |

## Input Format
```json
{
  "group_id": "grp-001",
  "member_id": "user-002",  // only for member history
  "format": "pdf"           // "pdf" or "excel"
}
```

## Output
```json
{
  "download_url": "https://s3.presigned...",
  "s3_key": "reports/grp-001/group-summary-20260528.pdf"
}
```

## Deploy
Package with dependencies as a Lambda deployment zip or use a Lambda Layer:
```bash
pip install -r requirements.txt -t package/
cp handler.py package/
cd package && zip -r ../report-service.zip .
```

## Run Tests
```bash
pytest tests/ -v
```
