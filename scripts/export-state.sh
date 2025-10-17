#!/bin/bash

# Export State Script
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

USAGE="Usage: $0 <provider> <stack> [--output-dir <directory>]"

if [ $# -lt 2 ]; then
    print_error "Missing arguments"
    echo $USAGE
    exit 1
fi

PROVIDER=$1
STACK=$2
shift 2

OUTPUT_DIR="./state-backups"

while [[ $# -gt 0 ]]; do
    case $1 in
        --output-dir)
        OUTPUT_DIR=$2
        shift 2
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

export_state() {
    local provider=$1
    local stack=$2
    local output_dir=$3
    
    print_status "Exporting state for $provider ($stack stack)..."
    
    cd $provider
    
    # Check if stack exists
    if ! pulumi stack ls | grep -q "$stack"; then
        print_error "Stack $stack not found in $provider"
        cd ..
        return 1
    fi
    
    # Select stack
    pulumi stack select $stack
    
    # Create output directory
    mkdir -p $output_dir
    
    # Export timestamp
    TIMESTAMP=$(date +%Y%m%d_%H%M%S)
    BACKUP_FILE="$output_dir/${provider}_${stack}_${TIMESTAMP}.json"
    
    # Export stack state
    print_status "Exporting stack state to $BACKUP_FILE"
    pulumi stack export --file $BACKUP_FILE
    
    # Export outputs
    OUTPUTS_FILE="$output_dir/${provider}_${stack}_${TIMESTAMP}_outputs.json"
    print_status "Exporting stack outputs to $OUTPUTS_FILE"
    pulumi stack output --json > $OUTPUTS_FILE
    
    # Create backup info
    INFO_FILE="$output_dir/${provider}_${stack}_${TIMESTAMP}_info.txt"
    cat > $INFO_FILE << EOF
Backup Information:
- Provider: $provider
- Stack: $stack
- Timestamp: $(date)
- Backup File: $(basename $BACKUP_FILE)
- Outputs File: $(basename $OUTPUTS_FILE)
- Pulumi Version: $(pulumi version)
EOF

    cd ..
    
    print_status "State export completed:"
    echo "  - State: $BACKUP_FILE"
    echo "  - Outputs: $OUTPUTS_FILE"
    echo "  - Info: $INFO_FILE"
}

# Validate inputs
if ! validate_provider $PROVIDER; then
    exit 1
fi

if [ ! -d "$PROVIDER" ]; then
    print_error "Provider directory '$PROVIDER' not found"
    exit 1
fi

# Create output directory
mkdir -p $OUTPUT_DIR

# Execute export
export_state $PROVIDER $STACK $OUTPUT_DIR

print_status "✅ State export completed successfully!"