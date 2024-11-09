# Use the official Jenkins LTS image as the base
FROM jenkins/jenkins:lts

# Switch to root user to install packages
USER root

# Install system dependencies and Python packages
RUN apt-get update && apt-get install -y \
    python3 \
    python3-pip \
    python3-apt \
    python3-distutils \
    rsync \
    build-essential \
    libpq-dev \
    cmake \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip with the --break-system-packages flag
RUN pip3 install --upgrade pip --break-system-packages

# Install Ansible using pip with the --break-system-packages flag
RUN pip3 install -U ansible --break-system-packages

# Optionally, install other Python packages if needed
# RUN pip3 install <your-other-packages> --break-system-packages

# Switch back to the jenkins user
USER jenkins