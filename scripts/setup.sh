#!/bin/bash

# Create necessary directories
mkdir -p data/raw data/transformed data/outputs logs

# Install Python dependencies
pip install -r requirements.txt

# Install Playwright browsers (for advanced scraping if needed)
python -m playwright install chromium

# Initialize database
python src/main.py init_db

echo "Setup completed successfully!"
echo "Configure LinkedIn API credentials in .env for real job extraction:"
echo "LINKEDIN_CLIENT_ID=your_client_id"
echo "LINKEDIN_CLIENT_SECRET=your_client_secret"