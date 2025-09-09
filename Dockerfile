FROM python:3.10-slim

# Set working directory
WORKDIR /code

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the project
COPY . .

# Hugging Face Spaces requires the app to listen on port 7860
ENV PORT=7860

# Run Django using gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:7860", "my_backend.wsgi:application"]
