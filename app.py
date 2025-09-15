from flask import Flask, render_template, request, jsonify
import os
from dotenv import load_dotenv
from auditor.analyzer import CodeAuditor

# Load environment variables
load_dotenv()

# Initialize Flask app
app = Flask(__name__)

# Initialize auditor with error handling
try:
    auditor = CodeAuditor(os.getenv('OPENAI_API_KEY'))
except Exception as e:
    print(f"Warning: Failed to initialize CodeAuditor: {e}")
    auditor = None

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/analyze', methods=['POST'])
def analyze():
    try:
        # Check if auditor is available
        if not auditor:
            return jsonify({'error': 'Code auditor is not available. Please check your API key configuration.'}), 500
        
        data = request.json
        if not data:
            return jsonify({'error': 'No JSON data provided'}), 400
            
        code = data.get('code', '')
        platform = data.get('platform', 'unknown')
        
        # Note: Your original code had 'prompt' but your analyzer expects 'code' first
        if not code:
            return jsonify({'error': 'Code is required'}), 400
        
        # Call the audit_code method with correct parameters
        result = auditor.audit_code(code, platform)
        
        # Convert AuditResult to dictionary for JSON serialization
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

@app.route('/health')
def health():
    """Health check endpoint for Railway"""
    return jsonify({'status': 'healthy', 'auditor_available': auditor is not None})

# Error handlers
@app.errorhandler(404)
def not_found(error):
    return jsonify({'error': 'Endpoint not found'}), 404

@app.errorhandler(500)
def internal_error(error):
    return jsonify({'error': 'Internal server error'}), 500

if __name__ == '__main__':
    port = int(os.environ.get('PORT', 5000))
    debug_mode = os.environ.get('FLASK_ENV') != 'production'
    app.run(host='0.0.0.0', port=port, debug=debug_mode)
