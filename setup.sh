# Setup script for PA Voter Registration Data Scraper

echo "Setting up PA Voter Registration Data Scraper..."

# Create virtual environment
echo "Creating virtual environment..."
python3 -m venv venv

# Activate virtual environment
echo "Activating virtual environment..."
source venv/bin/activate

# Install dependencies
echo "Installing dependencies..."
pip install -r requirements.txt

# Create data directory
echo "Creating data directory..."
mkdir -p data

# Make scraper executable
chmod +x scraper.py

echo "Setup complete!"
echo ""
echo "To run the scraper:"
echo "1. Activate the virtual environment: source venv/bin/activate"
echo "2. Run the scraper: python scraper.py"
echo ""
echo "Data will be saved in the ./data directory"