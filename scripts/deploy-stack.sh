#!/bin/bash

# Deploy Stack Script
set -e

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

print_status() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

USAGE="Usage: $0 <provider> <stack> [--refresh] [--target] [--skip-preview]"

if [ $# -lt 2 ]; then
    print_error "Missing arguments"
    echo $USAGE
    exit 1
fi

PROVIDER=$1
STACK=$2
shift 2

EXTRA_ARGS=""
SKIP_PREVIEW=false

while [[ $# -gt 0 ]]; do
    case $1 in
        --refresh)
        EXTRA_ARGS="$EXTRA_ARGS --refresh"
        shift
        ;;
        --target)
        EXTRA_ARGS="$EXTRA_ARGS --target $2"
        shift 2
        ;;
        --skip-preview)
        SKIP_PREVIEW=true
        shift
        ;;
        *)
        print_error "Unknown option: $1"
        echo $USAGE
        exit 1
        ;;
    esac
done

validate_provider() {
    case $1 in
        aws|azure|gcp|multi-cloud|kubernetes)
            return 0
            ;;
        *)
            print_error "Unknown provider: $1"
            echo "Available providers: aws, azure, gcp, multi-cloud, kubernetes"
            return 1
            ;;
    esac
}

validate_stack() {
    case $1 in
        dev|staging|production)
            return 0
            ;;
        *)
            print_warning "Non-standard stack: $1"
            return 0
            ;;
    esac
}

deploy_stack() {
    local provider=$1
    local stack=$2
    
    print_status "Deploying $provider infrastructure ($stack stack)..."
    
    cd $provider
    
    # Install dependencies
    if [ -f "requirements.txt" ]; then
        print_status "Installing Python dependencies..."
        source .venv/bin/activate
        pip install -r requirements.txt
    elif [ -f "package.json" ]; then
        print_status "Installing Node.js dependencies..."
        npm install
    fi
    
    # Select or init stack
    if pulumi stack ls | grep -q "$stack"; then
        print_status "Selecting existing stack: $stack"
        pulumi stack select $stack
    else
        print_status "Creating new stack: $stack"
        pulumi stack init $stack
    fi
    
    # Refresh state
    print_status "Refreshing stack state..."
    pulumi refresh --yes
    
    # Preview changes
    if [ "$SKIP_PREVIEW" = false ]; then
        print_status "Previewing changes..."
        pulumi preview --diff
    fi
    
    # Deploy
    print_status "Deploying infrastructure..."
    pulumi up --yes $EXTRA_ARGS
    
    cd ..
}

# Validate inputs
if ! validate_provider $PROVIDER; then
    exit 1
fi

if ! validate_stack $STACK; then
    print_warning "Continuing with non-standard stack: $STACK"
fi

if [ ! -d "$PROVIDER" ]; then
    print_error "Provider directory '$PROVIDER' not found"
    exit 1
fi

# Execute deployment
deploy_stack $PROVIDER $STACK

print_status "✅ Deployment completed successfully!"