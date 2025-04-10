from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union
import json
import pkgutil
from functools import lru_cache
from dataclasses import dataclass
import re
from collections import defaultdict

@dataclass
class Match:
    text: str
    start: int
    end: int
    replacement: str

class ContractionFixer:
    def __init__(self, use_informal: bool = True, use_slang: bool = True):
        """Initialize the contraction fixer with optional dictionaries.
        
        Args:
            use_informal: Whether to use the informal contractions dictionary
            use_slang: Whether to use the internet slang dictionary
        """
        self.standard = self._load_dict("standard_contractions.json")
        self.informal = self._load_dict("informal_contractions.json") if use_informal else {}
        self.slang = self._load_dict("internet_slang.json") if use_slang else {}
        
        # Add month abbreviations
        months = [
            "january", "february", "march", "april", "june", "july",
            "august", "september", "october", "november", "december"
        ]
        for month in months:
            self.standard[month[:3] + "."] = month
            
        # Add alternative apostrophe versions
        self._add_alt_apostrophes()
        
        # Build the combined dictionary
        self.combined_dict = self._build_combined_dict()
        
        # Precompile regex patterns
        self._compile_patterns()
        
    def _load_dict(self, filename: str) -> Dict[str, str]:
        """Load a dictionary from a JSON file in the package data."""
        data = pkgutil.get_data("contraction_fix", f"data/{filename}")
        return json.loads(data.decode("utf-8"))
        
    def _add_alt_apostrophes(self):
        """Add alternative apostrophe versions to dictionaries."""
        for d in [self.standard, self.informal, self.slang]:
            d.update({k.replace("'", "’"): v for k, v in d.items()})
            
    def _build_combined_dict(self) -> Dict[str, str]:
        """Build the combined dictionary from all enabled dictionaries."""
        combined = {}
        combined.update(self.standard)
        combined.update(self.informal)
        combined.update(self.slang)
        return combined
        
    def _compile_patterns(self):
        """Precompile regex patterns for faster matching."""
        # Create a pattern that matches any contraction
        self.pattern = re.compile(
            r'\b(' + '|'.join(re.escape(k) for k in self.combined_dict.keys()) + r')\b',
            re.IGNORECASE
        )
        
    @lru_cache(maxsize=1024)
    def fix(self, text: str) -> str:
        """Fix contractions in the given text.
        
        Args:
            text: The text to fix
            
        Returns:
            The text with contractions fixed
        """
        def replace_match(match):
            matched_text = match.group(0)
            return self.combined_dict.get(matched_text.lower(), matched_text)
            
        return self.pattern.sub(replace_match, text)
        
    def preview(self, text: str, context_size: int = 10) -> List[Dict[str, Union[str, int]]]:
        """Preview contractions in the text with context.
        
        Args:
            text: The text to analyze
            context_size: Number of characters to show before and after each match
            
        Returns:
            List of dictionaries containing match information and context
        """
        matches = []
        for match in self.pattern.finditer(text):
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            context = text[start:end]
            
            matches.append({
                "match": match.group(0),
                "start": match.start(),
                "end": match.end(),
                "replacement": self.combined_dict.get(match.group(0).lower(), match.group(0)),
                "context": context
            })
            
        return matches
        
    def add_contraction(self, contraction: str, expansion: str) -> None:
        """Add a new contraction to the dictionary.
        
        Args:
            contraction: The contraction to add
            expansion: The expanded form
        """
        self.combined_dict[contraction] = expansion
        self.combined_dict[contraction.replace("'", "’")] = expansion
        self._compile_patterns()  # Recompile patterns with new contraction
        
    def remove_contraction(self, contraction: str) -> None:
        """Remove a contraction from the dictionary.
        
        Args:
            contraction: The contraction to remove
        """
        if contraction in self.combined_dict:
            del self.combined_dict[contraction]
        alt_contraction = contraction.replace("'", "’")
        if alt_contraction in self.combined_dict:
            del self.combined_dict[alt_contraction]
        self._compile_patterns()  # Recompile patterns without the contraction 