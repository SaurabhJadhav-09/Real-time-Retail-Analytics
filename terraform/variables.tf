variable "aws_region" {
  description = "AWS region to deploy resources in"
  type        = string
  default     = "ap-south-1" # Mumbai region — lowest latency from India
}

variable "project_name" {
  description = "Prefix used for naming all resources"
  type        = string
  default     = "retail-analytics-dashboard"
}

variable "s3_bucket_name" {
  description = "Globally unique S3 bucket name for raw retail data. Must be changed to something unique."
  type        = string
  default     = "retail-analytics-raw-data-sanket-jadhav" # CHANGE THIS to a unique name
}

variable "dynamodb_table_name" {
  description = "DynamoDB table name for live/processed order records"
  type        = string
  default     = "retail_live_orders"
}

variable "ec2_instance_type" {
  description = "EC2 instance type (Free Tier eligible)"
  type        = string
  default     = "t3.micro"
}

variable "my_ip" {
  description = "Your IP address in CIDR form, used to restrict SSH/Streamlit access (e.g. 103.21.45.10/32). Find yours at whatismyip.com"
  type        = string
  default     = "0.0.0.0/0" # WARNING: open to all — replace with your IP before applying
}

variable "key_pair_name" {
  description = "Name of an existing EC2 key pair (for SSH access). Create one in the AWS Console first."
  type        = string
  default     = "retail-dashboard-key"
}
