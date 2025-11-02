# Use a slim Python image
FROM python:3.10-slim

# Set working directory
WORKDIR /app

# Copy requirements first (for caching)
COPY requirements.txt .

# Install system dependencies for OpenCV and EasyOCR
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libglib2.0-0 \
    libsm6 \
    libxrender1 \
    libxext6 \
    tesseract-ocr \
    && rm -rf /var/lib/apt/lists/*

# Install CPU-only PyTorch first (required by EasyOCR)
RUN pip install --upgrade pip
RUN pip install torch==2.9.0+cpu torchvision==0.24.0+cpu -f https://download.pytorch.org/whl/cpu/torch_stable.html

# Install the rest of Python dependencies
RUN pip install -r requirements.txt

# Copy backend code
COPY . .

# Expose port for Railway
EXPOSE 8080

# Start the Flask server using gunicorn
CMD ["gunicorn", "server:app", "--bind", "0.0.0.0:8080"]
