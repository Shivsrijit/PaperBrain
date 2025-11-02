# Use a slim Python image
FROM python:3.10-slim

# Set working directory inside the container
WORKDIR /app

# Copy only requirements first (for caching)
COPY requirements.txt .

# Install system dependencies for OpenCV, EasyOCR, tesseract
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    libgomp1 \
    libgl1-mesa-glx \
    libglib2.0-0 \
    libgl1 \
    libglx0 \
    libegl1 \
    libgles2 \
    libgbm1 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Set OpenCV to use headless mode (no GUI dependencies)
ENV OPENCV_VIDEOIO_PRIORITY_MSMF=0
ENV QT_QPA_PLATFORM=offscreen

# Upgrade pip
RUN pip install --upgrade pip

# Install opencv-python-headless instead of opencv-python (if in requirements.txt)
# This version doesn't require GUI libraries
RUN pip install opencv-python-headless==4.8.1.78

# Install CPU-only PyTorch (required by EasyOCR)
RUN pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu

# Install the rest of Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code into container
COPY . .

# Expose port 8080 for Railway
EXPOSE 8080

# Start Flask app with Gunicorn
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:8080", "--workers", "2", "--timeout", "120"]
