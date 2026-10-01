# ---------------------------------------------------------
# S3 bucket — stores the raw Kaggle CSV + any exported data
# Free Tier: 5 GB standard storage, 20,000 GET / 2,000 PUT per month
# ---------------------------------------------------------

resource "aws_s3_bucket" "raw_data" {
  bucket = var.s3_bucket_name

  tags = {
    Project = var.project_name
    Purpose = "raw-retail-data"
  }
}

resource "aws_s3_bucket_public_access_block" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id

  block_public_acls       = true
  block_public_policy     = true
  ignore_public_acls      = true
  restrict_public_buckets = true
}

resource "aws_s3_bucket_versioning" "raw_data" {
  bucket = aws_s3_bucket.raw_data.id
  versioning_configuration {
    status = "Disabled" # keep disabled to save storage on free tier
  }
}
