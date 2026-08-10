# ESP32 Temperature Control - Parts List

Complete shopping list for building your ESP32-based temperature control system.

## Required Components

### Main Board
**ESP32 Development Board** (Choose one)
- **Recommended**: ESP32 DevKit V1 (30 pins)
  - Price: $5-8
  - Built-in WiFi and Bluetooth
  - USB-C or Micro USB
  - Where to buy: Amazon, AliExpress, Adafruit, SparkFun

- **Alternative**: ESP32-WROOM-32
  - Price: $6-10
  - Same features, different form factor

### Temperature Sensor (Choose one)

#### Option 1: DS18B20 Digital Temperature Sensor (Recommended)
- **Type**: 1-Wire digital waterproof probe
- **Price**: $3-5
- **Accuracy**: ±0.5°C
- **Range**: -55°C to +125°C
- **Pros**:
  - Waterproof version available
  - Very accurate
  - Easy to use (3 wires: VCC, GND, DATA)
  - Multiple sensors on same pin possible
- **Cons**: Only temperature (no humidity)
- **Where to buy**: Amazon, AliExpress
- **Part number**: DS18B20 (waterproof probe version)

#### Option 2: DHT22 Temperature & Humidity Sensor
- **Type**: Digital temperature + humidity
- **Price**: $4-7
- **Accuracy**: ±0.5°C, ±2-5% humidity
- **Range**: -40°C to +80°C
- **Pros**:
  - Measures both temp and humidity
  - Simple 3-pin interface
- **Cons**: Slower update rate (2 seconds)
- **Where to buy**: Amazon, AliExpress, Adafruit
- **Part number**: DHT22 or AM2302

#### Option 3: BME280 Temperature, Humidity & Pressure Sensor
- **Type**: I2C/SPI digital sensor module
- **Price**: $5-8
- **Accuracy**: ±1°C, ±3% humidity
- **Range**: -40°C to +85°C
- **Pros**:
  - 3-in-1: Temperature + Humidity + Pressure
  - I2C interface (easy wiring)
  - Small module
- **Cons**: Slightly more expensive
- **Where to buy**: Amazon, AliExpress, Adafruit, SparkFun
- **Part number**: BME280 breakout board

### Buttons

#### Option 1: Tactile Push Buttons (Recommended - Cheapest)
- **Quantity**: 1-2 buttons
- **Type**: 12mm tactile push button switches
- **Price**: $0.10-0.50 each (buy pack of 20 for $2-3)
- **Where to buy**: Amazon, AliExpress
- **Notes**:
  - 4 pins (but only 2 used)
  - Breadboard friendly
  - Need 10kΩ pull-up resistors (or use internal pull-ups)

#### Option 2: Button Module
- **Quantity**: 1-2 modules
- **Type**: Pre-wired button module with resistor
- **Price**: $1-2 per module
- **Where to buy**: Amazon, AliExpress
- **Notes**: Built-in pull-up, 3 pins (VCC, GND, SIGNAL)

### Smart Plug
**Google Home Compatible Smart Plug** (Choose one)
- **TP-Link Kasa Smart Plug Mini (EP10)**: $12-15
- **Wemo Mini Smart Plug**: $15-20
- **Gosund Smart Plug**: $8-12
- **Wyze Plug**: $7-10

**Requirements**: Must support Google Home integration

### Additional Components

#### Breadboard & Wires
- **Breadboard**: 830 point breadboard ($3-5)
- **Jumper wires**: Male-to-male (for breadboard) ($2-5 for 65pcs)
- **Optional**: Female-to-male wires if using modules

#### Resistors (if using basic tactile buttons)
- **10kΩ resistors**: 2-3 pieces
- **Or use**: ESP32 internal pull-up resistors (free!)

#### Power Supply
- **USB Cable**: Micro USB or USB-C (depending on ESP32 board)
- **USB Power Adapter**: 5V 1A minimum ($3-5)
  - Or use phone charger

#### Optional: Enclosure
- **Project box**: 100x60x25mm plastic enclosure ($3-5)
- **Or 3D print**: Custom case (free if you have 3D printer)

## Complete Kit Recommendations

### Budget Kit (~$20-25)
```
- ESP32 DevKit V1: $6
- DS18B20 waterproof sensor: $3
- 2x Tactile buttons: $0.50
- 10kΩ resistors (3pcs): $0.10
- Breadboard: $3
- Jumper wires: $2
- USB cable: $2
- Smart plug (Gosund): $10
─────────────────────────
Total: ~$26.60
```

### Standard Kit (~$30-35)
```
- ESP32 DevKit V1: $7
- BME280 sensor module: $6
- Button module (2pcs): $3
- Breadboard: $4
- Jumper wires: $3
- USB cable: $2
- USB power adapter: $4
- Smart plug (TP-Link Kasa): $12
─────────────────────────
Total: ~$41
```

### Premium Kit (~$45-50)
```
- ESP32-WROOM-32: $10
- BME280 sensor: $7
- Quality button modules: $4
- Large breadboard: $5
- Premium jumper wires: $5
- USB-C cable: $3
- USB power adapter: $5
- Smart plug (Wemo): $18
- Project enclosure: $4
─────────────────────────
Total: ~$61
```

## Recommended Shopping List (Budget Option)

**My recommendation for beginners:**

| Item | Recommended Product | Price | Link Keywords |
|------|-------------------|-------|---------------|
| ESP32 Board | ESP32 DevKit V1 | $6 | "ESP32 DevKit V1 30 pin" |
| Temperature Sensor | DS18B20 Waterproof | $3 | "DS18B20 waterproof temperature sensor" |
| Buttons | 12mm Tactile Buttons (20 pack) | $2 | "12mm tactile push button switch" |
| Resistors | 10kΩ Resistor Kit | $3 | "10k ohm resistor kit" |
| Breadboard | 830 point breadboard | $3 | "830 point breadboard" |
| Jumper Wires | 65pcs Male-to-Male | $2 | "breadboard jumper wires male to male" |
| USB Cable | Micro USB cable | $2 | "micro USB cable" |
| Smart Plug | Gosund Smart Plug | $10 | "Gosund smart plug Google Home" |

**Total: ~$31** (excluding power adapter - use phone charger)

## Where to Buy

### Online Retailers

**United States:**
- Amazon (fast shipping, easy returns)
- Adafruit (quality components, tutorials)
- SparkFun (quality components, support)
- AliExpress (cheapest, slower shipping 2-4 weeks)

**Europe:**
- Amazon (country-specific)
- AliExpress
- Pimoroni (UK)
- Berrybase (Germany)

**International:**
- AliExpress (worldwide shipping)
- Banggood (worldwide)
- eBay

## Wiring Accessories Needed

### For DS18B20 Sensor
- 3 wires (usually included with waterproof version)
- 4.7kΩ resistor (pull-up for data line) - usually included

### For DHT22 Sensor
- 3 wires
- Usually comes with resistor on module

### For BME280 Sensor
- 4 wires (for I2C: VCC, GND, SDA, SCL)
- No resistor needed (built into module)

### For Tactile Buttons
- 2 wires per button
- 10kΩ resistor per button (or use internal pull-up)

## What's Included vs What to Buy

### Usually Included with Sensors
✅ DS18B20 waterproof: Cable with connector, pull-up resistor
✅ DHT22: Sometimes on module with resistor
✅ BME280: On breakout board with voltage regulator and resistors

### Need to Buy Separately
❌ Breadboard
❌ Jumper wires
❌ USB cable (sometimes included with ESP32)
❌ Power adapter
❌ Smart plug

## Cost Comparison: ESP32 vs Arduino R4 WiFi

| Component | ESP32 Version | Arduino R4 WiFi + Modulino |
|-----------|--------------|---------------------------|
| Main Board | $6 | $30+ (Arduino R4 WiFi) |
| Temp Sensor | $3-6 | $20+ (Modulino Thermo) |
| Buttons | $0.50-3 | $20+ (Modulino Buttons) |
| Modulino Base | $0 | $15+ |
| **Total (before plug)** | **$10-15** | **$85+** |

**ESP32 version is ~75% cheaper!**

## Alternative: All-in-One Kits

Some sellers offer ESP32 starter kits that include:
- ESP32 board
- Breadboard
- Jumper wires
- Various sensors (including temp sensors)
- Buttons and LEDs
- Resistors and capacitors

**Price**: $20-30
**Search for**: "ESP32 starter kit" or "ESP32 development kit"

## Next Steps

1. **Choose your components** based on budget
2. **Order from preferred retailer**
3. **While waiting for delivery**:
   - Set up Arduino IoT Cloud account
   - Install Arduino IDE
   - Read HARDWARE_SETUP_ESP32.md
4. **When parts arrive**:
   - Follow wiring guide
   - Upload code
   - Test and enjoy!

## Support and Community

**If you need help choosing parts:**
- Arduino Forum: forum.arduino.cc
- Reddit: r/arduino, r/esp32
- Discord: Arduino Discord server

**Before buying:**
- Check compatibility with Google Home
- Read reviews
- Compare prices across retailers
- Consider shipping time vs cost

Happy building! 🛠️
