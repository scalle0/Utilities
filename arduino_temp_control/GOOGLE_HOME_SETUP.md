# Google Home Integration Guide

This guide explains how to connect your Arduino temperature control system to Google Home for voice control and smart home integration.

## Prerequisites

- Arduino R4 WiFi running and connected to Arduino IoT Cloud
- Smart plug compatible with Google Home
- Google Home app installed on your phone
- IFTTT account (free tier is sufficient)

## Method 1: IFTTT Integration (Recommended for Beginners)

### Step 1: Set Up Your Smart Plug

1. Plug in your heater to the smart plug
2. Set up the smart plug in Google Home app:
   - Open Google Home app
   - Tap "+" → Add device
   - Follow instructions to add your smart plug
   - Name it "Heater" for easy voice control

3. Test manual control:
   - Say "Hey Google, turn on Heater"
   - Say "Hey Google, turn off Heater"

### Step 2: Connect Arduino IoT Cloud to IFTTT

1. Go to [IFTTT.com](https://ifttt.com) and sign in
2. Click **Create** to make a new Applet
3. Click **If This**:
   - Search for "Arduino IoT Cloud"
   - Click **Connect** and authorize with your Arduino account
   - Choose trigger: **Property Value**
   - Select your Thing
   - Select Property: `heaterStatus`
   - Condition: `equals`
   - Value: `true`

4. Click **Then That**:
   - Search for "Google Assistant"
   - Click **Connect** and authorize with your Google account
   - Choose action: **Control smart plug**
   - Device: Select "Heater"
   - Action: Turn ON

5. Review and click **Continue**
6. Name it: "Arduino Heater ON"
7. Click **Finish**

### Step 3: Create OFF Applet

Repeat Step 2 with these changes:
- Trigger value: `false`
- Action: Turn OFF
- Name: "Arduino Heater OFF"

### Step 4: Test the Integration

1. Open Arduino IoT Cloud dashboard
2. Toggle `autoControlEnabled` to OFF
3. Toggle `manualHeaterControl` ON
4. Wait 10-30 seconds
5. Check if heater turned on via Google Home

## Method 2: Arduino IoT Cloud Webhooks

### Step 1: Get Google Home API Access

This method requires more technical setup but doesn't rely on IFTTT.

1. Enable Google Home API access through Google Cloud Console
2. Create OAuth credentials
3. Get access token

(Note: This is advanced - IFTTT method recommended for most users)

### Step 2: Create Webhooks in Arduino IoT Cloud

1. Go to Arduino IoT Cloud → Integrations
2. Create new Webhook
3. Configure:
   - Trigger: `heaterStatus` changes to `true`
   - Action: HTTP POST to Google Home API
   - Endpoint: Your Google Home device endpoint
   - Body: `{"on": true}`

## Voice Commands with Google Assistant

Once integrated, you can use these commands:

### Direct Heater Control
- "Hey Google, turn on the heater"
- "Hey Google, turn off the heater"

### Check Status (requires IFTTT query applet)
- "Hey Google, what's the temperature?" (if you create additional applet)

### Routines

Create Google Home routines for automated control:

1. Open Google Home app → Routines
2. Create "Good Night" routine:
   - When: You say "Good night"
   - Actions:
     - Turn off heater
     - (Other bedtime actions)

3. Create "Morning Warmup":
   - When: 6:00 AM on weekdays
   - Actions:
     - Turn on heater
     - (Other morning actions)

## Advanced: Scene Integration

### Create Temperature Scenes

1. **Comfort Mode** (warmer):
   - Modify threshold: 24-25°C
   - Enable via dashboard switch

2. **Economy Mode** (cooler):
   - Modify threshold: 21-22°C
   - Save energy

3. **Away Mode**:
   - Disable auto control
   - Turn off heater

## Troubleshooting

### IFTTT Applet Not Triggering

**Check 1: Arduino Cloud Connection**
```
- Open Serial Monitor
- Look for "Connected to Arduino IoT Cloud"
- Verify cloud variables are updating
```

**Check 2: IFTTT Service Status**
```
- Go to IFTTT → My Applets
- Check if applets are enabled
- View Activity log for errors
```

**Check 3: Timing Delays**
```
- IFTTT free tier has delays (up to 1 hour)
- Consider IFTTT Pro for faster response
- Or use Arduino Cloud webhooks instead
```

### Google Home Not Responding

**Solution 1: Reconnect Services**
```
1. IFTTT → My Services → Google Assistant
2. Disconnect and reconnect
3. Re-authorize permissions
```

**Solution 2: Check Smart Plug**
```
1. Google Home app → Device settings
2. Verify plug is online
3. Test manual control from app
```

### Delayed Response

**For IFTTT Free Tier:**
- Delays of 1-60 minutes are normal
- Upgrade to IFTTT Pro for near-instant (<1s) triggers

**For Webhook Method:**
- Should be near-instant
- Check network latency
- Verify endpoint URL is correct

## Security Best Practices

1. **Network Security**
   - Use WPA2/WPA3 WiFi encryption
   - Separate IoT devices on guest network if possible

2. **IFTTT Security**
   - Use strong passwords
   - Enable two-factor authentication
   - Review connected services regularly

3. **Google Account**
   - Enable 2-factor authentication
   - Review device permissions periodically

## Alternative Integration Options

### Alexa Instead of Google Home

Replace IFTTT Google Assistant action with Amazon Alexa action:
- Same Arduino trigger
- THEN action: Alexa → Smart plug control

### HomeKit (Apple)

Use IFTTT or Homebridge:
- Arduino → IFTTT → HomeKit compatible devices
- Requires HomeKit hub (Apple TV, HomePod, or iPad)

### Smart Life / Tuya Integration

Many smart plugs support Tuya ecosystem:
- Arduino → IFTTT → Smart Life action
- Works with Tuya-compatible smart plugs

## Cost Breakdown

| Service | Free Tier | Paid Option |
|---------|-----------|-------------|
| Arduino IoT Cloud | Yes (2 Things) | Entry: $1.99/month |
| IFTTT | Yes (2 applets, delayed) | Pro: $2.50/month |
| Google Home | Free | N/A |
| Smart Plug | One-time: $10-30 | N/A |

**Total to get started: $10-30 (just the smart plug)**

## Next Steps

1. Test the basic integration with manual control
2. Let automatic mode run for 24 hours
3. Monitor temperature logs in IoT Cloud
4. Adjust thresholds based on your comfort
5. Create Google Home routines for convenience

## Useful Resources

- [IFTTT Arduino IoT Cloud Service](https://ifttt.com/arduino_iot_cloud)
- [Arduino IoT Cloud Documentation](https://docs.arduino.cc/arduino-cloud/)
- [Google Home Community](https://support.google.com/googlenest/community)
