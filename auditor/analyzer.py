import openai
import re
from typing import Dict, List, Any
from .models import AuditResult, PlatformPatterns

class CodeAuditor:
    def __init__(self, api_key: str):
        self.client = openai.OpenAI(api_key=api_key)
        
    def audit_code(self, prompt: str, code: str, platform: str = "unknown") -> Dict[str, Any]:
        """Main audit function that analyzes code efficiency and potential issues"""
        
        # Get platform-specific patterns
        platform_patterns = PlatformPatterns.get_patterns(platform)
        
        # Analyze with OpenAI
        analysis = self._analyze_with_ai(prompt, code, platform_patterns)
        
        # Calculate metrics
        efficiency_score = self._calculate_efficiency_score(prompt, code, analysis)
        complexity_score = self._calculate_complexity(code)
        bug_count = self._count_potential_bugs(analysis)
        
        # Extract insights
        optimizations = self._extract_optimizations(analysis)
        red_flags = self._detect_red_flags(prompt, code, analysis)
        cost_analysis = self._analyze_costs(prompt, code)
        
        return {
            'efficiency_score': efficiency_score,
            'complexity_score': complexity_score,
            'bug_count': bug_count,
            'optimization_suggestions': optimizations,
            'cost_analysis': cost_analysis,
            'red_flags': red_flags,
            'summary': analysis.get('summary', 'Analysis completed'),
            'platform': platform
        }
    
    def _analyze_with_ai(self, prompt: str, code: str, patterns: List[str]) -> Dict[str, Any]:
        """Use OpenAI to analyze the code quality and efficiency"""
        
        system_prompt = f"""You are an expert code auditor. Analyze the given prompt and generated code for:

1. Efficiency - Could this be solved more simply?
2. Overengineering - Is the solution unnecessarily complex?
3. Potential bugs or issues
4. Whether the code actually solves the original prompt
5. Signs of "time wasting" or unnecessary iterations

Platform-specific issues to watch for: {', '.join(patterns) if patterns else 'None specified'}

Respond in JSON format with:
- summary: Brief overall assessment
- efficiency_issues: List of efficiency problems
- bugs: List of potential bugs
- overengineered: Boolean if solution is too complex
- matches_prompt: Boolean if code solves the original request
- optimizations: List of suggested improvements
"""

        user_prompt = f"""
ORIGINAL PROMPT:
{prompt}

GENERATED CODE:
{code}

Please analyze this code for efficiency, bugs, and whether it's appropriately solving the original prompt.
"""
        
        try:
            response = self.client.chat.completions.create(
                model="gpt-3.5-turbo",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": user_prompt}
                ],
                temperature=0.1
            )
            
            content = response.choices[0].message.content
            # Try to parse as JSON, fallback to text analysis
            try:
                import json
                return json.loads(content)
            except:
                return {"summary": content, "efficiency_issues": [], "bugs": [], "optimizations": []}
                
        except Exception as e:
            return {"summary": f"Analysis failed: {str(e)}", "efficiency_issues": [], "bugs": [], "optimizations": []}
    
    def _calculate_efficiency_score(self, prompt: str, code: str, analysis: Dict) -> int:
        """Calculate efficiency score from 1-100"""
        score = 100
        
        # Deduct points for various issues
        if analysis.get('overengineered', False):
            score -= 30
        
        score -= len(analysis.get('efficiency_issues', [])) * 10
        score -= len(analysis.get('bugs', [])) * 15
        
        if not analysis.get('matches_prompt', True):
            score -= 40
        
        # Code length vs prompt complexity
        lines_of_code = len(code.split('\n'))
        prompt_words = len(prompt.split())
        
        if lines_of_code > prompt_words * 3:  # Rough heuristic
            score -= 20
        
        return max(1, min(100, score))
    
    def _calculate_complexity(self, code: str) -> int:
        """Simple complexity score from 1-10"""
        lines = code.split('\n')
        complexity = 1
        
        # Count nested structures
        nesting_level = 0
        max_nesting = 0
        
        for line in lines:
            stripped = line.strip()
            if any(keyword in stripped for keyword in ['if ', 'for ', 'while ', 'def ', 'class ']):
                nesting_level += 1
                max_nesting = max(max_nesting, nesting_level)
            
            # Simple heuristic for closing blocks
            if line.strip() == '' or not line.startswith(' ' * (nesting_level * 4)):
                nesting_level = max(0, nesting_level - 1)
        
        complexity += max_nesting
        complexity += len(lines) // 50  # Add complexity for length
        
        return min(10, complexity)
    
    def _count_potential_bugs(self, analysis: Dict) -> int:
        """Count potential bugs from analysis"""
        return len(analysis.get('bugs', []))
    
    def _extract_optimizations(self, analysis: Dict) -> List[str]:
        """Extract optimization suggestions"""
        optimizations = analysis.get('optimizations', [])
        efficiency_issues = analysis.get('efficiency_issues', [])
        
        # Combine and clean up suggestions
        all_suggestions = optimizations + [f"Fix: {issue}" for issue in efficiency_issues]
        
        return all_suggestions[:5]  # Limit to top 5 suggestions
    
    def _detect_red_flags(self, prompt: str, code: str, analysis: Dict) -> List[str]:
        """Detect potential signs of time-wasting or overcharging"""
        red_flags = []
        
        # Check if solution is way more complex than needed
        if analysis.get('overengineered', False):
            red_flags.append("🚩 Solution appears over-engineered for the given prompt")
        
        # Check for excessive code length
        prompt_words = len(prompt.split())
        code_lines = len([line for line in code.split('\n') if line.strip()])
        
        if code_lines > prompt_words * 2:
            red_flags.append(f"🚩 Code is unusually long ({code_lines} lines for {prompt_words} word prompt)")
        
        # Check for common time-wasting patterns
        if 'import' in code and code.count('import') > 5:
            red_flags.append("🚩 Excessive imports may indicate unnecessary complexity")
        
        if not analysis.get('matches_prompt', True):
            red_flags.append("🚩 Generated code doesn't appear to solve the original request")
        
        bug_count = len(analysis.get('bugs', []))
        if bug_count > 3:
            red_flags.append(f"🚩 High number of potential bugs ({bug_count}) - may require multiple fix iterations")
        
        return red_flags
    
    def _analyze_costs(self, prompt: str, code: str) -> Dict[str, Any]:
        """Analyze cost efficiency"""
        prompt_complexity = len(prompt.split())
        code_complexity = len(code.split('\n'))
        
        # Rough cost estimates (these would be more accurate with real pricing data)
        estimated_tokens_used = prompt_complexity + code_complexity * 2
        estimated_cost = estimated_tokens_used * 0.002  # Rough GPT-3.5 pricing
        
        # Determine if this was efficient
        efficiency_ratio = prompt_complexity / code_complexity if code_complexity > 0 else 0
        
        return {
            'estimated_tokens': estimated_tokens_used,
            'estimated_cost': round(estimated_cost, 4),
            'efficiency_ratio': round(efficiency_ratio, 2),
            'cost_per_line': round(estimated_cost / max(1, code_complexity), 4)
        }
