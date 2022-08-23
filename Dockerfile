FROM python:3.9

# Maintainer info
LABEL maintainer="philiprj2@gmail.com"

# Make working directories
WORKDIR /api

# Upgrade pip with no cache
RUN pip install --no-cache-dir -U pip

# Copy application requirements file to the created working directory
COPY requirements.txt requirements.txt

# Install application dependencies from the requirements file
RUN pip install -r requirements.txt

# Copy API scripts
COPY  scripts/ scripts/

# Copy models from model registry
COPY models/ models/

# Copy setup to install helper library
COPY setup.py setup.py

# Helper library in src
COPY src/ src/

# Install the src package and remove the src directory
RUN pip install --no-cache-dir . && rm -r src

# Run the python application
CMD ["python", "scripts/server.py"]
