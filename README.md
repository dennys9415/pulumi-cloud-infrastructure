# Pulumi Cloud Infrastructure

![Pulumi](https://img.shields.io/badge/Pulumi-Infrastructure%20as%20Code-blue)
![Multi-Cloud](https://img.shields.io/badge/Multi--Cloud-AWS%2C%20Azure%2C%20GCP-orange)
![Python](https://img.shields.io/badge/Python-3.8%2B-green)
![TypeScript](https://img.shields.io/badge/TypeScript-4.5%2B-blue)

A comprehensive Infrastructure as Code (IaC) repository using Pulumi with Python and TypeScript for multi-cloud infrastructure deployment across AWS, Azure, and Google Cloud Platform.

## 🚀 Features

- **Multi-Cloud Support** - AWS, Azure, GCP with consistent patterns
- **Multi-Language** - Python and TypeScript implementations
- **Production Ready** - Best practices for security, scalability, and reliability
- **Kubernetes Native** - EKS, AKS, GKE cluster deployments
- **Modular Design** - Reusable components across cloud providers
- **CI/CD Integration** - GitHub Actions for automated deployments
- **Security First** - Built-in security best practices and compliance
- **Monitoring Ready** - Integrated logging and monitoring stacks

## 📋 Prerequisites

### Required Tools

- **Pulumi** CLI >= 3.0.0
- **Python** >= 3.8 or **Node.js** >= 16.0.0
- **Cloud Provider CLIs** (AWS CLI, Azure CLI, Google Cloud SDK)
- **Docker** (for containerized applications)

### Cloud Accounts

- AWS Account with appropriate permissions
- Azure Subscription with Contributor role
- Google Cloud Project with Owner permissions

## 🏗️ Architecture

```
┌─────────────────┐ ┌─────────────────┐ ┌─────────────────┐
│       AWS       │ │       Azure     │ │ GCP             │
│                 │ │                 │ │                 │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │
│ │     VPC     │ │ │ │     VNet    │ │ │ │     VPC     │ │
│ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │
│                 │ │                 │ │                 │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │
│ │     EKS     │ │ │ │     AKS     │ │ │ │     GKE     │ │
│ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │
│                 │ │                 │ │                 │
│ ┌─────────────┐ │ │ ┌─────────────┐ │ │ ┌─────────────┐ │
│ │     RDS     │ │ │ │ PostgreSQL  │ │ │ │ Cloud SQL   │ │
│ └─────────────┘ │ │ └─────────────┘ │ │ └─────────────┘ │
└─────────────────┘ └─────────────────┘ └─────────────────┘
    │                       │                       │
    └───────────────────────────────────────────────┘
                            │
                ┌─────────────────────────┐
                │     Multi-Cloud App     │
                │       Deployment        │
                └─────────────────────────┘
```


## 🏁 Quick Start

### 1. Clone the Repository

```bash
git clone https://github.com/your-username/pulumi-cloud-infrastructure.git
cd pulumi-cloud-infrastructure
```

### 2. Setup Environment

```bash
# Install Pulumi and dependencies
./scripts/setup-pulumi.sh

# Configure cloud credentials
# AWS
aws configure
# Azure
az login
# GCP
gcloud auth login
```

### 3. Deploy AWS Infrastructure

```bash
cd aws
pulumi stack init dev
pulumi config set aws:region us-west-2
pulumi up
```

### 4. Deploy Azure Infrastructure

```bash
cd azure
pulumi stack init dev
pulumi config set azure-native:location EastUS
npm install
pulumi up
```

### 5. Deploy Multi-Cloud Application

```bash
cd multi-cloud
pulumi stack init dev
pulumi up
```

## 📁 Project Structure

### Simple Structure

```text
pulumi-cloud-infrastructure/
├── aws/                # AWS infrastructure (Python)
├── azure/              # Azure infrastructure (TypeScript)
├── gcp/                # GCP infrastructure (Python)
├── multi-cloud/        # Cross-cloud deployments
├── kubernetes/         # K8s manifests and operators
├── modules/            # Reusable cloud components
├── scripts/            # Deployment and utility scripts
├── tests/              # Infrastructure tests
└── docs/               # Documentation
```

### Entire Structure

```
pulumi-cloud-infrastructure/
├── .github/
│   └── workflows/
│       ├── pulumi-preview.yml
│       ├── pulumi-deploy.yml
│       └── security-scan.yml
├── aws/                                # AWS infrastructure (Python)
│   ├── __main__.py
│   ├── requirements.txt
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   └── Pulumi.production.yaml
├── azure/                              # Azure infrastructure (TypeScript)
│   ├── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   └── Pulumi.production.yaml
├── gcp/                                # GCP infrastructure (Python)
│   ├── __main__.py
│   ├── requirements.txt
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   └── Pulumi.production.yaml
├── multi-cloud/                        # Cross-cloud deployments
│   ├── __main__.py
│   ├── requirements.txt
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   └── Pulumi.production.yaml
├── kubernetes/                         # K8s manifests and operators
│   ├── index.ts
│   ├── package.json
│   ├── tsconfig.json
│   ├── Pulumi.yaml
│   ├── Pulumi.dev.yaml
│   ├── Pulumi.staging.yaml
│   └── Pulumi.production.yaml
├── modules/                            # Reusable cloud components
│   ├── aws/
│   │   ├── vpc/
│   │   │   ├── __init__.py
│   │   │   └── vpc.py
│   │   ├── eks/
│   │   │   ├── __init__.py
│   │   │   └── cluster.py
│   │   └── rds/
│   │       ├── __init__.py
│   │       └── database.py
│   ├── azure/
│   │   ├── aks/
│   │   │   ├── index.ts
│   │   │   └── cluster.ts
│   │   └── storage/
│   │       ├── index.ts
│   │       └── account.ts
│   └── gcp/
│       ├── gke/
│       │   ├── __init__.py
│       │   └── cluster.py
│       └── cloud-sql/
│           ├── __init__.py
│           └── database.py
├── scripts/                              # Deployment and utility scripts
│   ├── setup-pulumi.sh
│   ├── deploy-stack.sh
│   ├── destroy-stack.sh
│   └── export-state.sh
├── tests/                                # Infrastructure tests
│   ├── test_aws_infrastructure.py
│   ├── test_azure_infrastructure.py
│   └── test_gcp_infrastructure.py
├── docs/                                 # Documentation
│   ├── aws-setup.md
│   ├── azure-setup.md
│   ├── gcp-setup.md
│   └── multi-cloud.md
├── .pulumi/
│   └── templates/
├── .gitignore
├── LICENSE
├── README.md
├── CONTRIBUTING.md
└── pulumi-plugin.json
```

## 🛠️ Cloud Providers

### AWS (Python)

* VPC with public and private subnets

* EKS Kubernetes clusters

* RDS PostgreSQL databases

* S3 buckets for storage

* ALB for load balancing

* CloudWatch for monitoring

### Azure (TypeScript)

* Virtual Network with subnets

* AKS Kubernetes clusters

* PostgreSQL flexible servers

* Storage Accounts and Blob containers

* Application Gateway for load balancing

* Monitor for observability

### GCP (Python)

* VPC networks with subnets

* GKE Kubernetes clusters

* Cloud SQL PostgreSQL instances

* Cloud Storage buckets

* Load Balancers with managed certificates

* Stackdriver monitoring

## 🔧 Modules

### Reusable Components

| Module	                    | Description	                  | Cloud Providers |
|-----------------------------|-------------------------------|-----------------|
| vpc	                        | Virtual network with subnets	| AWS, Azure, GCP |
| eks/aks/gke	                | Managed Kubernetes clusters	  | AWS, Azure, GCP |
| rds/postgresql/cloud-sql	  | Managed databases	            | AWS, Azure, GCP |
| s3/storage/cloud-storage	  | Object storage	              | AWS, Azure, GCP |
---

### Using Modules

```python
# AWS VPC module
from modules.aws.vpc import Vpc

vpc = Vpc(
    name="main-vpc",
    cidr_block="10.0.0.0/16",
    enable_nat_gateway=True
)
```

```typescript
// Azure AKS module
import { AksCluster } from "./modules/azure/aks";

const cluster = new AksCluster("main-cluster", {
    nodeCount: 3,
    vmSize: "Standard_D2s_v3",
});
```

## 🚀 Deployment

### Environment-Based Stacks

```bash
# Development
pulumi stack select dev
pulumi up

# Staging
pulumi stack select staging
pulumi up

# Production
pulumi stack select production
pulumi up
```

### Using Deployment Scripts

```bash
# Deploy specific stack
./scripts/deploy-stack.sh aws dev

# Destroy stack
./scripts/destroy-stack.sh azure staging

# Export state for backup
./scripts/export-state.sh gcp production
```

## 🔒 Security

### Built-in Security Features

* Network Security - Security groups and NSGs

* IAM/RBAC - Least privilege access control

* Encryption - Data encryption at rest and in transit

* Secrets Management - Pulumi config and cloud secrets

* Compliance - CIS benchmarks and security best practices

### Security Configuration

```bash
# Set secrets
pulumi config set --secret databasePassword "secure-password"

# Use cloud secrets
pulumi config set --secret aws:accessKey "AKIA..."
pulumi config set --secret aws:secretKey "secret-key"
```

## 📊 Monitoring & Observability

### Integrated Monitoring

* AWS: CloudWatch alarms and dashboards

* Azure: Monitor alerts and insights

* GCP: Stackdriver monitoring and logging

* Kubernetes: Prometheus and Grafana

### Example Monitoring Setup

```python
# CloudWatch alarms
cloudwatch.MetricAlarm("high-cpu",
    alarm_description="CPU utilization too high",
    metric_name="CPUUtilization",
    threshold=80,
    alarm_actions=[sns_topic.arn]
)
```

## 💰 Cost Optimization

### Cost Estimation

```bash
# Preview costs before deployment
pulumi preview --diff

# View cost breakdown
pulumi stack output costs
```

### Cost Optimization Strategies

* Right-sizing resources

* Auto-scaling configurations

* Spot instances for workloads

* Storage lifecycle policies

## 🧪 Testing

### Infrastructure Tests

```bash
# Run AWS tests
python -m pytest tests/test_aws_infrastructure.py

# Run Azure tests
npm test -- tests/test_azure_infrastructure.ts

# Run validation
pulumi preview --diff
```

### Test Examples

```python
def test_vpc_creation():
    """Test VPC creation with proper CIDR range"""
    vpc = Vpc("test-vpc", cidr_block="10.0.0.0/16")
    assert vpc.cidr_block == "10.0.0.0/16"
    assert vpc.enable_dns_hostnames == True
```

## 🔄 CI/CD Pipeline

### GitHub Actions

* Preview Changes - Plan and validate infrastructure

* Automated Deployment - Deploy to environments

* Security Scanning - Check for vulnerabilities

* Testing - Run infrastructure tests

### Workflow Example

```yaml
name: Deploy AWS Infrastructure
on:
  push:
    branches: [main]
jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: pulumi/actions@v4
        with:
          command: up
          stack-name: aws-dev
```

## 🤝 Contributing

1. Fork the repository

2. Create a feature branch (git checkout -b feature/amazing-feature)

3. Commit your changes (git commit -m 'Add amazing feature')

4. Push to the branch (git push origin feature/amazing-feature)

5. Open a Pull Request

Please read CONTRIBUTING.md for details.

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🙏 Acknowledgments

* Pulumi Team for excellent IaC tooling

* Cloud Providers for comprehensive APIs

* Open Source Community for best practices

## 📞 Support

* Issues: GitHub Issues

* Discussions: GitHub Discussions

* Documentation: AWS, Azure, GCP