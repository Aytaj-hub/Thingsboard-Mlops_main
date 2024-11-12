FROM thingsboard/trendz:1.11.0

# Install Python and pip
RUN apt-get update && apt-get install -y python3 python3-pip

# Install mlflow and other required Python packages
RUN pip3 install mlflow scikit-learn pandas numpy

# Clean up to reduce image size
RUN apt-get clean && rm -rf /var/lib/apt/lists/*

# (Optional) Expose port if needed
EXPOSE 8888
