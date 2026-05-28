# Payment Proofs Bucket
resource "aws_s3_bucket" "payment_proofs" {
  bucket = "${var.project_prefix}-payment-proofs-${var.environment}-${var.aws_account_id}"

  tags = {
    Name        = "${var.project_prefix}-payment-proofs"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "payment_proofs" {
  bucket                  = aws_s3_bucket.payment_proofs.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_cors_configuration" "payment_proofs" {
  bucket = aws_s3_bucket.payment_proofs.id

  cors_rule {
    allowed_headers = ["*"]
    allowed_methods = ["PUT", "GET"]
    allowed_origins = ["*"]
    max_age_seconds = 3600
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "payment_proofs" {
  bucket = aws_s3_bucket.payment_proofs.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# Reports Bucket
resource "aws_s3_bucket" "reports" {
  bucket = "${var.project_prefix}-reports-${var.environment}-${var.aws_account_id}"

  tags = {
    Name        = "${var.project_prefix}-reports"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "reports" {
  bucket                  = aws_s3_bucket.reports.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    id     = "expire-temp-reports"
    status = "Enabled"

    expiration {
      days = 30
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "reports" {
  bucket = aws_s3_bucket.reports.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# Group Archives Bucket
resource "aws_s3_bucket" "archives" {
  bucket = "${var.project_prefix}-group-archives-${var.environment}-${var.aws_account_id}"

  tags = {
    Name        = "${var.project_prefix}-group-archives"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "archives" {
  bucket                  = aws_s3_bucket.archives.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_lifecycle_configuration" "archives" {
  bucket = aws_s3_bucket.archives.id

  rule {
    id     = "glacier-transition"
    status = "Enabled"

    transition {
      days          = 90
      storage_class = "GLACIER"
    }
  }
}

resource "aws_s3_bucket_server_side_encryption_configuration" "archives" {
  bucket = aws_s3_bucket.archives.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}

# Localization Bucket
resource "aws_s3_bucket" "localization" {
  bucket = "${var.project_prefix}-localization-${var.environment}-${var.aws_account_id}"

  tags = {
    Name        = "${var.project_prefix}-localization"
    Environment = var.environment
  }
}

resource "aws_s3_bucket_public_access_block" "localization" {
  bucket                  = aws_s3_bucket.localization.id
  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_server_side_encryption_configuration" "localization" {
  bucket = aws_s3_bucket.localization.id

  rule {
    apply_server_side_encryption_by_default {
      sse_algorithm = "aws:kms"
    }
  }
}
