# Code Summary — Unit 1: storage-infrastructure

## Generated Files

| File | Purpose |
|------|---------|
| `infrastructure/app.py` | CDK app entry point, instantiates all stacks |
| `infrastructure/cdk.json` | CDK config with dev/prod context |
| `infrastructure/requirements.txt` | Python dependencies (aws-cdk-lib, pytest) |
| `infrastructure/config/environment.py` | Environment config defaults |
| `infrastructure/stacks/vpc_stack.py` | VPC, subnets, NAT, security groups |
| `infrastructure/stacks/database_stack.py` | RDS MySQL + 6 DynamoDB tables |
| `infrastructure/stacks/storage_stack.py` | 4 S3 buckets |
| `infrastructure/stacks/iam_stack.py` | 8 IAM roles (per-service least-privilege) |
| `infrastructure/stacks/monitoring_stack.py` | CloudWatch log groups + dashboard |
| `infrastructure/migrations/001_initial_schema.sql` | Full RDS schema (9 tables) |
| `infrastructure/migrations/seed_data.sql` | Dev seed data |
| `infrastructure/tests/test_*.py` | 14 CDK assertion tests |
| `infrastructure/README.md` | Deployment instructions |

## Key Outputs for Downstream Units

| Output | Consumer |
|--------|----------|
| VPC ID + Subnet IDs | All ECS services |
| Security Group IDs | All services |
| RDS Endpoint + Secret ARN | auth, group, auction, payment, report services |
| DynamoDB Table Names | auth (sessions), auction (connections/state), notification (logs/tokens), bot (activity) |
| S3 Bucket ARNs | payment (proofs), report (reports), group (archives), notification (localization) |
| IAM Role ARNs | All services |

## Stories Completed
- ✅ US-033 — RDS MySQL, DynamoDB, S3 provisioning
- ✅ US-034 — IAM, VPC, CloudWatch setup
