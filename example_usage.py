#!/usr/bin/env python3
"""
Example: How to use the trained prompts with AI APIs
"""

# Example 1: Using with OpenAI (GPT-4)
def example_openai():
    """
    Example of using the generated prompts with OpenAI's API
    Uncomment and add your API key to use
    """
    # import openai
    #
    # # Set your API key
    # openai.api_key = "your-api-key-here"
    #
    # # Load the formal system prompt
    # with open('prompts/formal_system_prompt.txt', 'r', encoding='utf-8') as f:
    #     system_prompt = f.read()
    #
    # # Create a completion
    # response = openai.ChatCompletion.create(
    #     model="gpt-4",
    #     messages=[
    #         {"role": "system", "content": system_prompt},
    #         {"role": "user", "content": "Write an email requesting a project status update from the team"}
    #     ],
    #     temperature=0.7,
    #     max_tokens=500
    # )
    #
    # print("Generated Email:")
    # print(response.choices[0].message.content)

    print("See code above for OpenAI example")


# Example 2: Using with Anthropic Claude
def example_anthropic():
    """
    Example of using the generated prompts with Anthropic's Claude API
    Uncomment and add your API key to use
    """
    # import anthropic
    #
    # # Load the informal system prompt
    # with open('prompts/informal_system_prompt.txt', 'r', encoding='utf-8') as f:
    #     system_prompt = f.read()
    #
    # # Create client
    # client = anthropic.Anthropic(api_key="your-api-key-here")
    #
    # # Create a message
    # message = client.messages.create(
    #     model="claude-3-5-sonnet-20241022",
    #     max_tokens=1024,
    #     system=system_prompt,
    #     messages=[
    #         {
    #             "role": "user",
    #             "content": "Write a casual email to invite colleagues to a team lunch"
    #         }
    #     ]
    # )
    #
    # print("Generated Email:")
    # print(message.content[0].text)

    print("See code above for Anthropic Claude example")


# Example 3: Using locally without API (using the prompts as templates)
def example_local():
    """
    Example of using the training data locally without API calls
    """
    from pathlib import Path

    # Check if prompts exist
    if not Path('prompts/formal_system_prompt.txt').exists():
        print("Error: Run the pipeline first to generate prompts!")
        return

    # Load formal prompt
    with open('prompts/formal_system_prompt.txt', 'r', encoding='utf-8') as f:
        formal_prompt = f.read()

    print("="*60)
    print("FORMAL EMAIL STYLE GUIDE")
    print("="*60)
    print(formal_prompt[:500])  # Show first 500 chars
    print("\n... (truncated)")

    # Load informal prompt
    with open('prompts/informal_system_prompt.txt', 'r', encoding='utf-8') as f:
        informal_prompt = f.read()

    print("\n" + "="*60)
    print("INFORMAL EMAIL STYLE GUIDE")
    print("="*60)
    print(informal_prompt[:500])  # Show first 500 chars
    print("\n... (truncated)")


# Example 4: Simple template-based approach
def example_template():
    """
    Simple template approach using your writing samples
    """
    import json
    from pathlib import Path

    if not Path('classified_emails.json').exists():
        print("Error: Run the pipeline first!")
        return

    # Load classified emails
    with open('classified_emails.json', 'r', encoding='utf-8') as f:
        emails = json.load(f)

    # Get formal emails
    formal_emails = [e for e in emails if e['tone'] == 'formal']

    if formal_emails:
        print("Example of your formal writing style:")
        print("="*60)
        print(f"Subject: {formal_emails[0]['subject']}")
        print("-"*60)
        print(formal_emails[0]['clean_text'][:300])
        print("\n... (use this as a template for formal emails)")


if __name__ == '__main__':
    import sys

    print("Email Tone Training - Usage Examples")
    print("="*60)

    if len(sys.argv) > 1:
        mode = sys.argv[1]
        if mode == 'openai':
            example_openai()
        elif mode == 'anthropic':
            example_anthropic()
        elif mode == 'template':
            example_template()
        else:
            example_local()
    else:
        print("\nUsage:")
        print("  python example_usage.py openai     # Show OpenAI example")
        print("  python example_usage.py anthropic  # Show Anthropic example")
        print("  python example_usage.py template   # Show template example")
        print("  python example_usage.py            # Show local prompts")
        print("\nRunning local example by default...\n")
        example_local()
