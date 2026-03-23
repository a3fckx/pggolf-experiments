#!/bin/bash
set -euo pipefail

ssh -t mi300x 'tmux attach -t pg-monitor'
