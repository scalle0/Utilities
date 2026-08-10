# Google Home Integration Guide

This guide explains how to connect your Arduino temperature control system to Google Home for automatic smart plug control.

## Prerequisites

- Arduino R4 WiFi running and connected to Arduino IoT Cloud
- Smart plug compatible with Google Home
- Google Home app installed on your phone
- Arduino IoT Cloud account (free tier is sufficient)

## Method 1: Arduino IoT Cloud Automations (Recommended - Simplest & Fastest)

This is the easiest method with near-instant response time and no third-party services needed!

### Step 1: Set Up Your Smart Plug in Google Home

1. **Add smart plug to Google Home**
   - Open Google Home app
   - Tap "+" → Add device
   - Follow instructions to add your smart plug
   - Name it "Heater" for easy voice control

2. **Test manual control**
   - Say "Hey Google, turn on Heater"
   - Say "Hey Google, turn off Heater"
   - Or use Google Home app to control

### Step 2: Link Google Home to Arduino IoT Cloud

1. **Open Arduino IoT Cloud**
   - Go to [create.arduino.cc/iot](https://create.arduino.cc/iot)
   - Navigate to **Integrations** in left menu

2. **Add Google Home Integration**
   - Click **"Add Integration"**
   - Select **"Google Home"** or **"Google Assistant"**
   - Click **"Link Account"**
   - Authorize Arduino to access your Google account
   - Your Google Home devices will sync to Arduino Cloud

### Step 3: Create Automation to Turn Heater ON

1. **Go to Triggers** (or Automations)
   - In Arduino IoT Cloud, click **"Triggers"** in left menu
   - Click **"Create Trigger"** or **"New Automation"**

2. **Configure ON trigger**
   - **Name**: "Turn Heater ON"
   - **When**: Variable changes
     - Thing: Select your temperature control Thing
     - Variable: `heaterStatus`
     - Condition: `equals` or `becomes`
     - Value: `true`

3. **Set Action**
   - **Then**: Control device
     - Platform: Google Home
     - Device: Heater (your smart plug)
     - Action: Turn ON

4. **Save** the trigger

### Step 4: Create Automation to Turn Heater OFF

1. **Create second trigger**
   - Click **"Create Trigger"** again

2. **Configure OFF trigger**
   - **Name**: "Turn Heater OFF"
   - **When**: Variable changes
     - Thing: Your temperature control Thing
     - Variable: `heaterStatus`
     - Condition: `equals` or `becomes`
     - Value: `false`

3. **Set Action**
   - **Then**: Control device
     - Platform: Google Home
     - Device: Heater (your smart plug)
     - Action: Turn OFF

4. **Save** the trigger

### Step 5: Test the Integration

1. Open Arduino IoT Cloud dashboard
2. Toggle `autoControlEnabled` to OFF (disable automation)
3. Toggle `manualHeaterControl` to ON
4. Within 1-2 seconds, heater should turn on
5. Toggle `manualHeaterControl` to OFF
6. Heater should turn off immediately

**✅ That's it! Your system is now fully automated.**

## Method 2: IFTTT Integration (Alternative)

If Arduino Cloud automations don't work with your smart plug brand, you can use IFTTT as an alternative.

### When to Use IFTTT Instead

- Your smart plug brand isn't showing in Arduino Cloud Google Home integration
- You want to add custom logic or multiple actions
- You're already using IFTTT for other automations

### IFTTT Setup

1. **Create IFTTT account** at [ifttt.com](https://ifttt.com)

2. **Create applet for turning ON**
   - IF: Arduino IoT Cloud → `heaterStatus` equals `true`
   - THEN: Google Assistant → Turn on "Heater"

3. **Create applet for turning OFF**
   - IF: Arduino IoT Cloud → `heaterStatus` equals `false`
   - THEN: Google Assistant → Turn off "Heater"

**Note**: IFTTT free tier has delays (up to 60 minutes). Arduino Cloud automations are instant and recommended.

## Voice Commands with Google Assistant

Once integrated, you can use voice commands:

### Direct Heater Control
- "Hey Google, turn on the heater"
- "Hey Google, turn off the heater"
- "Hey Google, is the heater on?"

### Google Home Routines

Create routines for convenience:

**"Good Night" Routine**
1. Open Google Home app → Routines
2. Create new routine
3. When: You say "Good night"
4. Actions:
   - Turn off heater
   - Turn off lights
   - Lock doors

**"Morning Warmup" Routine**
1. Create new routine
2. When: 6:00 AM on weekdays
3. Actions:
   - Turn on heater
   - Start coffee maker
   - Play news

## Advanced Integration Features

### Scheduling in Arduino Cloud

Create time-based triggers in Arduino Cloud:

**Lower temperature at night**
- Trigger: Time schedule (10:00 PM daily)
- Action: Set Arduino variable (modify threshold or disable automation)

**Warm up before waking**
- Trigger: Time schedule (6:00 AM weekdays)
- Action: Enable automation

### Multiple Temperature Zones

If you have multiple rooms:
1. Create separate Things for each room
2. Each with its own temperature threshold
3. Link each to different smart plugs
4. Control all from one dashboard

## Troubleshooting

### Arduino Cloud Automation Not Triggering

**Check 1: Integration Status**
```
1. Arduino IoT Cloud → Integrations
2. Verify Google Home shows "Connected"
3. If not, re-link account
```

**Check 2: Trigger Configuration**
```
1. Arduino IoT Cloud → Triggers
2. Check trigger is enabled (toggle should be ON)
3. Verify variable name matches exactly: heaterStatus
4. Check condition is correct (true/false)
```

**Check 3: Smart Plug Visibility**
```
1. Ensure smart plug is online in Google Home app
2. Try manually controlling from Google Home
3. Plug name must match exactly in trigger
```

**Check 4: Arduino Cloud Connection**
```
1. Open Serial Monitor
2. Look for "Connected to Arduino IoT Cloud"
3. Verify heaterStatus variable is updating
4. Check dashboard shows correct values
```

### Google Home Device Not Showing in Arduino Cloud

**Solution 1: Refresh Integration**
```
1. Arduino IoT Cloud → Integrations
2. Click Google Home integration
3. Click "Sync Devices" or "Refresh"
4. Wait 1-2 minutes
5. Check if device appears
```

**Solution 2: Re-link Account**
```
1. Remove Google Home integration
2. Re-add and authorize again
3. Ensure all permissions granted
```

### Delayed Response

**Arduino Cloud Automations**: Should be near-instant (1-2 seconds)
- If delayed, check internet connection
- Verify Arduino Cloud status: [status.arduino.cc](https://status.arduino.cc)

**IFTTT Method**: Free tier has 1-60 minute delays
- Upgrade to IFTTT Pro ($2.50/month) for instant triggers
- Or switch to Arduino Cloud automations (free)

### Heater Turns On But Won't Turn Off

**Check both triggers exist**
```
1. One trigger for heaterStatus = true
2. Another trigger for heaterStatus = false
3. Both must be enabled
```

**Verify variable updates**
```
1. Watch dashboard while automation runs
2. heaterStatus should change from true → false
3. Check Serial Monitor confirms state change
```

## Security Best Practices

### Network Security
- Use WPA2/WPA3 WiFi encryption
- Consider separate network for IoT devices
- Keep router firmware updated

### Account Security
- Enable 2-factor authentication on:
  - Arduino Cloud account
  - Google account
- Use strong, unique passwords
- Review connected services regularly

### Smart Home Safety
- Only use certified smart plugs
- Check plug wattage rating matches heater
- Don't exceed smart plug capacity (typically 10-15A)

## Compatibility

### Supported Smart Plug Brands

Arduino Cloud Google Home integration works with most Google Home compatible plugs:

✅ **Confirmed Working**
- TP-Link Kasa
- Wemo (Belkin)
- Philips Hue (smart outlet)
- GE Cync
- Wyze Plug
- Gosund
- Tapo (TP-Link)

⚠️ **May Require IFTTT**
- Generic WiFi plugs
- Tuya/Smart Life ecosystem
- Less common brands

### Testing Your Plug

1. Add to Google Home app
2. Control via voice: "Hey Google, turn on [device]"
3. If voice works, Arduino Cloud integration will work
4. If not, use IFTTT method instead

## Alternative Smart Home Platforms

### Amazon Alexa

Replace Google Home with Alexa:
1. Arduino IoT Cloud → Integrations → Alexa
2. Create triggers same way
3. Voice: "Alexa, turn on heater"

### Apple HomeKit

Use Homebridge or IFTTT:
1. Arduino → IFTTT → HomeKit devices
2. Requires HomeKit hub (Apple TV/HomePod)
3. Control via Siri and Home app

### Home Assistant

Advanced users can integrate via:
- Arduino Cloud API
- MQTT bridge
- REST API calls
- Full local control possible

## Cost Comparison

| Method | Cost | Response Time | Complexity |
|--------|------|---------------|------------|
| Arduino Cloud Automations | Free | 1-2 seconds | Easy |
| IFTTT Free | Free | 1-60 minutes | Easy |
| IFTTT Pro | $2.50/month | <1 second | Easy |
| Webhooks | Free | 1-2 seconds | Advanced |

**Recommended**: Arduino Cloud Automations (free, fast, simple)

## Example Complete Setup

Here's what your final configuration looks like:

### Arduino Cloud Thing Variables
- `currentTemperature` → Reads from Modulino Thermo
- `autoControlEnabled` → Dashboard switch
- `heaterStatus` → Triggers smart plug
- `manualHeaterControl` → Dashboard override

### Arduino Cloud Triggers
1. **Heater ON**: When `heaterStatus` = `true` → Google Home turns ON plug
2. **Heater OFF**: When `heaterStatus` = `false` → Google Home turns OFF plug

### Dashboard Widgets
- Gauge: Shows current temperature
- Switch: Enable/disable automation
- LED: Heater status indicator
- Switch: Manual control

### Result
- Temperature drops below 23°C
- Arduino sets `heaterStatus` = `true`
- Arduino Cloud trigger fires
- Google Home turns on smart plug
- Heater starts warming room
- Temperature rises above 24°C
- Arduino sets `heaterStatus` = `false`
- Arduino Cloud trigger fires
- Google Home turns off smart plug
- Cycle repeats automatically!

## Next Steps

1. ✅ Set up Arduino Cloud automations
2. 🧪 Test with manual control first
3. ⏱️ Let automatic mode run for 24 hours
4. 📊 Monitor temperature logs
5. 🎚️ Adjust thresholds to your preference
6. 🏠 Create Google Home routines
7. 🔔 Add notifications (optional)

## Useful Resources

- [Arduino IoT Cloud Integrations](https://docs.arduino.cc/arduino-cloud/features/iot-cloud-integrations/)
- [Arduino Cloud Triggers Guide](https://docs.arduino.cc/arduino-cloud/features/triggers/)
- [Google Home Community](https://support.google.com/googlenest/community)
- [Arduino Forum - IoT Cloud](https://forum.arduino.cc/c/software/arduino-iot-cloud/)

## Pro Tips

💡 **Faster Response**: Arduino Cloud automations trigger in ~1-2 seconds vs IFTTT's 1-60 minutes

💡 **No Internet Required**: For local control, consider adding manual override button (already included via Modulino Buttons)

💡 **Energy Savings**: Monitor temperature trends in Arduino Cloud to optimize your thresholds

💡 **Safety**: System automatically turns off heater when you disable automation - built-in safety feature

Enjoy your automated smart home! 🌡️🏠✨
