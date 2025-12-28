# Utilities

## Email Tone Extraction & Training Pipeline

A comprehensive toolkit to extract your sent emails, analyze their tone (formal vs informal), and create training prompts for AI agents to mimic your writing style.

### Features

- 📧 **Email Extraction**: Parse .eml files and extract your written content
- 🧹 **Smart Cleaning**: Remove quoted replies, signatures, and email artifacts
- 🎯 **Tone Classification**: Automatically classify emails as formal or informal
- 🤖 **AI Training**: Generate system prompts for training AI agents on your style

### Quick Start

#### Installation

```bash
pip install -r requirements.txt
```

#### Usage - Complete Pipeline (Recommended)

Run the entire pipeline with one command:

```bash
python run_pipeline.py /path/to/your/emails
```

This will:
1. Extract all .eml files
2. Clean and parse the content
3. Classify emails by tone
4. Generate training prompts

#### Output Files

- `extracted_emails.json` - Raw extracted email data
- `my_writing.txt` - All your writing in plain text
- `classified_emails.json` - Emails with tone classification
- `training_data/` - Separated emails by tone (formal/informal/neutral)
- `prompts/` - Ready-to-use AI prompts

See individual script files for more advanced usage options.

---

## Other Projects

Energy management system in the house (growatt integration) 
