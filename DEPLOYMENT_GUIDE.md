# Deployment Guide: Using Your Trained Email Agent

After training the agent on your email style, here are multiple ways to deploy and use it:

## 🎯 Deployment Options

### 1. Interactive CLI Tool (Easiest)

Use the email composer directly from command line:

```bash
# Interactive mode
python email_composer.py

# Direct mode
python email_composer.py --provider anthropic --tone formal \
  --context "Request quarterly review meeting with management"
```

**Pros**: Simple, no setup required
**Cons**: Manual process for each email

---

### 2. Gmail Integration (Recommended)

Automatically create Gmail drafts in your style:

#### Setup:
```bash
# Install dependencies
pip install google-auth google-auth-oauthlib google-api-python-client

# Get Gmail API credentials
# 1. Go to https://console.cloud.google.com/
# 2. Create project → Enable Gmail API
# 3. Create OAuth 2.0 credentials
# 4. Download credentials.json
```

#### Usage:
```bash
python gmail_integration.py \
  --to client@company.com \
  --subject "Project Update Request" \
  --context "Ask for status update on the Q4 deliverables" \
  --tone formal
```

This creates a draft in your Gmail that you can review and send!

**Pros**: Direct integration with Gmail, review before sending
**Cons**: Requires Gmail API setup

---

### 3. Web API Service

Run as a microservice that can be called from anywhere:

#### Setup:
```bash
# Install Flask
pip install flask flask-cors

# Set API keys
export ANTHROPIC_API_KEY="your-key-here"

# Run server
python web_service.py
```

#### Usage:
```bash
# From command line
curl -X POST http://localhost:5000/api/compose \
  -H "Content-Type: application/json" \
  -d '{
    "context": "Thank the team for their hard work",
    "tone": "informal"
  }'

# From JavaScript (e.g., browser extension)
fetch('http://localhost:5000/api/compose', {
  method: 'POST',
  headers: {'Content-Type': 'application/json'},
  body: JSON.stringify({
    context: 'Invite team to lunch',
    tone: 'informal'
  })
})
```

**Pros**: Can integrate with any app, browser extension, or script
**Cons**: Need to keep service running

---

### 4. Browser Extension (Advanced)

Create a Chrome/Firefox extension that integrates with Gmail/Outlook web:

```javascript
// Example: Inject button into Gmail compose window
// content_script.js

function injectComposeButton() {
  const composeButtons = document.querySelectorAll('[role="button"]');

  const aiButton = document.createElement('button');
  aiButton.textContent = '🤖 Use My Style';
  aiButton.onclick = async () => {
    const context = prompt('What should this email say?');

    const response = await fetch('http://localhost:5000/api/compose', {
      method: 'POST',
      headers: {'Content-Type': 'application/json'},
      body: JSON.stringify({context, tone: 'formal'})
    });

    const data = await response.json();

    // Insert into compose box
    const composeBox = document.querySelector('[role="textbox"]');
    composeBox.innerHTML = data.email;
  };

  // Add to Gmail toolbar
  const toolbar = document.querySelector('[role="toolbar"]');
  toolbar.appendChild(aiButton);
}

// Run when Gmail loads
window.addEventListener('load', injectComposeButton);
```

**Pros**: Seamless integration with web email clients
**Cons**: Requires web service running, more complex setup

---

### 5. Outlook/Apple Mail Integration

#### For Outlook (Windows):

Create a VBA macro or Office Add-in:

```vbscript
' Outlook VBA Macro
Sub ComposeWithAI()
    Dim context As String
    context = InputBox("What should this email say?")

    ' Call your API
    Dim http As Object
    Set http = CreateObject("MSXML2.XMLHTTP")

    http.Open "POST", "http://localhost:5000/api/compose", False
    http.setRequestHeader "Content-Type", "application/json"
    http.send "{""context"":""" & context & """,""tone"":""formal""}"

    ' Parse response and insert into email
    Dim response As String
    response = http.responseText

    ' Insert into current email
    ActiveInspector.CurrentItem.Body = response
End Sub
```

#### For Apple Mail (macOS):

Create an AppleScript:

```applescript
-- Save as: ~/Library/Application Scripts/com.apple.mail/ComposeWithAI.scpt

tell application "Mail"
    set emailContext to text returned of (display dialog "What should this email say?" default answer "")

    -- Call API (requires curl)
    set apiResponse to do shell script "curl -s -X POST http://localhost:5000/api/compose -H 'Content-Type: application/json' -d '{\"context\":\"" & emailContext & "\",\"tone\":\"formal\"}'"

    -- Create new email with response
    set newMessage to make new outgoing message
    set content of newMessage to apiResponse

    activate
end tell
```

**Pros**: Native integration with desktop email clients
**Cons**: Platform-specific, requires scripting knowledge

---

## 🔧 Quick Start Recommendation

**Start with Option 1 or 2** (CLI or Gmail integration):

1. **First time setup:**
   ```bash
   pip install -r requirements.txt
   pip install anthropic  # or openai
   export ANTHROPIC_API_KEY="your-key-here"
   ```

2. **Quick test:**
   ```bash
   python email_composer.py
   ```

3. **For Gmail users:**
   ```bash
   # One-time Gmail setup
   pip install google-auth google-auth-oauthlib google-api-python-client
   # Download credentials.json from Google Cloud Console

   # Use it
   python gmail_integration.py \
     --to recipient@email.com \
     --subject "Meeting Request" \
     --context "Request 30min meeting to discuss project timeline" \
     --tone formal
   ```

---

## 💡 Advanced: Automated Workflows

### Option A: Email Templates with Placeholders

Create templates for common emails:

```python
# save_templates.py
templates = {
    'meeting_request': {
        'context': 'Request a {duration} meeting to discuss {topic}',
        'tone': 'formal'
    },
    'thank_you': {
        'context': 'Thank {person} for {reason}',
        'tone': 'informal'
    }
}
```

### Option B: Slack Bot Integration

```python
# slack_bot.py
from slack_bolt import App

app = App(token="xoxb-your-token")

@app.command("/compose-email")
def compose_email_command(ack, command, say):
    ack()
    # Call your email API
    # Post result back to Slack
```

### Option C: Zapier/Make.com Integration

1. Set up web service (Option 3)
2. Create Zapier webhook trigger
3. Connect to Gmail, Outlook, etc.
4. Auto-compose replies based on triggers

---

## 📊 Comparison Table

| Method | Setup Difficulty | Integration | Best For |
|--------|-----------------|-------------|----------|
| CLI Tool | ⭐ Easy | Manual | Testing, occasional use |
| Gmail API | ⭐⭐ Medium | Gmail only | Gmail users, frequent emails |
| Web Service | ⭐⭐ Medium | Universal | Developers, automation |
| Browser Ext | ⭐⭐⭐ Hard | Web clients | Power users, seamless UX |
| Desktop Client | ⭐⭐⭐ Hard | Outlook/Mail | Corporate environments |

---

## 🔐 Security Considerations

1. **API Keys**: Never commit API keys to git. Use environment variables.

2. **Local vs Cloud**:
   - Run web service locally (localhost) for personal use
   - Use HTTPS and authentication for production deployments

3. **Email Data**: Your training data contains personal emails. Keep prompts private.

4. **Review Before Sending**: Always review AI-generated emails before sending.

---

## 🚀 Next Steps

1. ✅ Train the model: `python run_pipeline.py /path/to/emails`
2. ✅ Test with CLI: `python email_composer.py`
3. ✅ Choose deployment method based on your email client
4. ✅ Automate your workflow!

## 📝 Need Help?

- Check `example_usage.py` for API examples
- See individual scripts for detailed usage
- Review prompts in `prompts/` directory
