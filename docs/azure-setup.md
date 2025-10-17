
# Azure Infrastructure Setup

## Prerequisites

- Azure Subscription with Contributor role
- Azure CLI installed and configured
- Pulumi CLI installed

## Configuration

### Azure Credentials

```bash
az login
az account set --subscription "your-subscription-id"
```

## Pulumi Configuration

```bash
cd azure
pulumi stack init dev

# Configure required settings
pulumi config set azure-native:location EastUS
pulumi config set nodeCount 3

# Set secrets
pulumi config set --secret dbPassword "secure-password"
```

## Deployment

```bash
# Install dependencies
npm install

# Preview changes
pulumi preview

# Deploy infrastructure
pulumi up
```

## Architecture

* Resource Group for resource organization

* AKS Kubernetes cluster with auto-scaling

* PostgreSQL flexible server

* Storage account with blob container

* Virtual Network with subnets

## Cost Estimation

* Development stack: ~$100-200/month

* Production stack: ~$400-600/month