terraform {
  required_version = ">= 1.5.0"

  required_providers {
    aws = {
      source  = "hashicorp/aws"
      version = "~> 5.0"
    }
    random = {
      source  = "hashicorp/random"
      version = "~> 3.5"
    }
  }
}

provider "aws" {
  region = var.aws_region
}

module "vpc" {
  source = "./modules/vpc"

  project_prefix     = var.project_prefix
  environment        = var.environment
  vpc_cidr           = var.vpc_cidr
  availability_zones = var.availability_zones
  nat_gateway_count  = var.nat_gateway_count
}

module "database" {
  source = "./modules/database"

  project_prefix        = var.project_prefix
  environment           = var.environment
  vpc_id                = module.vpc.vpc_id
  isolated_subnet_ids   = module.vpc.isolated_subnet_ids
  rds_security_group_id = module.vpc.rds_security_group_id
  rds_instance_class    = var.rds_instance_class
  rds_allocated_storage = var.rds_allocated_storage
  rds_db_name           = var.rds_db_name
  rds_master_username   = var.rds_master_username
  rds_multi_az          = var.rds_multi_az
  rds_backup_retention  = var.rds_backup_retention
  rds_deletion_protection = var.rds_deletion_protection
}

module "storage" {
  source = "./modules/storage"

  project_prefix = var.project_prefix
  environment    = var.environment
  aws_account_id = var.aws_account_id
}

module "iam" {
  source = "./modules/iam"

  project_prefix                  = var.project_prefix
  environment                     = var.environment
  rds_secret_arn                  = module.database.rds_secret_arn
  dynamodb_sessions_arn           = module.database.dynamodb_sessions_arn
  dynamodb_auction_connections_arn = module.database.dynamodb_auction_connections_arn
  dynamodb_auction_state_arn      = module.database.dynamodb_auction_state_arn
  dynamodb_notification_logs_arn  = module.database.dynamodb_notification_logs_arn
  dynamodb_device_tokens_arn      = module.database.dynamodb_device_tokens_arn
  dynamodb_bot_activity_log_arn   = module.database.dynamodb_bot_activity_log_arn
  payment_proofs_bucket_arn       = module.storage.payment_proofs_bucket_arn
  reports_bucket_arn              = module.storage.reports_bucket_arn
  archives_bucket_arn             = module.storage.archives_bucket_arn
}

module "monitoring" {
  source = "./modules/monitoring"

  project_prefix     = var.project_prefix
  environment        = var.environment
  log_retention_days = var.log_retention_days
}

module "cognito" {
  source = "./modules/cognito"

  project_prefix       = var.project_prefix
  environment          = var.environment
  google_client_id     = var.google_client_id
  google_client_secret = var.google_client_secret
}

module "sqs" {
  source = "./modules/sqs"

  project_prefix = var.project_prefix
  environment    = var.environment
}

module "cloudfront" {
  source = "./modules/cloudfront"

  project_prefix         = var.project_prefix
  environment            = var.environment
  localization_bucket_id  = module.storage.localization_bucket_id
  localization_bucket_arn = module.storage.localization_bucket_arn
}

module "ecs" {
  source = "./modules/ecs"

  project_prefix        = var.project_prefix
  environment           = var.environment
  aws_region            = var.aws_region
  vpc_id                = module.vpc.vpc_id
  private_subnet_ids    = module.vpc.private_subnet_ids
  ecs_security_group_id = module.vpc.ecs_security_group_id
  ecs_execution_role_arn = module.iam.ecs_execution_role_arn

  service_images = {
    "auth-service"         = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_prefix}-auth-service:latest"
    "group-service"        = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_prefix}-group-service:latest"
    "auction-service"      = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_prefix}-auction-service:latest"
    "payment-service"      = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_prefix}-payment-service:latest"
    "notification-service" = "${var.aws_account_id}.dkr.ecr.${var.aws_region}.amazonaws.com/${var.project_prefix}-notification-service:latest"
  }

  service_task_role_arns = {
    "auth-service"         = module.iam.auth_service_role_arn
    "group-service"        = module.iam.group_service_role_arn
    "auction-service"      = module.iam.auction_service_role_arn
    "payment-service"      = module.iam.payment_service_role_arn
    "notification-service" = module.iam.notification_service_role_arn
  }

  service_env_vars = {
    "auth-service" = [
      { name = "DATABASE_URL", value = "mysql+pymysql://${var.rds_master_username}@${module.database.rds_endpoint}/${var.rds_db_name}" },
      { name = "COGNITO_USER_POOL_ID", value = module.cognito.user_pool_id },
      { name = "COGNITO_CLIENT_ID", value = module.cognito.client_id },
      { name = "DYNAMODB_SESSIONS_TABLE", value = "${var.project_prefix}-sessions-${var.environment}" },
      { name = "AWS_REGION", value = var.aws_region },
    ]
    "group-service" = [
      { name = "DATABASE_URL", value = "mysql+pymysql://${var.rds_master_username}@${module.database.rds_endpoint}/${var.rds_db_name}" },
      { name = "S3_ARCHIVES_BUCKET", value = module.storage.archives_bucket_id },
      { name = "AWS_REGION", value = var.aws_region },
    ]
    "auction-service" = [
      { name = "DATABASE_URL", value = "mysql+pymysql://${var.rds_master_username}@${module.database.rds_endpoint}/${var.rds_db_name}" },
      { name = "DYNAMODB_AUCTION_CONNECTIONS_TABLE", value = "${var.project_prefix}-auction-connections-${var.environment}" },
      { name = "DYNAMODB_AUCTION_STATE_TABLE", value = "${var.project_prefix}-auction-state-${var.environment}" },
      { name = "GROUP_SERVICE_URL", value = "http://group-service.${var.project_prefix}.internal:8000" },
      { name = "AWS_REGION", value = var.aws_region },
    ]
    "payment-service" = [
      { name = "DATABASE_URL", value = "mysql+pymysql://${var.rds_master_username}@${module.database.rds_endpoint}/${var.rds_db_name}" },
      { name = "S3_PAYMENT_PROOFS_BUCKET", value = module.storage.payment_proofs_bucket_id },
      { name = "NOTIFICATION_SERVICE_URL", value = "http://notification-service.${var.project_prefix}.internal:8000" },
      { name = "AWS_REGION", value = var.aws_region },
    ]
    "notification-service" = [
      { name = "SQS_NOTIFICATION_QUEUE_URL", value = module.sqs.notification_queue_url },
      { name = "DYNAMODB_NOTIFICATION_LOGS_TABLE", value = "${var.project_prefix}-notification-logs-${var.environment}" },
      { name = "DYNAMODB_DEVICE_TOKENS_TABLE", value = "${var.project_prefix}-device-tokens-${var.environment}" },
      { name = "LOCALIZATION_BUCKET", value = module.storage.localization_bucket_id },
      { name = "AWS_REGION", value = var.aws_region },
    ]
  }
}

module "eventbridge" {
  source = "./modules/eventbridge"

  project_prefix       = var.project_prefix
  environment          = var.environment
  bot_agent_lambda_arn = module.iam.bot_agent_lambda_role_arn
}

module "api_gateway" {
  source = "./modules/api_gateway"

  project_prefix           = var.project_prefix
  environment              = var.environment
  aws_region               = var.aws_region
  cognito_user_pool_arn    = module.cognito.user_pool_arn
  report_lambda_arn        = ""  # Set after Lambda is deployed
  report_lambda_invoke_arn = ""  # Set after Lambda is deployed
}
