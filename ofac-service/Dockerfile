# Use an official Python runtime as a parent image
FROM python:3.9-slim

# Install cron and other dependencies
RUN apt-get update && apt-get install -y cron

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Copy the startup script to the container
COPY startup-script-cln.tpl /app/startup-script-cln.sh

# Copy the healthcheck script
COPY healthcheck.sh /app/healthcheck.sh

# Make the scripts executable
RUN chmod +x /app/startup-script-cln.sh /app/healthcheck.sh

# Copy the entrypoint script to prompt for rune
COPY entrypoint.sh /app/entrypoint.sh
RUN chmod +x /app/entrypoint.sh

# Add the cron job
RUN echo "0 * * * * /app/startup-script-cln.sh" > /etc/cron.d/startup-cron

# Give execution rights on the cron job
RUN chmod 0644 /etc/cron.d/startup-cron

# Apply cron job
RUN crontab /etc/cron.d/startup-cron

# Create the log file to be able to run tail
RUN touch /var/log/cron.log

# Health check using an external script
HEALTHCHECK --interval=30s --timeout=10s --retries=3 CMD /app/healthcheck.sh

# Use entrypoint.sh to wait for rune input before running the main CMD
ENTRYPOINT ["/app/entrypoint.sh"]

# Run the command on container startup
CMD cron && tail -f /var/log/cron.log
