document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('auditForm');
    const analyzeBtn = document.getElementById('analyzeBtn');
    const btnText = document.getElementById('btnText');
    const btnLoader = document.getElementById('btnLoader');
    const resultsSection = document.getElementById('results');
    const errorSection = document.getElementById('error');

    form.addEventListener('submit', async function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        const data = {
            prompt: formData.get('prompt').trim(),
            code: formData.get('code').trim(),
            platform: formData.get('platform')
        };

        if (!data.prompt || !data.code) {
            showError('Please fill in both the prompt and code fields.');
            return;
        }

        // Show loading state
        setLoading(true);
        hideResults();
        hideError();

        try {
            const response = await fetch('/analyze', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
                body: JSON.stringify(data)
            });

            const result = await response.json();

            if (!response.ok) {
                throw new Error(result.error || 'Analysis failed');
            }

            showResults(result);

        } catch (error) {
            console.error('Error:', error);
            showError(error.message || 'An error occurred during analysis. Please try again.');
        } finally {
            setLoading(false);
        }
    });

    function setLoading(loading) {
        if (loading) {
            analyzeBtn.disabled = true;
            btnText.textContent = 'Analyzing...';
            btnLoader.style.display = 'inline-block';
        } else {
            analyzeBtn.disabled = false;
            btnText.textContent = 'Analyze Code';
            btnLoader.style.display = 'none';
        }
    }

    function showResults(result) {
        // Update metrics
        document.getElementById('efficiencyScore').textContent = result.efficiency_score;
        document.getElementById('complexityScore').textContent = result.complexity_score;
        document.getElementById('bugCount').textContent = result.bug_count;

        // Color code the efficiency score
        const efficiencyElement = document.getElementById('efficiencyScore');
        if (result.efficiency_score >= 80) {
            efficiencyElement.style.color = '#10b981';
        } else if (result.efficiency_score >= 60) {
            efficiencyElement.style.color = '#f59e0b';
        } else {
            efficiencyElement.style.color = '#ef4444';
        }

        // Show red flags if any
        const redFlagsSection = document.getElementById('redFlags');
        const redFlagsList = document.getElementById('redFlagsList');
        
        if (result.red_flags && result.red_flags.length > 0) {
            redFlagsList.innerHTML = '';
            result.red_flags.forEach(flag => {
                const li = document.createElement('li');
                li.textContent = flag;
                redFlagsList.appendChild(li);
            });
            redFlagsSection.style.display = 'block';
        } else {
            redFlagsSection.style.display = 'none';
        }

        // Show optimization suggestions
        const suggestionsList = document.getElementById('suggestionsList');
        suggestionsList.innerHTML = '';
        
        if (result.optimization_suggestions && result.optimization_suggestions.length > 0) {
            result.optimization_suggestions.forEach(suggestion => {
                const li = document.createElement('li');
                li.textContent = suggestion;
                suggestionsList.appendChild(li);
            });
        } else {
            const li = document.createElement('li');
            li.textContent = 'No specific optimizations suggested - code looks generally efficient!';
            li.style.color = '#10b981';
            suggestionsList.appendChild(li);
        }

        // Show cost analysis
        const costDetails = document.getElementById('costDetails');
        const cost = result.cost_analysis;
        costDetails.innerHTML = `
            <div style="margin-bottom: 10px;"><strong>Estimated Tokens Used:</strong> ${cost.estimated_tokens}</div>
            <div style="margin-bottom: 10px;"><strong>Estimated Cost:</strong> ${cost.estimated_cost}</div>
            <div style="margin-bottom: 10px;"><strong>Cost per Line:</strong> ${cost.cost_per_line}</div>
            <div><strong>Efficiency Ratio:</strong> ${cost.efficiency_ratio} (higher = more efficient)</div>
        `;

        // Show summary
        document.getElementById('summaryText').textContent = result.summary;

        // Show results section
        resultsSection.style.display = 'block';
        resultsSection.scrollIntoView({ behavior: 'smooth' });
    }

    function showError(message) {
        document.getElementById('errorText').textContent = message;
        errorSection.style.display = 'block';
        errorSection.scrollIntoView({ behavior: 'smooth' });
    }

    function hideResults() {
        resultsSection.style.display = 'none';
    }

    function hideError() {
        errorSection.style.display = 'none';
    }

    // Add some example data for testing
    const exampleBtn = document.createElement('button');
    exampleBtn.textContent = 'Load Example';
    exampleBtn.type = 'button';
    exampleBtn.className = 'example-btn';
    exampleBtn.style.cssText = `
        margin-top: 10px;
        padding: 8px 16px;
        background: #6b7280;
        color: white;
        border: none;
        border-radius: 5px;
        cursor: pointer;
        font-size: 14px;
    `;
    
    exampleBtn.addEventListener('click', function() {
        document.getElementById('platform').value = 'replit';
        document.getElementById('prompt').value = 'Create a simple calculator that can add, subtract, multiply and divide two numbers';
        document.getElementById('code').value = `import math
import sys
import os
from datetime import datetime

class AdvancedCalculator:
    def __init__(self):
        self.history = []
        self.current_time = datetime.now()
        self.version = "1.0.0"
        
    def log_operation(self, operation, result):
        self.history.append({
            'operation': operation,
            'result': result,
            'timestamp': datetime.now()
        })
    
    def add(self, a, b):
        try:
            result = float(a) + float(b)
            self.log_operation(f"{a} + {b}", result)
            return result
        except ValueError as e:
            print(f"Error: {e}")
            return None
    
    def subtract(self, a, b):
        try:
            result = float(a) - float(b)
            self.log_operation(f"{a} - {b}", result)
            return result
        except ValueError as e:
            print(f"Error: {e}")
            return None
    
    def multiply(self, a, b):
        try:
            result = float(a) * float(b)
            self.log_operation(f"{a} * {b}", result)
            return result
        except ValueError as e:
            print(f"Error: {e}")
            return None
    
    def divide(self, a, b):
        try:
            if float(b) == 0:
                raise ZeroDivisionError("Cannot divide by zero")
            result = float(a) / float(b)
            self.log_operation(f"{a} / {b}", result)
            return result
        except (ValueError, ZeroDivisionError) as e:
            print(f"Error: {e}")
            return None
    
    def get_history(self):
        return self.history
    
    def clear_history(self):
        self.history = []
    
def main():
    calc = AdvancedCalculator()
    print("Advanced Calculator v1.0.0")
    print("Available operations: add, subtract, multiply, divide")
    
    while True:
        try:
            operation = input("Enter operation (or 'quit' to exit): ").lower().strip()
            
            if operation == 'quit':
                break
            
            if operation not in ['add', 'subtract', 'multiply', 'divide']:
                print("Invalid operation")
                continue
            
            a = input("Enter first number: ")
            b = input("Enter second number: ")
            
            if operation == 'add':
                result = calc.add(a, b)
            elif operation == 'subtract':
                result = calc.subtract(a, b)
            elif operation == 'multiply':
                result = calc.multiply(a, b)
            elif operation == 'divide':
                result = calc.divide(a, b)
            
            if result is not None:
                print(f"Result: {result}")
                
        except KeyboardInterrupt:
            print("\\nGoodbye!")
            break
        except Exception as e:
            print(f"Unexpected error: {e}")

if __name__ == "__main__":
    main()`;
    });
    
    form.appendChild(exampleBtn);
});
