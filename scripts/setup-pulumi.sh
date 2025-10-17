#!/bin/bash

# Pulumi Cloud Infrastructure Setup Script
set -e

echo "🚀 Setting up Pulumi Cloud Infrastructure..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Print colored output
print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check prerequisites
check_command() {
    if ! command -v $1 &> /dev/null; then
        print_error "$1 is not installed. Please install it first."
        exit 1
    fi
}

print_status "Checking prerequisites..."
check_command python3
check_command node
check_command npm

# Check cloud CLIs
if ! command -v aws &> /dev/null; then
    print_warning "AWS CLI is not installed. AWS deployments will fail."
fi

if ! command -v az &> /dev/null; then
    print_warning "Azure CLI is not installed. Azure deployments will fail."
fi

if ! command -v gcloud &> /dev/null; then
    print_warning "Google Cloud CLI is not installed. GCP deployments will fail."
fi

# Install Pulumi
if ! command -v pulumi &> /dev/null; then
    print_status "Installing Pulumi..."
    curl -fsSL https://get.pulumi.com | sh
    export PATH=$PATH:$HOME/.pulumi/bin
    print_status "Pulumi installed successfully"
else
    print_status "Pulumi is already installed"
fi

# Setup Python environments
print_status "Setting up Python environments..."
for dir in aws gcp multi-cloud; do
    if [ -d "$dir" ]; then
        print_status "Setting up $dir..."
        cd $dir
        if [ ! -d ".venv" ]; then
            python3 -m venv .venv
        fi
        source .venv/bin/activate
        pip install --upgrade pip
        pip install -r requirements.txt
        deactivate
        cd ..
        print_status "$dir setup completed"
    fi
done

# Setup TypeScript environments
print_status "Setting up TypeScript environments..."
for dir in azure kubernetes; do
    if [ -d "$dir" ]; then
        print_status "Setting up $dir..."
        cd $dir
        npm install
        cd ..
        print_status "$dir setup completed"
    fi
done

# Create configuration templates
print_status "Creating configuration templates..."
mkdir -p .pulumi/templates

# Create AWS template
cat > .pulumi/templates/aws-config.yaml << EOF
# AWS Configuration Template
# Copy to aws/Pulumi.<stack>.yaml and update values

config:
  aws:region: us-west-2
  aws-infrastructure:vpcCidrBlock: 10.0.0.0/16
  aws-infrastructure:databaseInstanceClass: db.t3.micro
  aws-infrastructure:minNodes: 1
  aws-infrastructure:maxNodes: 3
  aws-infrastructure:allocatedStorage: 20
EOF

# Create Azure template
cat > .pulumi/templates/azure-config.yaml << EOF
# Azure Configuration Template
# Copy to azure/Pulumi.<stack>.yaml and update values

config:
  azure-native:location: EastUS
  azure-infrastructure:nodeCount: 3
  azure-infrastructure:vmSize: Standard_D2s_v3
  azure-infrastructure:dbAdmin: psqladmin
EOF

# Create GCP template
cat > .pulumi/templates/gcp-config.yaml << EOF
# GCP Configuration Template
# Copy to gcp/Pulumi.<stack>.yaml and update values

config:
  gcp:project: your-project-id
  gcp:region: us-central1
  gcp-infrastructure:minNodes: 1
  gcp-infrastructure:maxNodes: 3
  gcp-infrastructure:machineType: e2-medium
  gcp-infrastructure:dbTier: db-f1-micro
  gcp-infrastructure:diskSize: 20
EOF

print_status "✅ Setup completed successfully!"
echo ""
print_status "Next steps:"
echo "1. Configure cloud credentials:"
echo "   aws configure"
echo "   az login"
echo "   gcloud auth login"
echo "2. Initialize stacks:"
echo "   cd aws && pulumi stack init dev"
echo "   cd ../azure && pulumi stack init dev"
echo "   cd ../gcp && pulumi stack init dev"
echo "3. Set configuration values in respective Pulumi.<stack>.yaml files"
echo "4. Deploy: ./scripts/deploy-stack.sh <provider> <stack>"