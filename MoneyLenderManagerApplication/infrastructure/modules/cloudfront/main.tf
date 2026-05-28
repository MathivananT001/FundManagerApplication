resource "aws_cloudfront_origin_access_identity" "localization" {
  comment = "${var.project_prefix} localization OAI"
}

resource "aws_s3_bucket_policy" "localization" {
  bucket = var.localization_bucket_id

  policy = jsonencode({
    Version = "2012-10-17"
    Statement = [{
      Effect    = "Allow"
      Principal = { AWS = aws_cloudfront_origin_access_identity.localization.iam_arn }
      Action    = "s3:GetObject"
      Resource  = "${var.localization_bucket_arn}/*"
    }]
  })
}

resource "aws_cloudfront_distribution" "localization" {
  enabled             = true
  default_root_object = "localization/en.json"
  comment             = "${var.project_prefix} localization CDN - ${var.environment}"

  origin {
    domain_name = "${var.localization_bucket_id}.s3.amazonaws.com"
    origin_id   = "s3-localization"

    s3_origin_config {
      origin_access_identity = aws_cloudfront_origin_access_identity.localization.cloudfront_access_identity_path
    }
  }

  default_cache_behavior {
    allowed_methods        = ["GET", "HEAD"]
    cached_methods         = ["GET", "HEAD"]
    target_origin_id       = "s3-localization"
    viewer_protocol_policy = "redirect-to-https"

    forwarded_values {
      query_string = false
      cookies { forward = "none" }
    }

    min_ttl     = 0
    default_ttl = 3600
    max_ttl     = 86400
  }

  restrictions {
    geo_restriction { restriction_type = "none" }
  }

  viewer_certificate {
    cloudfront_default_certificate = true
  }

  tags = { Environment = var.environment }
}
