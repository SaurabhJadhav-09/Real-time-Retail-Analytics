# Real-Time Analytics Dashboard — Infrastructure as Code (Step 3)

B.Sc. Cloud Computing Field Project — Sanket Sanjay Jadhav
Provisions AWS free-tier resources for a simulated real-time retail analytics dashboard, using Terraform.

## What this creates
- **S3 bucket** — stores the raw Kaggle dataset
- **DynamoDB table** — stores the simulated "live" order feed
- **IAM role** — lets EC2 read/write S3 & DynamoDB without hardcoded keys
- **Security Group** — opens only SSH (22) and Streamlit (8501) to your IP
- **EC2 instance (t2.micro)** — hosts the Streamlit dashboard, free tier eligible

## Before you run this

1. **Install Terraform**: https://developer.hashicorp.com/terraform/install
2. **Install & configure AWS CLI** with your student account credentials:
   ```
   aws configure
   ```
3. **Create an EC2 key pair** in the AWS Console (EC2 → Key Pairs → Create), download the `.pem` file, and set `key_pair_name` in `variables.tf` to match it.
4. **Set your own IP** in `variables.tf` → `my_ip` (find it at whatismyip.com, format `x.x.x.x/32`) — do NOT leave it open to `0.0.0.0/0`.
5. **Change `s3_bucket_name`** in `variables.tf` to something globally unique (S3 bucket names are unique across all AWS accounts).

## Deploy

```bash
cd terraform
terraform init
terraform plan      # review what will be created
terraform apply      # type 'yes' to confirm
```

Take a screenshot of the `terraform apply` output — this is one of your required deliverables.

## After deploy: screenshots to capture for submission

- [ ] `terraform apply` successful output (shows resources created)
- [ ] AWS Console → S3 → bucket created
- [ ] AWS Console → DynamoDB → table created
- [ ] AWS Console → EC2 → instance running, with public IP visible
- [ ] AWS Console → IAM → role and policy attached to the instance
- [ ] Terminal: SSH into the instance and `python3 --version` / `streamlit --version` showing they installed via user_data

## Destroy (important — avoid using up your free-tier credits)

When you're done demoing for the day:
```bash
terraform destroy
```
Re-run `terraform apply` next time you need it live. This keeps your 6-month student credit lasting the whole semester.

## Next steps (Application Deployment stage)
1. SSH into the EC2 instance: `ssh -i your-key.pem ec2-user@<ec2_public_ip>`
2. Clone your GitHub repo containing the `app/` folder (Streamlit code + data simulation script)
3. Run: `streamlit run app/dashboard.py --server.port 8501 --server.address 0.0.0.0`
4. Visit `http://<ec2_public_ip>:8501` in your browser

## Repository structure
```
.
├── README.md
├── terraform/
│   ├── provider.tf
│   ├── variables.tf
│   ├── s3.tf
│   ├── dynamodb.tf
│   ├── iam.tf
│   ├── security_group.tf
│   ├── ec2.tf
│   └── outputs.tf
└── app/
    ├── simulate_orders.py   # replays Kaggle CSV rows into DynamoDB
    └── dashboard.py          # Streamlit dashboard
```
