# RDS Subnet Group
resource "aws_db_subnet_group" "main" {
  name       = "${var.project_prefix}-db-subnet-${var.environment}"
  subnet_ids = var.isolated_subnet_ids

  tags = {
    Name = "${var.project_prefix}-db-subnet-${var.environment}"
  }
}

# RDS Password in Secrets Manager
resource "aws_secretsmanager_secret" "rds_password" {
  name = "${var.project_prefix}-rds-password-${var.environment}"
}

resource "random_password" "rds" {
  length  = 24
  special = false
}

resource "aws_secretsmanager_secret_version" "rds_password" {
  secret_id     = aws_secretsmanager_secret.rds_password.id
  secret_string = jsonencode({
    username = var.rds_master_username
    password = random_password.rds.result
    host     = aws_db_instance.main.endpoint
    dbname   = var.rds_db_name
  })
}

# RDS MySQL Instance
resource "aws_db_instance" "main" {
  identifier     = "${var.project_prefix}-mysql-${var.environment}"
  engine         = "mysql"
  engine_version = "8.0.35"
  instance_class = var.rds_instance_class

  allocated_storage = var.rds_allocated_storage
  storage_encrypted = true

  db_name  = var.rds_db_name
  username = var.rds_master_username
  password = random_password.rds.result

  db_subnet_group_name   = aws_db_subnet_group.main.name
  vpc_security_group_ids = [var.rds_security_group_id]

  multi_az            = var.rds_multi_az
  backup_retention_period = var.rds_backup_retention
  deletion_protection = var.rds_deletion_protection
  skip_final_snapshot = var.environment != "prod"

  tags = {
    Name        = "${var.project_prefix}-mysql-${var.environment}"
    Environment = var.environment
  }
}

# DynamoDB Tables
resource "aws_dynamodb_table" "sessions" {
  name         = "${var.project_prefix}-sessions-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "session_id"

  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "session_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "auction_connections" {
  name         = "${var.project_prefix}-auction-connections-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "auction_id"
  range_key    = "connection_id"

  attribute {
    name = "auction_id"
    type = "S"
  }
  attribute {
    name = "connection_id"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "auction_state" {
  name         = "${var.project_prefix}-auction-state-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "auction_id"
  range_key    = "event_timestamp"

  attribute {
    name = "auction_id"
    type = "S"
  }
  attribute {
    name = "event_timestamp"
    type = "S"
  }
}

resource "aws_dynamodb_table" "notification_logs" {
  name         = "${var.project_prefix}-notification-logs-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "timestamp"

  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "timestamp"
    type = "S"
  }

  ttl {
    attribute_name = "ttl"
    enabled        = true
  }
}

resource "aws_dynamodb_table" "device_tokens" {
  name         = "${var.project_prefix}-device-tokens-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "user_id"
  range_key    = "token"

  attribute {
    name = "user_id"
    type = "S"
  }
  attribute {
    name = "token"
    type = "S"
  }
}

resource "aws_dynamodb_table" "bot_activity_log" {
  name         = "${var.project_prefix}-bot-activity-log-${var.environment}"
  billing_mode = "PAY_PER_REQUEST"
  hash_key     = "group_id"
  range_key    = "timestamp"

  attribute {
    name = "group_id"
    type = "S"
  }
  attribute {
    name = "timestamp"
    type = "S"
  }
}
