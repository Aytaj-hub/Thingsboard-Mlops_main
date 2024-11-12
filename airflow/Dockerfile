FROM apache/airflow:2.6.3

USER root

# Switch to the airflow user for package installation
USER airflow

# Upgrade pip and install additional Python packages
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir \
        pandas \
        numpy \
        mysql-connector-python


