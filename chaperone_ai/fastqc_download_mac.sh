#!/bin/bash

# Define the FastQC download URL
fastqc_url="https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.9.zip"

# Get the directory of the script
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$script_directory"

# Download FastQC using curl
curl -O "$fastqc_url"

# Unzip the downloaded file
unzip fastqc_v0.11.9.zip

# Make the FastQC script executable
chmod +x FastQC/fastqc

# Print a message indicating the completion
echo "FastQC has been downloaded to and installed in the script directory."

