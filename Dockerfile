# Use Python slim image as the base
FROM python:3.12-slim

# Install FFmpeg and system dependencies
RUN apt-get update && apt-get install -y ffmpeg && apt-get clean

# Set the working directory
WORKDIR /app

# Copy project files
COPY . /app

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Run the bot
CMD ["python", "main.py"]
