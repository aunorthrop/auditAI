# AI Code Auditor 🔍

A web platform that analyzes AI-generated code to detect inefficiencies, potential overcharging patterns, and unnecessary complexity. Perfect for users of Replit AI, Lovable, Cursor, and other AI coding platforms who want to ensure they're getting good value.

## Features

- **Efficiency Analysis**: Scores your code from 1-100 based on how well it solves the original prompt
- **Red Flag Detection**: Identifies signs of time-wasting or overengineered solutions
- **Bug Detection**: Finds potential issues in AI-generated code
- **Cost Analysis**: Estimates token usage and cost efficiency
- **Platform-Specific Insights**: Tailored analysis for different AI coding platforms
- **Optimization Suggestions**: Actionable recommendations to improve your code

## Quick Start

1. **Clone the repository**
   ```bash
   git clone https://github.com/yourusername/ai-code-auditor.git
   cd ai-code-auditor
   ```

2. **Set up virtual environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure environment**
   ```bash
   cp .env.example .env
   # Edit .env and add your OpenAI API key
   ```

5. **Run the application**
   ```bash
   python app.py
   ```

6. **Open in browser**
   Navigate to `http://localhost:5000`

## How It Works

1. **Input**: Paste your original prompt and the AI-generated code
2. **Analysis**: The system uses OpenAI GPT to analyze efficiency, complexity, and potential issues
3. **Scoring**: Get metrics on efficiency (1-100), complexity (1-10), and bug count
4. **Insights**: Receive red flags, optimization suggestions, and cost analysis

## Example Analysis

The platform can detect issues like:
- ❌ Over-engineered solutions (100+ lines for simple tasks)
- ❌ Unnecessary imports and dependencies  
- ❌ Code that doesn't match the original prompt
- ❌ Potential bugs that require costly fix iterations
- ❌ Inefficient algorithms or approaches

## API Endpoints

### POST `/analyze`

Analyzes code for efficiency and potential issues.

**Request Body:**
```json
{
  "prompt": "Your original prompt text",
  "code": "The AI-generated code",
  "platform": "replit|lovable|cursor|chatgpt|unknown"
}
```

**Response:**
```json
{
  "efficiency_score": 85,
  "complexity_score": 4,
  "bug_count": 1,
  "optimization_suggestions": ["Remove unnecessary imports", "Simplify error handling"],
  "red_flags": ["🚩 Solution appears over-engineered for the given prompt"],
  "cost_analysis": {
    "estimated_tokens": 450,
    "estimated_cost": 0.009,
    "efficiency_ratio": 0.75,
    "cost_per_line": 0.0003
  },
  "summary": "Code is functional but could be simplified...",
  "platform": "replit"
}
```

## Platform-Specific Detection

The auditor knows common patterns for different AI platforms:

- **Replit**: Unnecessary package installations, overly complex file structures
- **Lovable**: Redundant React components, inline styles instead of CSS  
- **Cursor**: Excessive commenting, over-engineered solutions
- **General**: Bug patterns that lead to expensive fix iterations

## Development

### Project Structure
```
ai-code-auditor/
├── app.py              # Flask application
├── requirements.txt    # Dependencies
├── .env.example       # Environment template
├── auditor/           # Core analysis logic
│   ├── analyzer.py    # Main auditing engine
│   └── models.py      # Data models
├── static/            # CSS and JavaScript
└── templates/         # HTML templates
```

### Adding New Platform Patterns

Edit `auditor/models.py` to add detection patterns for new AI coding platforms:

```python
NEW_PLATFORM_PATTERNS = [
    "pattern1",
    "pattern2"
]
```

### Extending Analysis

The `CodeAuditor` class in `auditor/analyzer.py` can be extended with new analysis methods:

- `_analyze_security()`: Security vulnerability detection
- `_analyze_performance()`: Performance bottleneck identification  
- `_analyze_maintainability()`: Code maintainability scoring

## Deployment

### Heroku
1. Create a Heroku app
2. Set the `OPENAI_API_KEY` environment variable
3. Deploy using Git

### Docker
```dockerfile
FROM python:3.9-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt
COPY . .
EXPOSE 5000
CMD ["python", "app.py"]
```

## Contributing

1. Fork the repository
2. Create a feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Integration with GitHub to analyze repository code
- [ ] Historical tracking of code efficiency over time
- [ ] Team dashboard for organizations
- [ ] More AI platform integrations (Claude, Bard, etc.)
- [ ] Advanced cost optimization recommendations
- [ ] API rate limiting and authentication
- [ ] Webhook support for CI/CD integration

## Support

If you encounter any issues or have questions:

1. Check the [Issues](https://github.com/yourusername/ai-code-auditor/issues) page
2. Create a new issue with detailed information
3. Join our community discussions

---

**Built to help developers get better value from AI coding tools** 🚀
