# Use Python base image
FROM python:3.9

# Set working directory inside container
WORKDIR /app

# Copy all project files
COPY . .

# Install dependencies
RUN pip install --no-cache-dir -r requirement.txt

# Expose port 5000
EXPOSE 5000

# Start Flask app using Gunicorn
CMD ["gunicorn", "-b", "0.0.0.0:5000", "app:app"]

