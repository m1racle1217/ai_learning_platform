#!/bin/bash
cd "$(dirname "$0")" || exit 1
nohup python3 scripts/start_app.py >/tmp/ai_learning_platform.log 2>&1 &
