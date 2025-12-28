#!/usr/bin/env python3
"""
Train Agent - Prepare training data and create prompts for AI agent
"""

import json
from pathlib import Path
from typing import Dict, List
import random


class AgentTrainer:
    """Prepare training data and create prompts for tone-matching agent"""

    def __init__(self, training_data_dir: str = 'training_data'):
        self.training_dir = Path(training_data_dir)
        self.formal_examples = []
        self.informal_examples = []

    def load_training_data(self):
        """Load formal and informal training examples"""
        # Load classified emails
        classified_file = 'classified_emails.json'
        if Path(classified_file).exists():
            with open(classified_file, 'r', encoding='utf-8') as f:
                emails = json.load(f)

            self.formal_examples = [
                e for e in emails
                if e['tone'] == 'formal' and e['tone_confidence'] > 0.6
            ]
            self.informal_examples = [
                e for e in emails
                if e['tone'] == 'informal' and e['tone_confidence'] > 0.6
            ]

            print(f"Loaded {len(self.formal_examples)} formal examples")
            print(f"Loaded {len(self.informal_examples)} informal examples")

    def create_system_prompt(self, tone: str = 'formal') -> str:
        """Create a system prompt for the AI agent based on writing style"""

        if tone == 'formal':
            examples = self.formal_examples[:5]  # Use top 5 examples
            tone_description = "formal, professional, and polished"
            style_notes = """
- Use complete sentences and proper grammar
- Avoid contractions and colloquialisms
- Maintain a professional and respectful tone
- Use sophisticated vocabulary when appropriate
- Structure emails with clear paragraphs
"""
        else:
            examples = self.informal_examples[:5]
            tone_description = "casual, friendly, and conversational"
            style_notes = """
- Use a relaxed, conversational tone
- Contractions and casual language are fine
- Keep it brief and to the point
- Feel free to use casual expressions
- Maintain a warm and approachable tone
"""

        prompt = f"""You are an email writing assistant trained to match a specific writing style.

WRITING STYLE: {tone_description}

STYLE GUIDELINES:
{style_notes}

EXAMPLE EMAILS FROM THE USER:
"""

        for i, example in enumerate(examples, 1):
            prompt += f"\n--- Example {i} ---\n"
            prompt += f"Subject: {example.get('subject', 'N/A')}\n"
            prompt += f"{example['clean_text'][:500]}...\n"  # Truncate long examples

        prompt += """

When writing emails, carefully mimic the user's:
1. Sentence structure and length
2. Vocabulary choices
3. Greeting and closing styles
4. Level of formality
5. Use of punctuation and emphasis

Always maintain the authentic voice demonstrated in these examples.
"""

        return prompt

    def create_few_shot_examples(self, tone: str = 'formal', num_examples: int = 3) -> List[Dict]:
        """Create few-shot examples for prompting"""

        examples = self.formal_examples if tone == 'formal' else self.informal_examples

        if len(examples) < num_examples:
            num_examples = len(examples)

        selected = random.sample(examples, num_examples)

        few_shot = []
        for example in selected:
            few_shot.append({
                'subject': example.get('subject', ''),
                'content': example['clean_text'][:300],  # Truncate for prompt
            })

        return few_shot

    def generate_training_prompt(self, context: str, tone: str = 'formal') -> str:
        """Generate a complete prompt for the agent to write an email"""

        system_prompt = self.create_system_prompt(tone)
        few_shot = self.create_few_shot_examples(tone, num_examples=2)

        user_prompt = f"""
{system_prompt}

NOW, please write an email in this same style for the following context:

{context}

Remember to match the tone, style, and voice from the examples above.
"""

        return user_prompt

    def save_prompts(self, output_dir: str = 'prompts'):
        """Save generated prompts for different tones"""
        output_path = Path(output_dir)
        output_path.mkdir(exist_ok=True)

        # Create formal prompt
        formal_prompt = self.create_system_prompt('formal')
        with open(output_path / 'formal_system_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(formal_prompt)

        # Create informal prompt
        informal_prompt = self.create_system_prompt('informal')
        with open(output_path / 'informal_system_prompt.txt', 'w', encoding='utf-8') as f:
            f.write(informal_prompt)

        print(f"\nSaved system prompts to {output_path}/")

        # Create example usage
        example_usage = """
# How to Use These Prompts

## For Formal Emails:
1. Load the system prompt from 'formal_system_prompt.txt'
2. Add your context (e.g., "Write an email to request a meeting with the client")
3. Pass to your AI agent (ChatGPT, Claude, etc.)

## For Informal Emails:
1. Load the system prompt from 'informal_system_prompt.txt'
2. Add your context (e.g., "Write an email to invite friends to a party")
3. Pass to your AI agent

## Example with Python and OpenAI API:
```python
import openai

# Load the system prompt
with open('prompts/formal_system_prompt.txt', 'r') as f:
    system_prompt = f.read()

# Create a completion
response = openai.ChatCompletion.create(
    model="gpt-4",
    messages=[
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": "Write an email requesting a project update"}
    ]
)

print(response.choices[0].message.content)
```

## Example with Anthropic Claude API:
```python
import anthropic

# Load the system prompt
with open('prompts/informal_system_prompt.txt', 'r') as f:
    system_prompt = f.read()

client = anthropic.Anthropic(api_key="your-api-key")

message = client.messages.create(
    model="claude-3-5-sonnet-20241022",
    max_tokens=1024,
    system=system_prompt,
    messages=[
        {"role": "user", "content": "Write an email to catch up with an old friend"}
    ]
)

print(message.content)
```
"""

        with open(output_path / 'USAGE.md', 'w', encoding='utf-8') as f:
            f.write(example_usage)

        print(f"Saved usage instructions to {output_path}/USAGE.md")


def main():
    """Main function"""
    import argparse

    parser = argparse.ArgumentParser(description='Create training prompts for email agent')
    parser.add_argument('--training-dir', default='training_data',
                       help='Directory with training data')
    parser.add_argument('--output-dir', default='prompts',
                       help='Output directory for prompts')

    args = parser.parse_args()

    trainer = AgentTrainer(args.training_dir)
    trainer.load_training_data()
    trainer.save_prompts(args.output_dir)

    print("\n=== Training Complete ===")
    print("You can now use the generated prompts with any AI model!")


if __name__ == '__main__':
    main()
