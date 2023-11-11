#!/bin/bash

# Download Velvet
wget https://www.ebi.ac.uk/~zerbino/velvet/velvet_1.2.10.tgz

# Extract the downloaded tarball
tar -zxvf velvet_1.2.10.tgz

# Navigate into the Velvet directory
cd velvet_1.2.10

# Build Velvet
make

# Optionally, you can move the Velvet binaries to a directory in your PATH
# For example, moving to /usr/local/bin/
sudo mv velvetg velveth /usr/local/bin/

# Clean up the downloaded files
cd ..
rm -rf velvet_1.2.10.tgz velvet_1.2.10

