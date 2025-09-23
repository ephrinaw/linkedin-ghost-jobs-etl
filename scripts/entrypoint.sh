#!/bin/bash


# Initialize the database
echo "Initializing database..."
python /app/src/main.py init_db

# Start the main application
echo "Starting ETL pipeline..."
python /app/src/main.py run_etl

# Keep container running if needed
tail -f /dev/null