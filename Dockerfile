FROM python:3.11-slim

# Set working directory inside the container
WORKDIR /app

# Copy all files into the container
COPY . /app

# Ensure the C++ binary is executable
RUN chmod +x "/app/c++ spiel/a.out"

# Expose the default port (will be overridden by environment variables in cloud hosts)
EXPOSE 8000

# Run the python server in unbuffered mode for real-time cloud logging
CMD ["python", "-u", "server.py"]
