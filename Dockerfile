FROM python:3.10

# Install system dependencies including CMake
RUN apt-get update && apt-get install -y \
    cmake \
    libpq-dev \
    && rm -rf /var/lib/apt/lists/*

# Set the working directory inside the container
WORKDIR /app

# Install dependencies
COPY requirements.txt /app/
RUN pip install --upgrade pip  # Upgrade pip
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container at /app
COPY . /app/

# Expose port 8000
EXPOSE 8000

# Set environment variables for Django settings
ENV PYTHONUNBUFFERED 1

# Run Django's development server
CMD ["python", "manage.py", "runserver", "0.0.0.0:8000"]