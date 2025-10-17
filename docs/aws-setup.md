# AWS Infrastructure Setup

## Prerequisites

- AWS Account with appropriate permissions
- AWS CLI configured
- Pulumi CLI installed

## Configuration

### AWS Credentials

```bash
aws configure
# or set environment variables
export AWS_ACCESS_KEY_ID="your-access-key"
export AWS_SECRET_ACCESS_KEY="your-secret-key"
```
## Pulumi Configuration

```bash
cd aws
pulumi stack init dev

# Configure required settings
pulumi config set aws:region us-west-2
pulumi config set vpcCidrBlock 10.0.0.0/16

# Set secrets
pulumi config set --secret databasePassword "secure-password"
```

## Deployment

```bash
# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up

# Destroy infrastructure
pulumi destroy
```

## Architecture

* VPC with public and private subnets across 2 AZs

* EKS Kubernetes cluster with managed node groups

* RDS PostgreSQL database with backup enabled

* S3 bucket for application storage

* Security groups and IAM roles with least privilege

## Cost Estimation

* Development stack: ~$50-100/month

* Production stack: ~$300-500/month

## Troubleshooting

### Common Issues

1. Insufficient permissions: Ensure IAM user has required permissions

2. Resource limits: Check AWS service limits in your account

3. Network conflicts: Ensure CIDR blocks don't overlap with existing networks