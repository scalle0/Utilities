#!/usr/bin/env python3
"""
Web Service - Simple web API for email composition
Deploy as a microservice that your email client can call
"""

import os
from pathlib import Path
from typing import Optional

try:
    from flask import Flask, request, jsonify
    from flask_cors import CORS
    FLASK_AVAILABLE = True
except ImportError:
    FLASK_AVAILABLE = False


app = Flask(__name__)
CORS(app)  # Enable CORS for browser extensions


class EmailAPI:
    """API for email composition"""

    def __init__(self):
        self.formal_prompt = self._load_prompt('prompts/formal_system_prompt.txt')
        self.informal_prompt = self._load_prompt('prompts/informal_system_prompt.txt')

    def _load_prompt(self, filepath: str) -> Optional[str]:
        """Load system prompt"""
        path = Path(filepath)
        if path.exists():
            with open(path, 'r', encoding='utf-8') as f:
                return f.read()
        return None

    def compose(self, context: str, tone: str = 'formal', provider: str = 'anthropic') -> dict:
        """Compose an email"""
        system_prompt = self.formal_prompt if tone == 'formal' else self.informal_prompt

        if not system_prompt:
            return {'error': 'Prompt not found. Run training pipeline first.'}

        # Get API key from environment
        if provider == 'anthropic':
            api_key = os.getenv('ANTHROPIC_API_KEY')
            if not api_key:
                return {'error': 'ANTHROPIC_API_KEY not set'}

            try:
                import anthropic
                client = anthropic.Anthropic(api_key=api_key)
                message = client.messages.create(
                    model="claude-3-5-sonnet-20241022",
                    max_tokens=1024,
                    system=system_prompt,
                    messages=[
                        {"role": "user", "content": f"Write an email: {context}"}
                    ]
                )
                return {'email': message.content[0].text}

            except Exception as e:
                return {'error': str(e)}

        elif provider == 'openai':
            api_key = os.getenv('OPENAI_API_KEY')
            if not api_key:
                return {'error': 'OPENAI_API_KEY not set'}

            try:
                import openai
                openai.api_key = api_key
                response = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": system_prompt},
                        {"role": "user", "content": f"Write an email: {context}"}
                    ],
                    temperature=0.7,
                    max_tokens=800
                )
                return {'email': response.choices[0].message.content}

            except Exception as e:
                return {'error': str(e)}

        else:
            return {'error': f'Unknown provider: {provider}'}


# Initialize API
email_api = EmailAPI()


@app.route('/health', methods=['GET'])
def health():
    """Health check endpoint"""
    return jsonify({'status': 'healthy'})


@app.route('/api/compose', methods=['POST'])
def compose_email():
    """
    Compose an email

    Request body:
    {
        "context": "Request meeting about project",
        "tone": "formal",  // optional, default: "formal"
        "provider": "anthropic"  // optional, default: "anthropic"
    }
    """
    data = request.get_json()

    if not data or 'context' not in data:
        return jsonify({'error': 'Missing required field: context'}), 400

    context = data['context']
    tone = data.get('tone', 'formal')
    provider = data.get('provider', 'anthropic')

    result = email_api.compose(context, tone, provider)

    if 'error' in result:
        return jsonify(result), 500

    return jsonify(result)


@app.route('/api/prompts', methods=['GET'])
def get_prompts():
    """Get available prompts"""
    return jsonify({
        'formal': email_api.formal_prompt is not None,
        'informal': email_api.informal_prompt is not None,
    })


def main():
    """Run the web service"""
    if not FLASK_AVAILABLE:
        print("Error: Flask not installed!")
        print("Install with: pip install flask flask-cors")
        return

    print("="*60)
    print("EMAIL COMPOSITION WEB SERVICE")
    print("="*60)
    print("\n🚀 Starting server on http://localhost:5000")
    print("\nEndpoints:")
    print("  GET  /health          - Health check")
    print("  GET  /api/prompts     - Check available prompts")
    print("  POST /api/compose     - Compose an email")
    print("\nExample request:")
    print("""
  curl -X POST http://localhost:5000/api/compose \\
    -H "Content-Type: application/json" \\
    -d '{
      "context": "Request meeting about Q4 goals",
      "tone": "formal",
      "provider": "anthropic"
    }'
    """)
    print("\n" + "="*60)

    # Run server
    app.run(host='0.0.0.0', port=5000, debug=False)


if __name__ == '__main__':
    main()
