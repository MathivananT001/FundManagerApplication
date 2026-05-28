# Operations — Monitoring & Observability

## CloudWatch Log Groups

| Service | Log Group |
|---------|-----------|
| auth-service | `/mlm/prod/auth` |
| group-service | `/mlm/prod/group` |
| auction-service | `/mlm/prod/auction` |
| payment-service | `/mlm/prod/payment` |
| notification-service | `/mlm/prod/notification` |
| report-service | `/mlm/prod/report` |
| bot-agent | `/mlm/prod/bot-agent` |

## Key Metrics to Monitor

| Metric | Threshold | Action |
|--------|-----------|--------|
| RDS CPU | > 80% | Scale up instance class |
| RDS Connections | > 80% of max | Check connection pooling |
| ECS Task CPU | > 70% | Auto-scale tasks |
| Lambda Duration | > 10s (report) | Optimize queries |
| Lambda Errors | > 5/min | Check logs, alert |
| API Gateway 5xx | > 1% | Investigate service health |
| DynamoDB Throttles | > 0 | Check capacity |

## Alarms (CloudWatch)

```bash
# RDS CPU alarm
aws cloudwatch put-metric-alarm \
  --alarm-name mlm-rds-cpu-high \
  --metric-name CPUUtilization \
  --namespace AWS/RDS \
  --statistic Average \
  --period 300 \
  --threshold 80 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 2 \
  --dimensions Name=DBInstanceIdentifier,Value=mlm-mysql-prod

# API Gateway 5xx alarm
aws cloudwatch put-metric-alarm \
  --alarm-name mlm-api-5xx \
  --metric-name 5xx \
  --namespace AWS/ApiGateway \
  --statistic Sum \
  --period 60 \
  --threshold 10 \
  --comparison-operator GreaterThanThreshold \
  --evaluation-periods 1
```

## Health Check Endpoints

All services expose `GET /health` returning `{"status": "healthy"}`.

Recommended: Configure ECS health checks and API Gateway health routes.

## Incident Response

1. **Service Down**: Check ECS task status, CloudWatch logs
2. **Database Issues**: Check RDS metrics, connection count, slow query log
3. **Auction WebSocket Issues**: Check DynamoDB AuctionConnections table, API Gateway WebSocket metrics
4. **Notification Failures**: Check SQS DLQ, SNS delivery status
