#!/usr/bin/env python3
"""
Email Extractor - Extract and parse sent emails from .eml files
"""

import email
import re
import os
from pathlib import Path
from email.parser import Parser
from email.policy import default
from typing import List, Dict, Optional
import json


class EmailExtractor:
    """Extract and clean email content from .eml files"""

    def __init__(self, eml_folder: str):
        self.eml_folder = Path(eml_folder)
        self.emails = []

    def parse_eml_file(self, filepath: Path) -> Optional[Dict]:
        """Parse a single .eml file and extract relevant information"""
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                msg = email.message_from_file(f, policy=default)

            # Extract basic metadata
            email_data = {
                'filepath': str(filepath),
                'from': msg.get('From', ''),
                'to': msg.get('To', ''),
                'subject': msg.get('Subject', ''),
                'date': msg.get('Date', ''),
                'body': self._extract_body(msg),
                'clean_text': '',  # Will be filled after cleaning
            }

            return email_data

        except Exception as e:
            print(f"Error parsing {filepath}: {e}")
            return None

    def _extract_body(self, msg) -> str:
        """Extract the body text from an email message"""
        body = ""

        if msg.is_multipart():
            for part in msg.walk():
                content_type = part.get_content_type()
                content_disposition = str(part.get("Content-Disposition"))

                # Skip attachments
                if "attachment" in content_disposition:
                    continue

                # Get text/plain parts
                if content_type == "text/plain":
                    try:
                        body = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        break
                    except:
                        pass

                # Fallback to HTML if no plain text
                elif content_type == "text/html" and not body:
                    try:
                        html_content = part.get_payload(decode=True).decode('utf-8', errors='ignore')
                        # Basic HTML tag removal
                        body = re.sub(r'<[^>]+>', '', html_content)
                    except:
                        pass
        else:
            try:
                body = msg.get_payload(decode=True).decode('utf-8', errors='ignore')
            except:
                body = str(msg.get_payload())

        return body

    def clean_email_text(self, body: str) -> str:
        """
        Clean email body to extract only the user's written text.
        Removes:
        - Quoted replies (lines starting with >)
        - Email signatures
        - Forwarded message headers
        - Reply headers
        - Disclaimers
        """
        lines = body.split('\n')
        cleaned_lines = []

        # Patterns to detect quoted text and common email artifacts
        quote_patterns = [
            r'^>+\s',  # Lines starting with >
            r'^On .* wrote:',  # "On [date] [person] wrote:"
            r'^From:.*',  # Forwarded message headers
            r'^Sent:.*',
            r'^To:.*',
            r'^Subject:.*',
            r'^Date:.*',
            r'^-----Original Message-----',
            r'^________________________________',  # Outlook separator
            r'^-{3,}',  # Multiple dashes (often signature separator)
        ]

        in_signature = False
        in_quote = False

        for line in lines:
            stripped = line.strip()

            # Check if we hit a signature separator
            if re.match(r'^--\s*$', stripped) or re.match(r'^-{3,}$', stripped):
                in_signature = True
                continue

            # Check if line is quoted or part of reply/forward
            is_quoted = any(re.match(pattern, stripped) for pattern in quote_patterns)

            if is_quoted:
                in_quote = True
                continue

            # If we're in signature or quote section, skip
            if in_signature or in_quote:
                # Check if we've exited the quote section (new paragraph)
                if stripped and not is_quoted:
                    in_quote = False
                else:
                    continue

            # Keep non-empty lines that aren't quoted
            if stripped:
                cleaned_lines.append(line)

        # Join and clean up excessive whitespace
        cleaned_text = '\n'.join(cleaned_lines)
        cleaned_text = re.sub(r'\n{3,}', '\n\n', cleaned_text)  # Max 2 newlines

        return cleaned_text.strip()

    def extract_all_emails(self) -> List[Dict]:
        """Extract all .eml files from the specified folder"""
        if not self.eml_folder.exists():
            print(f"Error: Folder {self.eml_folder} does not exist")
            return []

        eml_files = list(self.eml_folder.glob('**/*.eml'))
        print(f"Found {len(eml_files)} .eml files")

        for eml_file in eml_files:
            email_data = self.parse_eml_file(eml_file)
            if email_data:
                # Clean the email body
                email_data['clean_text'] = self.clean_email_text(email_data['body'])

                # Only include emails with substantial content
                if len(email_data['clean_text']) > 50:
                    self.emails.append(email_data)

        print(f"Successfully extracted {len(self.emails)} emails with content")
        return self.emails

    def save_to_json(self, output_file: str = 'extracted_emails.json'):
        """Save extracted emails to JSON file"""
        output_path = Path(output_file)

        with open(output_path, 'w', encoding='utf-8') as f:
            json.dump(self.emails, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(self.emails)} emails to {output_path}")

    def save_clean_text(self, output_file: str = 'my_writing.txt'):
        """Save only the clean text to a text file for training"""
        output_path = Path(output_file)

        with open(output_path, 'w', encoding='utf-8') as f:
            for i, email_data in enumerate(self.emails):
                f.write(f"=== Email {i+1} ===\n")
                f.write(f"Subject: {email_data['subject']}\n")
                f.write(f"Date: {email_data['date']}\n")
                f.write(f"\n{email_data['clean_text']}\n")
                f.write("\n" + "="*50 + "\n\n")

        print(f"Saved clean text to {output_path}")

    def get_statistics(self) -> Dict:
        """Get statistics about extracted emails"""
        if not self.emails:
            return {}

        total_chars = sum(len(e['clean_text']) for e in self.emails)
        total_words = sum(len(e['clean_text'].split()) for e in self.emails)

        return {
            'total_emails': len(self.emails),
            'total_characters': total_chars,
            'total_words': total_words,
            'avg_words_per_email': total_words / len(self.emails) if self.emails else 0,
        }


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Extract text from .eml files')
    parser.add_argument('eml_folder', help='Folder containing .eml files')
    parser.add_argument('--output-json', default='extracted_emails.json',
                       help='Output JSON file (default: extracted_emails.json)')
    parser.add_argument('--output-text', default='my_writing.txt',
                       help='Output text file (default: my_writing.txt)')

    args = parser.parse_args()

    # Extract emails
    extractor = EmailExtractor(args.eml_folder)
    extractor.extract_all_emails()

    # Save results
    extractor.save_to_json(args.output_json)
    extractor.save_clean_text(args.output_text)

    # Print statistics
    stats = extractor.get_statistics()
    print("\n=== Statistics ===")
    for key, value in stats.items():
        print(f"{key}: {value}")


if __name__ == '__main__':
    main()
