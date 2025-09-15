import os
import openai
from typing import Dict, List, Any
from .models import AuditResult, PlatformPatterns

class CodeAuditor:
    def __init__(self, api_key: str = None):
        """Initialize the code auditor with OpenAI API key"""
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key is required")
        
        # Initialize OpenAI client (v1.0+ compatible) with explicit parameters only
        try:
            # Only pass supported parameters to avoid proxy issues
            self.client = openai.OpenAI(
                api_key=self.api_key,
                # Explicitly don't pass any proxy-related parameters
            )
        except TypeError as e:
            if 'proxies' in str(e):
                # Fallback for environments that might inject proxy settings
                print(f"Warning: Proxy parameter issue detected: {e}")
                # Try with minimal parameters
                self.client = openai.OpenAI(api_key=self.api_key)
            else:
                raise e
    
    def audit_code(self, code: str, platform: str = None, language: str = "python") -> AuditResult:
        """Audit the provided code and return detailed analysis"""
        try:
            # Get platform-specific patterns if specified
            platform_patterns = PlatformPatterns.get_patterns(platform) if platform else []
            
            # Create the audit prompt
            prompt = self._create_audit_prompt(code, platform_patterns, language)
            
            # Get analysis from OpenAI
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": "You are an expert code auditor and security analyst."},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=1500,
                temperature=0.1
            )
            
            # Parse the response
            analysis = response.choices[0].message.content
            return self._parse_analysis(analysis, code)
            
        except Exception as e:
            # Fallback analysis in case of API issues
            return self._fallback_analysis(code, str(e))
    
    def _create_audit_prompt(self, code: str, platform_patterns: List[str], language: str) -> str:
        """Create a detailed prompt for code analysis"""
        platform_context = ""
        if platform_patterns:
            platform_context = f"\nAlso check for these platform-specific issues: {', '.join(platform_patterns)}"
        
        return f"""
Please audit this {language} code and provide a detailed analysis:

CODE:
{code}

Please analyze for:
1. Code efficiency (score 1-100)
2. Complexity score (1-10, where 10 is most complex)
3. Potential bugs or issues
4. Optimization suggestions
5. Cost analysis (performance, maintainability)
6. Security red flags
7. Overall summary

{platform_context}

Format your response as structured analysis covering all these points.
"""
    
    def _parse_analysis(self, analysis: str, code: str) -> AuditResult:
        """Parse the AI analysis into structured AuditResult"""
        # Basic parsing - in production, you'd want more sophisticated parsing
        lines = analysis.split('\n')
        
        # Default values
        efficiency_score = self._extract_score(analysis, "efficiency", 75)
        complexity_score = self._extract_score(analysis, "complexity", 5)
        bug_count = self._count_bugs(analysis)
        optimization_suggestions = self._extract_suggestions(analysis)
        red_flags = self._extract_red_flags(analysis)
        summary = self._extract_summary(analysis)
        
        # Simple cost analysis
        cost_analysis = {
            "lines_of_code": len(code.split('\n')),
            "estimated_runtime": "medium" if len(code) > 1000 else "low",
            "maintainability": "good" if efficiency_score > 70 else "needs_improvement"
        }
        
        return AuditResult(
            efficiency_score=efficiency_score,
            complexity_score=complexity_score,
            bug_count=bug_count,
            optimization_suggestions=optimization_suggestions,
            cost_analysis=cost_analysis,
            red_flags=red_flags,
            summary=summary
        )
    
    def _fallback_analysis(self, code: str, error_msg: str) -> AuditResult:
        """Provide basic analysis when API is unavailable"""
        lines = code.split('\n')
        non_empty_lines = [line for line in lines if line.strip()]
        
        return AuditResult(
            efficiency_score=70,  # Default moderate score
            complexity_score=5,   # Default moderate complexity
            bug_count=0,
            optimization_suggestions=[
                "API analysis unavailable - manual review recommended",
                "Consider code formatting and structure improvements"
            ],
            cost_analysis={
                "lines_of_code": len(non_empty_lines),
                "estimated_runtime": "unknown",
                "maintainability": "requires_analysis",
                "api_error": error_msg
            },
            red_flags=["API analysis unavailable"],
            summary=f"Basic analysis: {len(non_empty_lines)} lines of code. Full analysis unavailable due to API issues."
        )
    
    def _extract_score(self, text: str, score_type: str, default: int) -> int:
        """Extract numeric scores from analysis text"""
        import re
        pattern = rf"{score_type}.*?(\d+)"
        match = re.search(pattern, text.lower())
        if match:
            return min(100, max(1, int(match.group(1))))
        return default
    
    def _count_bugs(self, text: str) -> int:
        """Count potential bugs mentioned in analysis"""
        bug_keywords = ["bug", "issue", "problem", "error", "vulnerability"]
        count = 0
        for keyword in bug_keywords:
            count += text.lower().count(keyword)
        return min(count, 10)  # Cap at 10 for reasonableness
    
    def _extract_suggestions(self, text: str) -> List[str]:
        """Extract optimization suggestions from analysis"""
        suggestions = []
        lines = text.split('\n')
        
        for line in lines:
            line = line.strip()
            if any(word in line.lower() for word in ['suggest', 'recommend', 'improve', 'optimize', 'consider']):
                if len(line) > 10:  # Avoid very short lines
                    suggestions.append(line)
        
        # Default suggestions if none found
        if not suggestions:
            suggestions = [
                "Consider adding error handling",
                "Review variable naming conventions",
                "Add documentation and comments"
            ]
        
        return suggestions[:5]  # Limit to 5 suggestions
    
    def _extract_red_flags(self, text: str) -> List[str]:
        """Extract security and quality red flags"""
        red_flags = []
        flag_keywords = ["security", "vulnerable", "risk", "dangerous", "warning", "critical"]
        
        lines = text.split('\n')
        for line in lines:
            if any(keyword in line.lower() for keyword in flag_keywords):
                if len(line.strip()) > 10:
                    red_flags.append(line.strip())
        
        return red_flags[:3]  # Limit to 3 most important flags
    
    def _extract_summary(self, text: str) -> str:
        """Extract or generate summary from analysis"""
        lines = text.split('\n')
        
        # Look for summary section
        for i, line in enumerate(lines):
            if 'summary' in line.lower():
                # Get next few lines
                summary_lines = lines[i+1:i+4]
                summary = ' '.join([l.strip() for l in summary_lines if l.strip()])
                if summary:
                    return summary
        
        # Fallback: use first substantial paragraph
        for line in lines:
            if len(line.strip()) > 50:
                return line.strip()
        
        return "Code analysis completed. Review detailed metrics for insights."
