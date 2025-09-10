# 1. Base Image: Start with an official Python slim image.
# This provides a lightweight environment with Python pre-installed.
FROM python:3.10-slim

# 2. Set Environment Variables:
# These are best practices for running Python in Docker.
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

# 3. Set Working Directory:
# This is where your application's code will live inside the container.
WORKDIR /django_test

# 4. Install System Dependencies (if any):
# This step is often needed for libraries that have C extensions, like psycopg2 for PostgreSQL.
# Even if using SQLite locally, it's good practice to include for future-proofing.
RUN apt-get update && apt-get install -y \
    build-essential \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# 5. Install Python Dependencies:
# First, copy only the requirements file to leverage Docker's layer caching.
# This step will only re-run if requirements.txt changes.
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# 6. Copy Project Code:
# Copy the rest of your application's code into the working directory.
COPY . /django_test/

# 7. Expose Port:
# Tell Docker that the container will listen on port 8000 at runtime.
# This does not actually open the port; it's for documentation and linking.
EXPOSE 8000

# 8. Set Default Command (for development):
# This is the command that will run if you start the container without any other instructions.
# It runs the Django development server, which is great for local testing.
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]
