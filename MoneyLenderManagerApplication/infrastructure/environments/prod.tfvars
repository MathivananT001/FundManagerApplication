# MoneyLendingManager - Production Environment Variables

project_prefix = "mlm"
environment    = "prod"
aws_region     = "ap-south-1"
aws_account_id = "REPLACE_WITH_ACCOUNT_ID"

# VPC
vpc_cidr           = "10.1.0.0/16"
availability_zones = ["ap-south-1a", "ap-south-1b"]
nat_gateway_count  = 2

# RDS
rds_instance_class      = "db.t3.medium"
rds_allocated_storage   = 100
rds_db_name             = "moneylender"
rds_master_username     = "mlm_admin"
rds_multi_az            = true
rds_backup_retention    = 7
rds_deletion_protection = true

# Monitoring
log_retention_days = 90
enable_xray        = true
