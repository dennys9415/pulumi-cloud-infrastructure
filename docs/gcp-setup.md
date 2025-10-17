# GCP Infrastructure Setup

## Prerequisites

- Google Cloud Project with Owner permissions
- Google Cloud SDK installed
- Pulumi CLI installed

## Configuration

### GCP Credentials

```bash
gcloud auth login
gcloud config set project your-project-id
```

## Pulumi Configuration

```bash
cd gcp
pulumi stack init dev

# Configure required settings
pulumi config set gcp:project your-project-id
pulumi config set gcp:region us-central1

# Set secrets
pulumi config set --secret dbPassword "secure-password"
```

## Deployment

```bash
# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up
```

## Architecture

* VPC network with subnets

* GKE cluster with node pools

* Cloud SQL PostgreSQL instance

* Cloud Storage bucket

* IAM roles and service accounts

## Cost Estimation

* Development stack: ~$70-120/month

* Production stack: ~$350-550/month