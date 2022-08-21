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

# Copy files
COPY  scripts/ scripts/

COPY models/ models/

COPY setup.py setup.py

COPY src/ src/

# Install the src package
RUN pip install --no-cache-dir . && rm -r src

# Run the python application
CMD ["python", "scripts/server.py"]
