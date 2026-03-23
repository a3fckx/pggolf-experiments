#!/bin/bash
set -euo pipefail

mkdir -p "$(dirname "$0")/plots-vm"
scp -r mi300x:~/experiments/plots/. "$(dirname "$0")/plots-vm/"
echo "Fetched plots into $(dirname "$0")/plots-vm/"
