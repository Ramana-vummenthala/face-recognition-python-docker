# # Use a more specific base image that includes required libraries
# FROM python:3.9-buster

# # Install system dependencies
# RUN apt-get update && apt-get install -y \
#     build-essential \
#     cmake \
#     pkg-config \
#     libx11-dev \
#     libatlas-base-dev \
#     libgtk-3-dev \
#     libboost-python-dev \
#     python3-dev \
#     && rm -rf /var/lib/apt/lists/*

# # Set working directory
# WORKDIR /app

# # Copy requirements first to leverage Docker cache
# COPY requirements.txt .

# # Install Python dependencies with verbose output and pip upgrade
# RUN python -m pip install --upgrade pip && \
#     pip install --no-cache-dir -r requirements.txt --verbose

# # Copy the application code
# COPY app.py .

# # Expose port
# EXPOSE 5000

# # Add healthcheck
# HEALTHCHECK --interval=30s --timeout=30s --start-period=5s --retries=3 \
#     CMD curl -f http://localhost:5000/ || exit 1

# # Run the application
# CMD ["python", "app.py"]


FROM python:3.9-buster

# Install system dependencies
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    pkg-config \
    libx11-dev \
    libatlas-base-dev \
    libgtk-3-dev \
    libboost-python-dev \
    python3-dev \
    && rm -rf /var/lib/apt/lists/*

# Set working directory
WORKDIR /app

# Copy requirements first to leverage Docker cache
COPY requirements.txt .

# Install Python dependencies
RUN python -m pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Don't copy app.py here - it will be mounted as a volume