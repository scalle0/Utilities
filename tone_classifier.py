#!/usr/bin/env python3
"""
Tone Classifier - Classify emails as formal or informal
"""

import json
import re
from pathlib import Path
from typing import Dict, List, Tuple
import numpy as np


class ToneClassifier:
    """Classify emails based on formal vs informal tone"""

    def __init__(self):
        # Informal indicators
        self.informal_patterns = [
            r'\b(gonna|wanna|gotta|kinda|sorta)\b',
            r'\b(yeah|yep|nope|nah|hey|hi|yo)\b',
            r'\b(lol|btw|fyi|asap|omg|tbh)\b',
            r'[!]{2,}',  # Multiple exclamation marks
            r'[?]{2,}',  # Multiple question marks
            r':\)|:\(|:D|;-?\)',  # Emoticons
            r'\b(cool|awesome|great|nice)\b',
            r'\b(thanks|thx|ty)\b',
            r'\.{3,}',  # Ellipsis
        ]

        # Formal indicators
        self.formal_patterns = [
            r'\b(sincerely|regards|respectfully|cordially)\b',
            r'\b(please find attached|kindly|hereby|furthermore|moreover|therefore)\b',
            r'\b(pursuant to|in accordance with|with respect to)\b',
            r'\b(I am writing to|I would like to|please be advised)\b',
            r'\b(dear sir|dear madam|to whom it may concern)\b',
            r'\b(appreciate|grateful|acknowledge|confirm)\b',
        ]

        # Additional features
        self.contractions = [
            r"won't", r"can't", r"shouldn't", r"wouldn't",
            r"didn't", r"doesn't", r"isn't", r"aren't",
            r"haven't", r"hasn't", r"I'm", r"you're",
            r"we're", r"they're", r"it's", r"that's"
        ]

    def analyze_text_features(self, text: str) -> Dict:
        """Analyze various linguistic features of the text"""
        text_lower = text.lower()

        # Count informal patterns
        informal_count = sum(
            len(re.findall(pattern, text_lower, re.IGNORECASE))
            for pattern in self.informal_patterns
        )

        # Count formal patterns
        formal_count = sum(
            len(re.findall(pattern, text_lower, re.IGNORECASE))
            for pattern in self.formal_patterns
        )

        # Count contractions (informal)
        contraction_count = sum(
            len(re.findall(pattern, text, re.IGNORECASE))
            for pattern in self.contractions
        )

        # Sentence length analysis
        sentences = re.split(r'[.!?]+', text)
        sentences = [s.strip() for s in sentences if s.strip()]

        avg_sentence_length = np.mean([len(s.split()) for s in sentences]) if sentences else 0

        # Word length analysis
        words = text.split()
        avg_word_length = np.mean([len(w) for w in words]) if words else 0

        # Exclamation usage
        exclamation_count = text.count('!')

        return {
            'informal_markers': informal_count,
            'formal_markers': formal_count,
            'contractions': contraction_count,
            'avg_sentence_length': avg_sentence_length,
            'avg_word_length': avg_word_length,
            'exclamations': exclamation_count,
            'total_words': len(words),
        }

    def classify_tone(self, text: str) -> Tuple[str, float, Dict]:
        """
        Classify the tone of the text as formal or informal

        Returns:
            (classification, confidence, features)
        """
        features = self.analyze_text_features(text)

        # Scoring system
        informal_score = 0
        formal_score = 0

        # Informal indicators
        informal_score += features['informal_markers'] * 3
        informal_score += features['contractions'] * 1
        informal_score += features['exclamations'] * 0.5

        # Short sentences can be informal
        if features['avg_sentence_length'] < 10:
            informal_score += 2

        # Short words can be informal
        if features['avg_word_length'] < 4.5:
            informal_score += 1

        # Formal indicators
        formal_score += features['formal_markers'] * 3

        # Long sentences tend to be formal
        if features['avg_sentence_length'] > 20:
            formal_score += 2

        # Longer words tend to be formal
        if features['avg_word_length'] > 5.5:
            formal_score += 1

        # Determine classification
        total_score = informal_score + formal_score

        if total_score == 0:
            classification = "neutral"
            confidence = 0.5
        elif informal_score > formal_score:
            classification = "informal"
            confidence = min(informal_score / (total_score + 1), 0.95)
        else:
            classification = "formal"
            confidence = min(formal_score / (total_score + 1), 0.95)

        return classification, confidence, features

    def classify_emails(self, emails: List[Dict]) -> List[Dict]:
        """Classify a list of emails"""
        classified = []

        for email in emails:
            tone, confidence, features = self.classify_tone(email['clean_text'])

            classified_email = email.copy()
            classified_email['tone'] = tone
            classified_email['tone_confidence'] = confidence
            classified_email['tone_features'] = features

            classified.append(classified_email)

        return classified

    def save_classified_emails(self, emails: List[Dict], output_file: str = 'classified_emails.json'):
        """Save classified emails to JSON"""
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(emails, f, indent=2, ensure_ascii=False)

        print(f"Saved {len(emails)} classified emails to {output_file}")

    def create_training_sets(self, emails: List[Dict], output_dir: str = 'training_data'):
        """Create separate training sets for formal and informal emails"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        formal_emails = [e for e in emails if e['tone'] == 'formal']
        informal_emails = [e for e in emails if e['tone'] == 'informal']
        neutral_emails = [e for e in emails if e['tone'] == 'neutral']

        # Save formal emails
        with open(output_path / 'formal_emails.txt', 'w', encoding='utf-8') as f:
            for i, email in enumerate(formal_emails):
                f.write(f"=== Formal Email {i+1} ===\n")
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"Confidence: {email['tone_confidence']:.2f}\n\n")
                f.write(f"{email['clean_text']}\n")
                f.write("\n" + "="*50 + "\n\n")

        # Save informal emails
        with open(output_path / 'informal_emails.txt', 'w', encoding='utf-8') as f:
            for i, email in enumerate(informal_emails):
                f.write(f"=== Informal Email {i+1} ===\n")
                f.write(f"Subject: {email['subject']}\n")
                f.write(f"Confidence: {email['tone_confidence']:.2f}\n\n")
                f.write(f"{email['clean_text']}\n")
                f.write("\n" + "="*50 + "\n\n")

        # Save neutral emails
        with open(output_path / 'neutral_emails.txt', 'w', encoding='utf-8') as f:
            for i, email in enumerate(neutral_emails):
                f.write(f"=== Neutral Email {i+1} ===\n")
                f.write(f"Subject: {email['subject']}\n\n")
                f.write(f"{email['clean_text']}\n")
                f.write("\n" + "="*50 + "\n\n")

        print(f"\n=== Training Data Created ===")
        print(f"Formal emails: {len(formal_emails)} -> {output_path / 'formal_emails.txt'}")
        print(f"Informal emails: {len(informal_emails)} -> {output_path / 'informal_emails.txt'}")
        print(f"Neutral emails: {len(neutral_emails)} -> {output_path / 'neutral_emails.txt'}")

        # Save summary statistics
        stats = {
            'formal_count': len(formal_emails),
            'informal_count': len(informal_emails),
            'neutral_count': len(neutral_emails),
            'total_count': len(emails),
        }

        with open(output_path / 'statistics.json', 'w', encoding='utf-8') as f:
            json.dump(stats, f, indent=2)

        return stats


def main():
    """Main function for command-line usage"""
    import argparse

    parser = argparse.ArgumentParser(description='Classify email tone')
    parser.add_argument('input_json', help='Input JSON file from email_extractor.py')
    parser.add_argument('--output-dir', default='training_data',
                       help='Output directory for training data')

    args = parser.parse_args()

    # Load emails
    with open(args.input_json, 'r', encoding='utf-8') as f:
        emails = json.load(f)

    # Classify emails
    classifier = ToneClassifier()
    classified = classifier.classify_emails(emails)

    # Save results
    classifier.save_classified_emails(classified)
    stats = classifier.create_training_sets(classified, args.output_dir)

    print(f"\nTotal emails processed: {len(emails)}")


if __name__ == '__main__':
    main()
