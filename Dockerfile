# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory
WORKDIR /app

# Copy the application files
COPY . /app/

# Ensure the entrypoint script has executable permissions
RUN chmod +x /app/docker-entrypoint.sh

# Upgrade pip
RUN pip install --upgrade pip

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Fix SQLite database permissions (Ensure DB is writable)
RUN chmod -R 777 /app/db.sqlite3

# Expose the port (if needed)
EXPOSE 8000

# Set entrypoint script
ENTRYPOINT ["sh", "/app/docker-entrypoint.sh"]

# Run the application
CMD ["gunicorn", "--bind", "0.0.0.0:8000", "railway_ticket_reservation.wsgi:application"]
