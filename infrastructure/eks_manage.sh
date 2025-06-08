#!/bin/bash

# EKS Cluster Manager
# Usage examples:
#   ./eks_manager.sh resize 2
#   ./eks_manager.sh info

# Configuration
CLUSTER_NAME="erik-chatapp-cluster"
NODEGROUP_NAME="erik-chatapp-cluster-node-group"
REGION="ap-south-1"

# Check for AWS CLI
command -v aws >/dev/null 2>&1 || {
    echo >&2 "aws CLI is not installed."
    exit 1
}

command -v kubectl >/dev/null 2>&1 || {
    echo >&2 "kubectl is not installed."
    exit 1
}

function resize_nodegroup() {
    local desired_size="$1"

    if ! [[ "$desired_size" =~ ^[0-9]+$ ]]; then
        echo "Error: desired_size must be a non-negative integer."
        exit 1
    fi

    local current_nodes
    current_nodes=$(kubectl get nodes -l "eks.amazonaws.com/nodegroup=$NODEGROUP_NAME" --no-headers 2>/dev/null | wc -l)

    if [ "$current_nodes" -eq "$desired_size" ]; then
        echo "No resize needed. Node pool '$POOL_NAME' already has $current_nodes node(s)."
        exit 1
    fi

    echo "Resizing EKS Node Group '$NODEGROUP_NAME' to $desired_size node(s)..."

    aws eks update-nodegroup-config \
        --cluster-name "$CLUSTER_NAME" \
        --nodegroup-name "$NODEGROUP_NAME" \
        --scaling-config "minSize=$desired_size,maxSize=3,desiredSize=$desired_size" \
        --region "$REGION"

    echo "Resize request sent."
}

function usage() {
    echo "EKS Cluster Manager"
    echo
    echo "Usage: $0 <command> [args]"
    echo
    echo "Commands:"
    echo "  resize <desired_size>   Resize the node group to desired_size"
    echo
    exit 1
}

# Main
case "$1" in
resize)
    [ -z "$2" ] && usage
    resize_nodegroup "$2"
    ;;
*)
    usage
    ;;
esac
