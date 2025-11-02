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
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Upgrade pip
RUN pip install --upgrade pip

# Install CPU-only PyTorch (required by EasyOCR)
RUN pip install torch==2.3.1+cpu torchvision==0.14.1+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install the rest of Python dependencies
RUN pip install -r requirements.txt

# Copy all backend code into container
COPY . .

# Expose port 8080 for Railway
EXPOSE 8080

# Start Flask app with Gunicorn
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:8080"]
