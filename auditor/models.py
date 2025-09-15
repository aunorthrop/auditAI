from dataclasses import dataclass
from typing import List, Dict, Any

@dataclass
class AuditResult:
    efficiency_score: int  # 1-100
    complexity_score: int  # 1-10
    bug_count: int
    optimization_suggestions: List[str]
    cost_analysis: Dict[str, Any]
    red_flags: List[str]
    summary: str
    
class PlatformPatterns:
    """Known patterns and issues for different AI coding platforms"""
    
    REPLIT_PATTERNS = [
        "unnecessary package installations",
        "overly complex file structure",
        "missing error handling for replit environment"
    ]
    
    LOVABLE_PATTERNS = [
        "redundant react components",
        "inline styles instead of css",
        "missing prop validation"
    ]
    
    CURSOR_PATTERNS = [
        "excessive commenting",
        "over-engineered solutions",
        "unnecessary abstractions"
    ]
    
    @classmethod
    def get_patterns(cls, platform: str) -> List[str]:
        platform_map = {
            'replit': cls.REPLIT_PATTERNS,
            'lovable': cls.LOVABLE_PATTERNS,
            'cursor': cls.CURSOR_PATTERNS
        }
        return platform_map.get(platform.lower(), [])
