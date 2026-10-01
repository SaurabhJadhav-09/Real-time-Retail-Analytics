output "s3_bucket_name" {
  value = aws_s3_bucket.raw_data.bucket
}

output "dynamodb_table_name" {
  value = aws_dynamodb_table.live_orders.name
}

output "ec2_public_ip" {
  value = aws_instance.dashboard_server.public_ip
}

output "dashboard_url" {
  value = "http://${aws_instance.dashboard_server.public_ip}:8501"
}