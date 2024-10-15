#!/bin/bash

# Prompt for the rune value
echo "Please enter the rune value:"
read rune_value

# Store the rune value in an environment variable or a file
export RUNE_VALUE=$rune_value
echo "Rune value set to: $RUNE_VALUE"

# Optionally, save to a file if other scripts need to read it
echo $RUNE_VALUE > /app/rune_value.txt

# Start cron service
cron

# Keep the container running
exec "$@"
