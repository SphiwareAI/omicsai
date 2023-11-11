#!/bin/bash

# Define the FastQC download URL
fastqc_url="https://www.bioinformatics.babraham.ac.uk/projects/fastqc/fastqc_v0.11.9.zip"

# Define the target directory
# Get the directory of the script
script_directory="$( cd "$( dirname "${BASH_SOURCE[0]}" )" &> /dev/null && pwd )"

# Change to the script directory
cd "$script_directory"


# Create the target directory if it doesn't exist
#mkdir -p "$target_directory"

# Change to the target directory
#cd "$target_directory"

# Download FastQC using wget
wget "$fastqc_url"

# Unzip the downloaded file
unzip fastqc_v0.11.9.zip

# Make the FastQC script executable
chmod +x FastQC/fastqc

# Print a message indicating the completion
echo "FastQC has been downloaded and is ready to use."

