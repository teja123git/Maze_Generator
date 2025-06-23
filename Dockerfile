# Stage 1: Use an official, slim Python image as our base.
# "slim" versions are smaller, which is good for deployment.
FROM python:3.11-slim

# Set the working directory inside the container to /app.
# All subsequent commands will run from this directory.
WORKDIR /app

# Copy only the requirements.txt file first. This is a Docker optimization.
# If this file doesn't change, Docker can use a cached layer, speeding up future builds.
COPY requirements.txt .

# Install the Python dependencies from the requirements file.
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application code into the container's /app directory.
COPY . .

# Tell Docker that the application inside the container will listen on port 5000.
EXPOSE 5000


# We use gunicorn, a production-ready web server, with an eventlet worker
# which is required for Flask-SocketIO to work correctly under load.
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--worker-class", "eventlet", "-w", "1", "app:app"]
