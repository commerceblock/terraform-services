# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install cron
RUN apt-get update && apt-get install -y cron

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the inventory service script to the container
COPY scripts/inventory-service /app/inventory-service

# Make the script executable
RUN chmod +x /app/inventory-service

# Add the cron job
RUN echo "0 0 * * * /app/inventory-service" > /etc/cron.d/inventory-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/inventory-cron

# Apply cron job
RUN crontab /etc/cron.d/inventory-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
