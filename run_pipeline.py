#!/usr/bin/env python3
"""
Complete Pipeline - Run all steps to extract, classify, and prepare training data
"""

import sys
from pathlib import Path
from email_extractor import EmailExtractor
from tone_classifier import ToneClassifier
from train_agent import AgentTrainer


def run_complete_pipeline(eml_folder: str):
    """
    Run the complete pipeline:
    1. Extract emails from .eml files
    2. Classify them as formal/informal
    3. Create training prompts
    """

    print("="*60)
    print("EMAIL TONE EXTRACTION & TRAINING PIPELINE")
    print("="*60)

    # Step 1: Extract emails
    print("\n[Step 1/3] Extracting emails from .eml files...")
    print("-" * 60)
    extractor = EmailExtractor(eml_folder)
    emails = extractor.extract_all_emails()

    if not emails:
        print("Error: No emails were extracted. Please check the folder path.")
        return

    extractor.save_to_json('extracted_emails.json')
    extractor.save_clean_text('my_writing.txt')

    stats = extractor.get_statistics()
    print(f"\nExtracted {stats['total_emails']} emails")
    print(f"Total words: {stats['total_words']}")
    print(f"Average words per email: {stats['avg_words_per_email']:.1f}")

    # Step 2: Classify tone
    print("\n[Step 2/3] Classifying email tones...")
    print("-" * 60)
    classifier = ToneClassifier()
    classified = classifier.classify_emails(emails)

    classifier.save_classified_emails(classified, 'classified_emails.json')
    tone_stats = classifier.create_training_sets(classified, 'training_data')

    # Step 3: Create training prompts
    print("\n[Step 3/3] Creating training prompts...")
    print("-" * 60)
    trainer = AgentTrainer('training_data')
    trainer.load_training_data()
    trainer.save_prompts('prompts')

    # Final summary
    print("\n" + "="*60)
    print("PIPELINE COMPLETE!")
    print("="*60)
    print(f"\n📊 Summary:")
    print(f"  - Total emails: {tone_stats['total_count']}")
    print(f"  - Formal emails: {tone_stats['formal_count']}")
    print(f"  - Informal emails: {tone_stats['informal_count']}")
    print(f"  - Neutral emails: {tone_stats['neutral_count']}")

    print(f"\n📁 Generated Files:")
    print(f"  - extracted_emails.json (raw extracted data)")
    print(f"  - my_writing.txt (all your writing)")
    print(f"  - classified_emails.json (classified data)")
    print(f"  - training_data/ (separated by tone)")
    print(f"  - prompts/ (AI agent prompts)")

    print(f"\n🚀 Next Steps:")
    print(f"  1. Review the training_data/ folder to verify classification")
    print(f"  2. Check prompts/USAGE.md for how to use the generated prompts")
    print(f"  3. Use the system prompts with your preferred AI model (GPT-4, Claude, etc.)")

    print("\n" + "="*60)


def main():
    """Main entry point"""
    import argparse

    parser = argparse.ArgumentParser(
        description='Complete pipeline for email tone extraction and training',
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_pipeline.py /path/to/emails
  python run_pipeline.py ./my_emails
  python run_pipeline.py ~/Documents/Emails
        """
    )
    parser.add_argument('eml_folder', help='Folder containing .eml files')

    args = parser.parse_args()

    # Validate folder exists
    if not Path(args.eml_folder).exists():
        print(f"Error: Folder '{args.eml_folder}' does not exist")
        sys.exit(1)

    run_complete_pipeline(args.eml_folder)


if __name__ == '__main__':
    main()
