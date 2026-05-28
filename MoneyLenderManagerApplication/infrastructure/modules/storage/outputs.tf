output "payment_proofs_bucket_arn" {
  value = aws_s3_bucket.payment_proofs.arn
}

output "payment_proofs_bucket_id" {
  value = aws_s3_bucket.payment_proofs.id
}

output "reports_bucket_arn" {
  value = aws_s3_bucket.reports.arn
}

output "reports_bucket_id" {
  value = aws_s3_bucket.reports.id
}

output "archives_bucket_arn" {
  value = aws_s3_bucket.archives.arn
}

output "archives_bucket_id" {
  value = aws_s3_bucket.archives.id
}

output "localization_bucket_arn" {
  value = aws_s3_bucket.localization.arn
}

output "localization_bucket_id" {
  value = aws_s3_bucket.localization.id
}
