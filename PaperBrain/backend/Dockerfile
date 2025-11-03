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

# Install opencv-python-headless instead of opencv-python
RUN pip install opencv-python-headless==4.8.1.78

# Install CPU-only PyTorch (required by EasyOCR)
RUN pip install torch==2.3.1 torchvision==0.18.1 --index-url https://download.pytorch.org/whl/cpu

# Install the rest of Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy all backend code into container (INCLUDING agents folder with Python code)
COPY . .

# Only remove and symlink the uploads directory
RUN rm -rf /app/uploads 2>/dev/null || true && \
    ln -sfn /persistent_data/uploads /app/uploads

# Create all agent data directories (no symlinks - simpler approach)
RUN mkdir -p /app/agents/evaluator/inputs/related_docs \
    /app/agents/evaluator/results/visualizations \
    /app/agents/evaluator/temp \
    /app/agents/preprocessor/aligned_outputs \
    /app/agents/preprocessor/answer_scripts \
    /app/agents/preprocessor/question_paper_templates \
    /app/agents/region_selector/agent1_output \
    /app/agents/region_selector/evaluation_results \
    /app/agents/text_recognition/debug_crops \
    /app/agents/text_recognition/Outputs

# Create startup script
RUN echo '#!/bin/bash\n\
# Ensure uploads directory exists in persistent storage\n\
mkdir -p /persistent_data/uploads\n\
\n\
# Start gunicorn\n\
exec gunicorn server:app --bind 0.0.0.0:8080 --workers 2 --timeout 120\n\
' > /app/start.sh && chmod +x /app/start.sh

# Expose port 8080 for Railway
EXPOSE 8080

# Use startup script
CMD ["/app/start.sh"]
