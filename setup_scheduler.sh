#!/bin/bash
#
# Setup Scheduler for Battery Automation
# This script sets up a cron job to run the battery optimization daily
#

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo "======================================"
echo "Battery Automation Scheduler Setup"
echo "======================================"
echo

# Get the directory where this script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Check if Python 3 is available
if ! command -v python3 &> /dev/null; then
    echo -e "${RED}Error: Python 3 is not installed${NC}"
    exit 1
fi

echo -e "${GREEN}✓${NC} Python 3 found: $(python3 --version)"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓${NC} Virtual environment created"
fi

# Activate virtual environment
source venv/bin/activate

# Install requirements
echo -e "${YELLOW}Installing requirements...${NC}"
pip install -q --upgrade pip
pip install -q -r requirements.txt
echo -e "${GREEN}✓${NC} Requirements installed"

# Check if configuration file exists
if [ ! -f "battery_config.json" ]; then
    echo -e "${YELLOW}Warning: battery_config.json not found${NC}"
    echo "Creating from example..."
    cp battery_config.example.json battery_config.json
    echo -e "${YELLOW}Please edit battery_config.json with your settings before running${NC}"
fi

# Test the configuration
echo
echo -e "${YELLOW}Testing configuration...${NC}"
if python3 battery_automation.py test; then
    echo -e "${GREEN}✓${NC} Configuration test passed"
else
    echo -e "${RED}✗${NC} Configuration test failed"
    echo "Please fix the configuration and run this script again"
    exit 1
fi

# Ask user for schedule time
echo
echo "When should the optimization run daily?"
echo "Recommendation: Run at 13:00-14:00 when next-day prices are usually published"
read -p "Enter hour (0-23, default 13): " HOUR
HOUR=${HOUR:-13}

read -p "Enter minute (0-59, default 0): " MINUTE
MINUTE=${MINUTE:-0}

# Validate inputs
if ! [[ "$HOUR" =~ ^[0-9]+$ ]] || [ "$HOUR" -lt 0 ] || [ "$HOUR" -gt 23 ]; then
    echo -e "${RED}Invalid hour. Using default (13)${NC}"
    HOUR=13
fi

if ! [[ "$MINUTE" =~ ^[0-9]+$ ]] || [ "$MINUTE" -lt 0 ] || [ "$MINUTE" -gt 59 ]; then
    echo -e "${RED}Invalid minute. Using default (0)${NC}"
    MINUTE=0
fi

# Create the cron job
CRON_CMD="$MINUTE $HOUR * * * cd $SCRIPT_DIR && $SCRIPT_DIR/venv/bin/python3 $SCRIPT_DIR/battery_automation.py run >> $SCRIPT_DIR/battery_automation.log 2>&1"

# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "battery_automation.py"; then
    echo
    echo -e "${YELLOW}Cron job already exists. Removing old entry...${NC}"
    crontab -l 2>/dev/null | grep -v "battery_automation.py" | crontab -
fi

# Add new cron job
echo
echo "Adding cron job..."
(crontab -l 2>/dev/null; echo "$CRON_CMD") | crontab -

echo -e "${GREEN}✓${NC} Cron job added successfully!"
echo
echo "Schedule: Daily at $(printf "%02d:%02d" $HOUR $MINUTE)"
echo "Log file: $SCRIPT_DIR/battery_automation.log"
echo

# Create a wrapper script for manual execution
cat > run_battery_automation.sh << 'EOF'
#!/bin/bash
# Manual execution wrapper
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"
source venv/bin/activate
python3 battery_automation.py run
EOF

chmod +x run_battery_automation.sh

echo -e "${GREEN}✓${NC} Created manual run script: run_battery_automation.sh"
echo

# Summary
echo "======================================"
echo "Setup Complete!"
echo "======================================"
echo
echo "Next steps:"
echo "1. Edit battery_config.json with your actual settings"
echo "2. Set dry_run to false in battery_config.json when ready"
echo "3. Test manually: ./run_battery_automation.sh"
echo "4. Check logs: tail -f battery_automation.log"
echo
echo "The automation will run automatically at $(printf "%02d:%02d" $HOUR $MINUTE) daily"
echo
echo "To view current cron jobs: crontab -l"
echo "To remove cron job: crontab -e (then delete the line)"
echo

deactivate
