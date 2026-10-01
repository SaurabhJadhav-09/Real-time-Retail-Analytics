# ---------------------------------------------------------
# DynamoDB table — stores the "live" simulated order feed
# Free Tier: Always free up to 25 GB storage + 25 RCU/WCU
# On-demand billing keeps cost at $0 for this project's scale
# ---------------------------------------------------------

resource "aws_dynamodb_table" "live_orders" {
  name         = var.dynamodb_table_name
  billing_mode = "PAY_PER_REQUEST" # no idle cost, ideal for free-tier student use

  hash_key = "order_id"

  attribute {
    name = "order_id"
    type = "S"
  }

  tags = {
    Project = var.project_name
    Purpose = "live-order-simulation"
  }
}
