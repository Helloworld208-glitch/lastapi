FROM python:3.9-slim

WORKDIR /app

# Copy and install your Python dependencies
COPY requirements.txt /app/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your application code into the container
COPY . /app

# Start your Python application
CMD ["python", "main.py"]