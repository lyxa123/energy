# Use Python 3.12 with Ubuntu base for better PyGame support
FROM python:3.12-slim-bookworm

# Set working directory
WORKDIR /app

# Install system dependencies for PyGame and graphics
RUN apt-get update && \
    apt-get install -y --no-install-recommends \
    libsdl2-2.0-0 \
    libsdl2-image-2.0-0 \
    libsdl2-mixer-2.0-0 \
    libsdl2-ttf-2.0-0 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libxext6 \
    libsm6 \
    libxrender1 \
    libfontconfig1 \
    fontconfig \
    libice6 \
    xvfb \
    x11-utils \
    x11vnc \
    novnc \
    websockify \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

# Create and activate virtual environment
RUN python -m venv /opt/venv
ENV PATH="/opt/venv/bin:$PATH"

# Copy and install requirements
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy project files
COPY . .

# Set environment variables for headless operation
ENV DISPLAY=:99
# ENV SDL_VIDEODRIVER=dummy # This must be commented out to see the GUI
# ENV SDL_AUDIODRIVER=dummy # Uncomment if you want to run in headless mode
ENV PYTHONUNBUFFERED=1

# Copy startup script and make it executable
COPY start.sh .
RUN chmod +x start.sh

# Command to run the application
CMD ["/app/start.sh"]