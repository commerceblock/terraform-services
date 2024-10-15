#!/bin/bash

# Check if the cron service is running
if pgrep cron > /dev/null; then
  exit 0
else
  exit 1
fi
