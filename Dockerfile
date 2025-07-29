# Use Python 3.12 as base
FROM python:3.12-slim-bullseye

# Set working directory
WORKDIR /app

# Install system dependencies for PyGame and graphics
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    python3-pygame \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    x11-xserver-utils \
    xvfb \
    git && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set display for PyGame
ENV DISPLAY=:0

# Command to run the application
CMD ["xvfb-run", "python", "pyPSA_db.py"] 