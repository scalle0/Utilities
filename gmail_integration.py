#!/usr/bin/env python3
"""
Gmail Integration - Compose emails directly in Gmail using your trained style
"""

import os
import pickle
from pathlib import Path
from typing import Optional

# Gmail API imports
try:
    from google.auth.transport.requests import Request
    from google.oauth2.credentials import Credentials
    from google_auth_oauthlib.flow import InstalledAppFlow
    from googleapiclient.discovery import build
    GMAIL_AVAILABLE = True
except ImportError:
    GMAIL_AVAILABLE = False


SCOPES = ['https://www.googleapis.com/auth/gmail.compose']


class GmailIntegration:
    """Integration with Gmail for composing emails in your style"""

    def __init__(self):
        self.service = None
        self.creds = None

    def authenticate(self, credentials_file: str = 'credentials.json'):
        """Authenticate with Gmail API"""
        if not GMAIL_AVAILABLE:
            print("Error: Google API libraries not installed!")
            print("Install with: pip install google-auth google-auth-oauthlib google-auth-httplib2 google-api-python-client")
            return False

        token_file = 'token.pickle'

        # Check if we have existing credentials
        if os.path.exists(token_file):
            with open(token_file, 'rb') as token:
                self.creds = pickle.load(token)

        # If there are no (valid) credentials, let user log in
        if not self.creds or not self.creds.valid:
            if self.creds and self.creds.expired and self.creds.refresh_token:
                self.creds.refresh(Request())
            else:
                if not os.path.exists(credentials_file):
                    print(f"Error: {credentials_file} not found!")
                    print("\nTo use Gmail integration:")
                    print("1. Go to https://console.cloud.google.com/")
                    print("2. Create a new project or select existing")
                    print("3. Enable Gmail API")
                    print("4. Create OAuth 2.0 credentials")
                    print("5. Download credentials.json")
                    return False

                flow = InstalledAppFlow.from_client_secrets_file(
                    credentials_file, SCOPES)
                self.creds = flow.run_local_server(port=0)

            # Save credentials for next run
            with open(token_file, 'wb') as token:
                pickle.dump(self.creds, token)

        # Build the service
        self.service = build('gmail', 'v1', credentials=self.creds)
        print("✓ Authenticated with Gmail")
        return True

    def create_draft(self, to: str, subject: str, body: str, cc: Optional[str] = None):
        """Create a Gmail draft"""
        if not self.service:
            print("Error: Not authenticated. Call authenticate() first.")
            return None

        from email.mime.text import MIMEText
        import base64

        message = MIMEText(body)
        message['to'] = to
        message['subject'] = subject
        if cc:
            message['cc'] = cc

        raw_message = base64.urlsafe_b64encode(message.as_bytes()).decode('utf-8')

        try:
            draft = self.service.users().drafts().create(
                userId='me',
                body={'message': {'raw': raw_message}}
            ).execute()

            print(f"✓ Draft created! Draft ID: {draft['id']}")
            print(f"  View in Gmail: https://mail.google.com/mail/#drafts")
            return draft

        except Exception as e:
            print(f"Error creating draft: {e}")
            return None


class EmailDraftComposer:
    """Compose email drafts using AI and save to Gmail"""

    def __init__(self, ai_provider='anthropic'):
        self.ai_provider = ai_provider
        self.gmail = GmailIntegration()

    def compose_and_draft(self, to: str, subject: str, context: str,
                         tone: str = 'formal', api_key: Optional[str] = None):
        """Compose an email using AI and create a Gmail draft"""

        # Load the system prompt
        prompt_file = f'prompts/{tone}_system_prompt.txt'
        if not Path(prompt_file).exists():
            print(f"Error: {prompt_file} not found. Run the pipeline first!")
            return None

        with open(prompt_file, 'r', encoding='utf-8') as f:
            system_prompt = f.read()

        # Generate email body using AI
        print(f"🤖 Generating {tone} email using {self.ai_provider}...")

        if self.ai_provider == 'anthropic':
            body = self._compose_with_anthropic(system_prompt, context, api_key)
        elif self.ai_provider == 'openai':
            body = self._compose_with_openai(system_prompt, context, api_key)
        else:
            print(f"Unknown provider: {self.ai_provider}")
            return None

        if not body:
            return None

        print("\n" + "="*60)
        print("GENERATED EMAIL")
        print("="*60)
        print(body)
        print("="*60)

        # Ask user to confirm
        confirm = input("\nCreate Gmail draft with this content? (y/n): ").strip().lower()

        if confirm != 'y':
            print("Draft cancelled.")
            return None

        # Authenticate and create draft
        if not self.gmail.authenticate():
            return None

        draft = self.gmail.create_draft(to, subject, body)
        return draft

    def _compose_with_anthropic(self, system_prompt: str, context: str, api_key: Optional[str]) -> Optional[str]:
        """Compose using Anthropic Claude"""
        try:
            import anthropic
        except ImportError:
            print("Error: anthropic package not installed. Run: pip install anthropic")
            return None

        if not api_key:
            api_key = os.getenv('ANTHROPIC_API_KEY')

        if not api_key:
            api_key = input("Enter your Anthropic API key: ")

        try:
            client = anthropic.Anthropic(api_key=api_key)
            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {"role": "user", "content": f"Write an email: {context}"}
                ]
            )
            return message.content[0].text
        except Exception as e:
            print(f"Error: {e}")
            return None

    def _compose_with_openai(self, system_prompt: str, context: str, api_key: Optional[str]) -> Optional[str]:
        """Compose using OpenAI"""
        try:
            import openai
        except ImportError:
            print("Error: openai package not installed. Run: pip install openai")
            return None

        if not api_key:
            api_key = os.getenv('OPENAI_API_KEY')

        if not api_key:
            api_key = input("Enter your OpenAI API key: ")

        openai.api_key = api_key

        try:
            response = openai.ChatCompletion.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": f"Write an email: {context}"}
                ],
                temperature=0.7,
                max_tokens=800
            )
            return response.choices[0].message.content
        except Exception as e:
            print(f"Error: {e}")
            return None


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Compose emails and create Gmail drafts in your style',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python gmail_integration.py --to john@example.com --subject "Meeting Request" \\
    --context "Request a 30-min meeting to discuss Q4 goals" --tone formal

  python gmail_integration.py --to friends@example.com --subject "Party!" \\
    --context "Invite to birthday party this Saturday" --tone informal

Setup:
  1. Install: pip install google-auth google-auth-oauthlib google-api-python-client
  2. Get Gmail API credentials from https://console.cloud.google.com/
  3. Download credentials.json to this directory
  4. Set ANTHROPIC_API_KEY or OPENAI_API_KEY environment variable
        """
    )
    parser.add_argument('--to', required=True, help='Recipient email address')
    parser.add_argument('--subject', required=True, help='Email subject')
    parser.add_argument('--context', required=True, help='Email context/description')
    parser.add_argument('--tone', choices=['formal', 'informal'], default='formal',
                       help='Email tone (default: formal)')
    parser.add_argument('--provider', choices=['openai', 'anthropic'], default='anthropic',
                       help='AI provider (default: anthropic)')
    parser.add_argument('--api-key', help='API key for AI provider')

    args = parser.parse_args()

    composer = EmailDraftComposer(ai_provider=args.provider)
    composer.compose_and_draft(
        to=args.to,
        subject=args.subject,
        context=args.context,
        tone=args.tone,
        api_key=args.api_key
    )


if __name__ == '__main__':
    main()
