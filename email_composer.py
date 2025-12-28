#!/usr/bin/env python3
"""
Email Composer - Interactive tool to compose emails in your style
"""

import sys
from pathlib import Path
from typing import Optional


class EmailComposer:
    """Compose emails using AI trained on your writing style"""

    def __init__(self):
        self.formal_prompt = self._load_prompt('prompts/formal_system_prompt.txt')
        self.informal_prompt = self._load_prompt('prompts/informal_system_prompt.txt')

    def _load_prompt(self, filepath: str) -> Optional[str]:
        """Load a system prompt from file"""
        path = Path(filepath)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def compose_with_openai(self, context: str, tone: str = 'formal', api_key: Optional[str] = None):
        """Compose email using OpenAI API"""
        try:
            import openai
        except ImportError:
            print("Error: openai package not installed. Run: pip install openai")
            return None

        if not api_key:
            api_key = input("Enter your OpenAI API key (or set OPENAI_API_KEY env var): ")

        openai.api_key = api_key

        system_prompt = self.formal_prompt if tone == 'formal' else self.informal_prompt

        if not system_prompt:
            print(f"Error: {tone} prompt not found. Run the pipeline first!")
            return None

        print(f"\nGenerating {tone} email using OpenAI...")

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
            print(f"Error calling OpenAI: {e}")
            return None

    def compose_with_anthropic(self, context: str, tone: str = 'formal', api_key: Optional[str] = None):
        """Compose email using Anthropic Claude API"""
        try:
            import anthropic
        except ImportError:
            print("Error: anthropic package not installed. Run: pip install anthropic")
            return None

        if not api_key:
            api_key = input("Enter your Anthropic API key (or set ANTHROPIC_API_KEY env var): ")

        system_prompt = self.formal_prompt if tone == 'formal' else self.informal_prompt

        if not system_prompt:
            print(f"Error: {tone} prompt not found. Run the pipeline first!")
            return None

        print(f"\nGenerating {tone} email using Claude...")

        try:
            client = anthropic.Anthropic(api_key=api_key)

            message = client.messages.create(
                model="claude-3-5-sonnet-20241022",
                max_tokens=1024,
                system=system_prompt,
                messages=[
                    {
                        "role": "user",
                        "content": f"Write an email: {context}"
                    }
                ]
            )

            return message.content[0].text
        except Exception as e:
            print(f"Error calling Anthropic: {e}")
            return None

    def interactive_mode(self):
        """Interactive mode for composing emails"""
        print("="*60)
        print("INTERACTIVE EMAIL COMPOSER")
        print("="*60)

        # Check if prompts exist
        if not self.formal_prompt and not self.informal_prompt:
            print("\nError: No training prompts found!")
            print("Please run the pipeline first: python run_pipeline.py /path/to/emails")
            return

        while True:
            print("\n" + "-"*60)
            print("What would you like to write?")
            print("1. Formal email")
            print("2. Informal email")
            print("3. Exit")
            print("-"*60)

            choice = input("\nChoice (1-3): ").strip()

            if choice == '3':
                print("Goodbye!")
                break

            if choice not in ['1', '2']:
                print("Invalid choice!")
                continue

            tone = 'formal' if choice == '1' else 'informal'

            # Get email context
            print(f"\n📝 Describe the email you want to write:")
            print("   (e.g., 'Request a meeting with the client about the project update')")
            context = input("\n> ").strip()

            if not context:
                print("Context cannot be empty!")
                continue

            # Choose AI provider
            print("\nChoose AI provider:")
            print("1. OpenAI (GPT-4)")
            print("2. Anthropic (Claude)")
            print("3. Show prompt only (no API call)")

            provider = input("\nChoice (1-3): ").strip()

            if provider == '1':
                # Get API key from environment or user
                import os
                api_key = os.getenv('OPENAI_API_KEY')
                email = self.compose_with_openai(context, tone, api_key)

            elif provider == '2':
                import os
                api_key = os.getenv('ANTHROPIC_API_KEY')
                email = self.compose_with_anthropic(context, tone, api_key)

            elif provider == '3':
                # Just show the prompt
                system_prompt = self.formal_prompt if tone == 'formal' else self.informal_prompt
                print("\n" + "="*60)
                print(f"SYSTEM PROMPT ({tone.upper()})")
                print("="*60)
                print(system_prompt)
                print("\n" + "="*60)
                print("USER PROMPT")
                print("="*60)
                print(f"Write an email: {context}")
                print("\n💡 Copy the above prompts to ChatGPT, Claude, or any AI assistant")
                continue

            else:
                print("Invalid choice!")
                continue

            if email:
                print("\n" + "="*60)
                print("GENERATED EMAIL")
                print("="*60)
                print(email)
                print("="*60)

                # Option to copy or save
                save = input("\nSave to file? (y/n): ").strip().lower()
                if save == 'y':
                    filename = input("Filename (e.g., draft_email.txt): ").strip()
                    if filename:
                        with open(filename, 'w', encoding='utf-8') as f:
                            f.write(email)
                        print(f"✓ Saved to {filename}")


def main():
    """Main entry point"""
    import argparse
    import os

    parser = argparse.ArgumentParser(
        description='Compose emails in your writing style using AI',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Interactive mode
  python email_composer.py

  # Quick compose with OpenAI
  python email_composer.py --provider openai --tone formal --context "Request meeting about Q4 goals"

  # Quick compose with Claude
  python email_composer.py --provider anthropic --tone informal --context "Invite team to lunch"

Environment Variables:
  OPENAI_API_KEY      - Your OpenAI API key
  ANTHROPIC_API_KEY   - Your Anthropic API key
        """
    )
    parser.add_argument('--provider', choices=['openai', 'anthropic'],
                       help='AI provider to use')
    parser.add_argument('--tone', choices=['formal', 'informal'], default='formal',
                       help='Email tone (default: formal)')
    parser.add_argument('--context', help='Email context/description')
    parser.add_argument('--api-key', help='API key for the provider')

    args = parser.parse_args()

    composer = EmailComposer()

    # If context provided, run in direct mode
    if args.context and args.provider:
        if args.provider == 'openai':
            api_key = args.api_key or os.getenv('OPENAI_API_KEY')
            email = composer.compose_with_openai(args.context, args.tone, api_key)
        else:
            api_key = args.api_key or os.getenv('ANTHROPIC_API_KEY')
            email = composer.compose_with_anthropic(args.context, args.tone, api_key)

        if email:
            print(email)
    else:
        # Interactive mode
        composer.interactive_mode()


if __name__ == '__main__':
    main()
