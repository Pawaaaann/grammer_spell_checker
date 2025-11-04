"""
Flask web application for grammar and spell checking.

Installation:
    pip install flask

Usage:
    python grammar_spell_checker/web_app.py
    Then open: http://localhost:5000
"""

from flask import Flask, render_template, request, jsonify
import sys
from pathlib import Path

# Import from app.py
try:
    from textblob import TextBlob
except ImportError:
    TextBlob = None

try:
    import language_tool_python
except ImportError as e:
    print("Missing dependency: language-tool-python", file=sys.stderr)
    sys.exit(1)


app = Flask(__name__)

# Initialize LanguageTool once (reuse across requests)
_tool_instance = None

def get_language_tool():
    """Get or create LanguageTool instance (singleton pattern)."""
    global _tool_instance
    if _tool_instance is None:
        _tool_instance = language_tool_python.LanguageTool('en-US')
    return _tool_instance


def correct_spelling(text: str) -> str:
    """Correct spelling using TextBlob."""
    if TextBlob is None:
        return text  # Skip if not installed
    return str(TextBlob(text).correct())


def check_grammar_detailed(text: str) -> dict:
    """Check grammar and return detailed results."""
    # Use cached LanguageTool instance
    tool = get_language_tool()
    matches = tool.check(text)
    corrected = language_tool_python.utils.correct(text, matches)
    
    issues = []
    for m in matches:
        issues.append({
            'message': m.message,
            'context': m.context if m.context else '',
            'replacements': m.replacements[:3] if m.replacements else [],
            'offset': m.offset,
            'length': m.errorLength
        })
    
    return {
        'corrected': corrected,
        'issues_count': len(matches),
        'issues': issues
    }


def fix_text_web(text: str) -> dict:
    """Fix text and return detailed results for web interface."""
    original = text
    
    # Step 1: Spelling
    spelled = correct_spelling(original)
    spelling_changed = (original != spelled)
    
    # Step 2: Grammar
    grammar_result = check_grammar_detailed(spelled)
    
    return {
        'original': original,
        'corrected': grammar_result['corrected'],
        'spelling_fixed': spelling_changed,
        'grammar_issues': grammar_result['issues_count'],
        'issues': grammar_result['issues']
    }


@app.route('/')
def index():
    """Serve the main page."""
    return render_template('index.html')


@app.route('/check', methods=['POST'])
def check_text():
    """API endpoint to check text."""
    data = request.get_json()
    text = data.get('text', '').strip()
    
    if not text:
        return jsonify({'error': 'No text provided'}), 400
    
    # Limit text length to prevent timeout
    if len(text) > 5000:
        return jsonify({'error': 'Text too long. Maximum 5000 characters.'}), 400
    
    try:
        print(f"Checking text: {text[:50]}...")  # Debug log
        result = fix_text_web(text)
        print(f"Result: {result['corrected'][:50]}...")  # Debug log
        return jsonify(result)
    except Exception as e:
        print(f"Error: {str(e)}")  # Debug log
        return jsonify({'error': f'Server error: {str(e)}'}), 500


if __name__ == '__main__':
    print("\n🚀 Grammar & Spell Checker Web App")
    print("📝 Open in browser: http://localhost:5000\n")
    app.run(debug=True, port=5000)
