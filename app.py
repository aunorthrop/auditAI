from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from auditor.analyzer import CodeAuditor

load_dotenv()
app = Flask(__name__)
auditor = CodeAuditor(os.getenv('OPENAI_API_KEY'))

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        data = request.json
        prompt = data.get('prompt', '')
        code = data.get('code', '')
        platform = data.get('platform', 'unknown')
        
        if not prompt or not code:
            return jsonify({'error': 'Both prompt and code are required'}), 400
        
        result = auditor.audit_code(prompt, code, platform)
        return jsonify(result)
    
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port, debug=True)
