import os
# Clear proxy variables before importing OpenAI
for var in ['HTTP_PROXY', 'HTTPS_PROXY', 'http_proxy', 'https_proxy']:
    if var in os.environ:
        del os.environ[var]
from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Try to initialize auditor, but don't fail if it doesn't work
auditor = None
try:
    from auditor.analyzer import CodeAuditor
    auditor = CodeAuditor(os.getenv('OPENAI_API_KEY'))
    print("✅ CodeAuditor initialized successfully")
except Exception as e:
    print(f"⚠️  Failed to initialize CodeAuditor: {e}")

@app.route('/')
def index():
    try:
        return render_template('index.html')
    except Exception as e:
        return f"<h1>AuditAI</h1><p>App is running but template not found: {e}</p>"

@app.route('/health')
def health():
    """Health check endpoint"""
    return jsonify({
        'status': 'healthy',
        'auditor_available': auditor is not None,
        'openai_key_present': bool(os.getenv('OPENAI_API_KEY'))
    })

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        if not auditor:
            return jsonify({
                'error': 'Code auditor is not available. Check server logs for details.'
            }), 500
        
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        code = data.get('code', '')
        platform = data.get('platform', 'unknown')
        
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        # Call the audit_code method
        result = auditor.audit_code(code, platform)
        
        # Convert AuditResult to dictionary
        result_dict = {
            'efficiency_score': result.efficiency_score,
            'complexity_score': result.complexity_score,
            'bug_count': result.bug_count,
            'optimization_suggestions': result.optimization_suggestions,
            'cost_analysis': result.cost_analysis,
            'red_flags': result.red_flags,
            'summary': result.summary
        }
        
        return jsonify(result_dict)
    
    except Exception as e:
        return jsonify({'error': f'Analysis failed: {str(e)}'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
