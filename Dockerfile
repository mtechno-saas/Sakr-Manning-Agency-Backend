# 1. Base Image: Every Dockerfile MUST start with a FROM instruction.
# We start with a lightweight Python 3.10 image.
FROM python:3.10-slim

# 2. Set Environment Variables for best practices
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV OLLAMA_HOST=0.0.0.0

# 3. Set the Working Directory inside the container
WORKDIR /app

# 4. Install System Dependencies needed for our Python packages and Ollama
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 5. Install the Ollama executable
RUN curl -L https://ollama.com/download/ollama-linux-amd64 -o /usr/bin/ollama && chmod +x /usr/bin/ollama

# 6. Copy and Install Python libraries from requirements.txt
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 7. Copy your entire project's code into the container
COPY . /app/

# 8. Create directories for persistent data (though Hugging Face may not persist them )
RUN mkdir -p /root/.ollama
RUN mkdir -p /app/staticfiles
RUN mkdir -p /app/mediafiles

# 9. Expose the ports for Django and Ollama (for documentation and linking)
EXPOSE 8000
EXPOSE 11434

# 10. Create the startup script that will run everything
RUN echo '#!/bin/bash' > /app/start.sh && \
    echo 'set -e' >> /app/start.sh && \
    echo 'ollama serve &' >> /app/start.sh && \
    echo 'sleep 5' >> /app/start.sh && \
    echo 'ollama pull phi3:3.8b-mini-4k-instruct-q4_0 &' >> /app/start.sh && \
    echo 'python manage.py migrate' >> /app/start.sh && \
    echo 'gunicorn saker.wsgi:application --bind 0.0.0.0:8000' >> /app/start.sh && \
    chmod +x /app/start.sh

# 11. Set the startup script as the main command for the container
CMD ["/app/start.sh"]
