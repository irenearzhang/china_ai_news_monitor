#!/bin/bash
# China AI News Monitor - Setup Script
# This script helps set up the environment and dependencies

set -e

echo "=========================================="
echo "🇨🇳 China AI News Monitor - Setup"
echo "=========================================="
echo ""

# Get script directory
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Function to print status
print_status() {
    echo -e "${GREEN}[✓]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[!]${NC} $1"
}

print_error() {
    echo -e "${RED}[✗]${NC} $1"
}

# Check Python version
echo "📦 Checking Python environment..."
if command -v python3 &> /dev/null; then
    PYTHON_VERSION=$(python3 --version 2>&1)
    print_status "Python found: $PYTHON_VERSION"
else
    print_error "Python 3 not found. Please install Python 3.8 or higher."
    exit 1
fi

# Create virtual environment
echo ""
echo "🔧 Setting up virtual environment..."
if [ ! -d "venv" ]; then
    python3 -m venv venv
    print_status "Virtual environment created"
else
    print_status "Virtual environment already exists"
fi

# Activate virtual environment
source venv/bin/activate

# Upgrade pip
echo ""
echo "⬆️  Upgrading pip..."
pip install --upgrade pip -q
print_status "pip upgraded"

# Install dependencies
echo ""
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt -q
print_status "Dependencies installed"

# Create data directory
echo ""
echo "📁 Creating data directory..."
mkdir -p data
print_status "Data directory created"

# Check configuration
echo ""
echo "📋 Checking configuration..."
if [ -f "config.yaml" ]; then
    print_status "config.yaml found"
    
    # Check if email is configured
    if grep -q "sender_email: \"\"" config.yaml || ! grep -q "sender_email:" config.yaml; then
        print_warning "Email not configured in config.yaml"
        echo "   Run 'python main.py --setup' to configure email settings"
    else
        print_status "Email configuration present"
    fi
elif [ -f "config.example.yaml" ]; then
    print_warning "config.yaml not found, copying config.example.yaml..."
    cp config.example.yaml config.yaml
    print_status "config.yaml created from template"
    echo "   Run 'python main.py --setup' to configure email settings"
else
    print_error "config.yaml and config.example.yaml not found!"
    exit 1
fi

# Make main script executable
echo ""
echo "🔐 Making scripts executable..."
chmod +x main.py
print_status "Scripts made executable"

# Summary
echo ""
echo "=========================================="
echo "✅ Setup Complete!"
echo "=========================================="
echo ""
echo "Next steps:"
echo ""
echo "1. Configure email settings:"
echo "   python main.py --setup"
echo ""
echo "2. Test email configuration:"
echo "   python main.py --test-email"
echo ""
echo "3. View current configuration:"
echo "   python main.py --config"
echo ""
echo "4. Run manually:"
echo "   python main.py"
echo ""
echo "5. Run as scheduler:"
echo "   python main.py --schedule"
echo ""
echo "For MCP integration, please refer to the README.md"
echo "=========================================="
