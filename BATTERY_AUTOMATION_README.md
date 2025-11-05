# Growatt Battery Automation System

Intelligent battery management system that automatically optimizes charging schedules based on dynamic electricity prices. Save money by charging your 10kWh battery when electricity is cheapest and using it during peak price hours.

## 🎯 Features

- **Automatic Price Fetching**: Supports multiple price sources (ENTSO-E, Tibber, Nord Pool, manual)
- **Smart Optimization**: Calculates optimal charging windows to minimize costs
- **Daily Automation**: Runs automatically every day to update charging schedule
- **Multiple Control Methods**: Supports both Growatt Cloud API and local Modbus control
- **Comprehensive Logging**: Track performance and savings over time
- **Dry-run Mode**: Test configuration safely before applying real changes
- **Energy Savings**: Potential savings of €10-50+ per month depending on price volatility

## 📋 Requirements

### Hardware
- Growatt inverter with battery (tested with 10kWh systems)
- Network connection to inverter (WiFi/Ethernet for API, or RS485 for Modbus)
- Linux system for automation (Raspberry Pi, server, or any Linux machine)

### Software
- Python 3.8 or higher
- Internet connection (for price fetching)

## 🚀 Quick Start

### 1. Installation

```bash
# Clone or download the files to your system
cd /home/user/Utilities

# Install Python dependencies
pip install -r requirements.txt
```

### 2. Configuration

```bash
# Copy example configuration
cp battery_config.example.json battery_config.json

# Edit with your settings
nano battery_config.json
```

**Key settings to configure:**

```json
{
  "price_fetcher": {
    "provider": "entsoe",
    "entsoe_api_key": "YOUR_API_KEY",
    "area_code": "10YNL----------L"
  },
  "battery": {
    "battery_capacity_kwh": 10.0,
    "expected_daily_consumption": 8.0
  },
  "growatt": {
    "connection_type": "modbus",
    "modbus_host": "192.168.1.100",
    "dry_run": true
  }
}
```

### 3. Get Your API Keys

#### ENTSO-E (Free, covers most of Europe)
1. Register at https://transparency.entsoe.eu/
2. Go to "Account Settings" → "Web API Security Token"
3. Copy your token to `entsoe_api_key` in config

**Area Codes:**
- Netherlands: `10YNL----------L`
- Germany: `10YDE-VE-------2`
- France: `10YFR-RTE------C`
- Spain: `10YES-REE------0`
- Belgium: `10YBE----------2`
- [Full list](https://transparency.entsoe.eu/content/static_content/Static%20content/web%20api/Guide.html#_areas)

#### Tibber (Alternative, if you're a Tibber customer)
1. Login to Tibber app
2. Go to Settings → Developer → Personal Access Token
3. Copy token to `tibber_api_key` in config

### 4. Test Configuration

```bash
# Test all connections
python3 battery_automation.py test
```

Expected output:
```
✓ Price fetcher working: 24 price points retrieved
✓ Growatt controller working: Battery SOC = 50%
✓ All systems operational!
```

### 5. Test Optimization (Dry Run)

```bash
# Run optimization without changing inverter settings
python3 battery_automation.py run
```

Review the output to ensure charging windows make sense. Check `battery_data/` for saved schedules.

### 6. Enable Live Control

Once you're satisfied with dry-run results:

```bash
# Edit config and set dry_run to false
nano battery_config.json
# Change: "dry_run": false

# Test one more time
python3 battery_automation.py run
```

### 7. Setup Daily Automation

```bash
# Run the setup script
chmod +x setup_scheduler.sh
./setup_scheduler.sh
```

This will:
- Create a Python virtual environment
- Install dependencies
- Set up a daily cron job
- Create a manual run script

**Recommended schedule:** 13:00-14:00 (when next-day prices are usually published)

## 📖 Usage

### Manual Execution

```bash
# Run optimization now
./run_battery_automation.sh

# Or use Python directly
python3 battery_automation.py run
```

### View Logs

```bash
# Real-time log viewing
tail -f battery_automation.log

# View recent entries
tail -n 100 battery_automation.log
```

### Generate Performance Report

```bash
# 7-day report (default)
python3 battery_automation.py report

# Custom period
python3 battery_automation.py report --days 30
```

Example output:
```
BATTERY PERFORMANCE REPORT (7 days)
======================================================================
2025-11-06: Charged 8.5 kWh, Saved 1.23 €
2025-11-07: Charged 9.0 kWh, Saved 1.45 €
...
----------------------------------------------------------------------
Total savings: 9.87 €
Average per day: 1.41 €
Projected monthly: 42.30 €
```

## 🔧 Configuration Details

### Battery Settings

```json
{
  "battery_capacity_kwh": 10.0,        // Total battery capacity
  "max_charge_rate_kw": 5.0,           // Max charging power
  "max_discharge_rate_kw": 5.0,        // Max discharge power
  "min_soc": 10.0,                     // Minimum state of charge (%)
  "max_soc": 95.0,                     // Maximum state of charge (%)
  "efficiency": 0.95,                  // Round-trip efficiency
  "reserve_capacity_kwh": 1.0,         // Reserve to always maintain
  "expected_daily_consumption": 8.0    // Average daily usage
}
```

### Growatt Connection Methods

#### Option A: Modbus TCP (Recommended)

**Pros:** Local control, no cloud dependency, faster
**Cons:** Requires network access to inverter

```json
{
  "connection_type": "modbus",
  "modbus_type": "tcp",
  "modbus_host": "192.168.1.100",     // Your inverter's IP
  "modbus_port": 502,
  "modbus_unit_id": 1
}
```

**Finding your inverter's IP:**
```bash
# Check your router's DHCP leases
# Or use network scanner
sudo nmap -sn 192.168.1.0/24
```

#### Option B: Modbus RTU (Serial/RS485)

**Pros:** Direct connection, very reliable
**Cons:** Requires physical RS485 connection

```json
{
  "connection_type": "modbus",
  "modbus_type": "rtu",
  "serial_port": "/dev/ttyUSB0",      // RS485 adapter
  "baudrate": 9600
}
```

#### Option C: Growatt Cloud API

**Pros:** Works from anywhere
**Cons:** Requires cloud access, may have rate limits

```json
{
  "connection_type": "api",
  "username": "your_growatt_username",
  "password": "your_growatt_password",
  "device_serial": "XXXXXX"           // From Growatt app
}
```

## 📊 How It Works

1. **Price Fetching** (13:00 daily)
   - Fetches next day's hourly electricity prices
   - Saves prices to `battery_data/prices_YYYYMMDD.csv`

2. **Optimization**
   - Analyzes price patterns
   - Identifies cheapest hours for charging
   - Identifies expensive hours for battery usage
   - Calculates optimal charging windows
   - Maximizes savings while meeting energy needs

3. **Schedule Application**
   - Converts optimal schedule to Growatt time slots
   - Updates inverter charging schedule via API/Modbus
   - Saves schedule to `battery_data/schedule_*.json`

4. **Execution**
   - Inverter automatically charges during scheduled times
   - Battery available for use during expensive hours
   - Process repeats daily

## 💡 Optimization Strategy

The system uses intelligent algorithms to determine when to charge:

- **Charging Threshold**: Charge when price < 25th percentile
- **Discharge Threshold**: Prioritize battery when price > 75th percentile
- **Energy Balancing**: Ensures enough charge for expected consumption
- **Efficiency Consideration**: Accounts for round-trip losses
- **Peak Shaving**: Maximizes battery use during highest prices

**Example Day:**
```
00:00-06:00  Low prices   → CHARGE (02:00-06:00)
06:00-08:00  Rising       → Battery First mode
08:00-16:00  Moderate     → Normal operation
16:00-21:00  Peak prices  → Battery First mode
21:00-24:00  Falling      → Normal operation
```

## 🔍 Troubleshooting

### Price Fetching Issues

**ENTSO-E Returns No Data:**
```bash
# Check if prices are published yet (usually after 13:00)
# Try fetching today's prices first
python3 -c "from price_fetcher import *; from datetime import datetime;
config = {'provider': 'entsoe', 'entsoe_api_key': 'YOUR_KEY', 'area_code': 'YOUR_CODE'};
fetcher = get_price_fetcher(config);
print(fetcher.fetch_prices(datetime.now()))"
```

**Wrong Area Code:**
- Verify your area code at https://transparency.entsoe.eu/
- Some countries have multiple zones

### Growatt Connection Issues

**Modbus Connection Failed:**
```bash
# Test if inverter is reachable
ping 192.168.1.100

# Check if Modbus port is open
nc -zv 192.168.1.100 502

# Some inverters need Modbus enabled in settings
```

**API Authentication Failed:**
- Verify username/password in Growatt app
- Check if 2FA is enabled (may need app password)
- Some accounts require API access activation

**Register Addresses Wrong:**
- Modbus registers vary by inverter model
- Check your inverter's Modbus documentation
- Common models: SPH, MIN, MID, MAX series
- Adjust register addresses in `growatt_controller.py`

### Schedule Not Applied

**Check Inverter Time Slots:**
- Login to Growatt app
- Go to Settings → Time periods
- Verify slots were updated

**Dry Run Still Enabled:**
```bash
# Check config
grep dry_run battery_config.json
# Should show: "dry_run": false
```

### Permission Errors

```bash
# If cron job fails with permissions
chmod +x setup_scheduler.sh run_battery_automation.sh
chmod +r battery_config.json
```

## 📈 Expected Savings

Savings depend on:
- Price volatility in your market
- Your consumption patterns
- Battery capacity vs. usage
- Current electricity rates

**Example Scenarios:**

| Market | Daily Price Range | Battery Size | Avg. Daily Savings | Monthly Savings |
|--------|------------------|--------------|-------------------|-----------------|
| High volatility (NL, DE) | €0.05 - €0.30/kWh | 10 kWh | €1.50 | €45 |
| Medium volatility | €0.10 - €0.25/kWh | 10 kWh | €1.00 | €30 |
| Low volatility | €0.12 - €0.18/kWh | 10 kWh | €0.40 | €12 |

**Additional benefits:**
- Reduces grid dependency
- Helps balance grid load
- Increases battery ROI
- Enables participation in demand response programs

## 🛡️ Safety & Best Practices

### Battery Health

- **Avoid deep cycles:** Keep min_soc at 10-20%
- **Avoid full charges:** Keep max_soc at 90-95%
- **Temperature monitoring:** Check inverter warnings
- **Cycle counting:** Modern batteries handle 6000+ cycles

### System Maintenance

```bash
# Weekly: Check logs for errors
tail -n 500 battery_automation.log | grep -i error

# Monthly: Review performance report
python3 battery_automation.py report --days 30

# Quarterly: Update software
pip install --upgrade -r requirements.txt
```

### Backup Configuration

```bash
# Backup config
cp battery_config.json battery_config.backup

# Backup before updates
tar -czf battery_automation_backup_$(date +%Y%m%d).tar.gz *.py *.json *.sh battery_data/
```

## 🔄 Advanced Configuration

### Multiple Daily Updates

Some markets publish intraday updates. To run optimization twice daily:

```bash
# Edit crontab
crontab -e

# Add second run
0 13 * * * cd /path/to/Utilities && ./venv/bin/python3 battery_automation.py run
0 20 * * * cd /path/to/Utilities && ./venv/bin/python3 battery_automation.py run
```

### Custom Optimization Logic

Edit `battery_optimizer.py` to implement custom strategies:

```python
# Example: More aggressive charging during very cheap hours
if price < analysis['price_10th']:
    # Charge at 100% power
    pass
```

### Integration with Home Assistant

```yaml
# Example sensor
sensor:
  - platform: command_line
    name: Battery Schedule
    command: "cat /path/to/Utilities/battery_data/schedule_latest.json"
    scan_interval: 3600
```

## 📝 Files Overview

| File | Purpose |
|------|---------|
| `battery_automation.py` | Main orchestration script |
| `price_fetcher.py` | Electricity price fetching |
| `battery_optimizer.py` | Optimization algorithms |
| `growatt_controller.py` | Inverter control |
| `battery_config.json` | Your configuration |
| `requirements.txt` | Python dependencies |
| `setup_scheduler.sh` | Automated setup script |
| `battery_data/` | Output directory (logs, schedules, prices) |

## 🤝 Contributing

Found a bug or have an improvement? Contributions welcome!

## 📄 License

This project is provided as-is for personal use with Growatt energy systems.

## ⚠️ Disclaimer

- This software controls your battery system - test thoroughly before use
- Always start with `dry_run: true`
- Monitor system behavior closely in the first weeks
- Electricity market prices can be volatile
- Past savings don't guarantee future performance
- Consult your electricity contract for any restrictions on charging patterns

## 🆘 Support

For issues:
1. Check logs: `tail -f battery_automation.log`
2. Run test: `python3 battery_automation.py test`
3. Review configuration: Ensure all fields are correct
4. Check Growatt app: Verify inverter is online

## 📚 Additional Resources

- [ENTSO-E Transparency Platform](https://transparency.entsoe.eu/)
- [Growatt Website](https://www.growatt.com/)
- [Tibber API Documentation](https://developer.tibber.com/)
- [Modbus Protocol Specification](https://modbus.org/)

---

**Happy Optimizing! 🔋⚡💰**
