# ---------------------------------------------------------
# EC2 instance — hosts the Streamlit dashboard
# Free Tier: 750 hrs/month of t2.micro for 12 months
# ---------------------------------------------------------

data "aws_ami" "amazon_linux" {
  most_recent = true
  owners      = ["amazon"]

  filter {
    name   = "name"
    values = ["al2023-ami-*-x86_64"]
  }
}

resource "aws_instance" "dashboard_server" {
  ami                    = data.aws_ami.amazon_linux.id
  instance_type          = var.ec2_instance_type
  key_name               = var.key_pair_name
  vpc_security_group_ids = [aws_security_group.dashboard_sg.id]
  iam_instance_profile   = aws_iam_instance_profile.ec2_profile.name

  # Installs Python + pip on first boot so the instance is ready
  # for you to `git clone` your Streamlit app and run it.
  user_data = <<-EOF
              #!/bin/bash
              dnf update -y
              dnf install -y python3 python3-pip git
              pip3 install streamlit boto3 pandas plotly
              EOF

  tags = {
    Name    = "${var.project_name}-server"
    Project = var.project_name
  }
}
