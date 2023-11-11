#!/bin/bash

# Check if the system is Mac or Linux
if [[ "$OSTYPE" == "darwin"* ]]; then
    # macOS
    brew install prodigal
elif [[ "$OSTYPE" == "linux-gnu"* ]]; then
    # Linux (assuming Ubuntu, you may need adjustments for other distributions)
    sudo apt-get update
    sudo apt-get install prodigal
else
    echo "Unsupported operating system"
    exit 1
fi

# Verify the installation
prodigal -v

