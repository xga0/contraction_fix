from __future__ import annotations
from typing import Dict, List, ClassVar
import json
import pkgutil
from functools import lru_cache, cached_property
from dataclasses import dataclass
import re
from threading import Lock

@dataclass
class Match:
    text: str
    start: int
    end: int
    replacement: str
    context: str

class ContractionFixer:
    # Class constants for commonly used sets
    CONTRACTION_BASES: ClassVar[frozenset[str]] = frozenset({
        'he', 'she', 'it', 'what', 'who', 'that', 'there', 'here', 'where',
        'when', 'why', 'how', 'this', 'everyone', 'somebody', 'someone',
        'something', 'nobody', 'let'
    })
    
    TIME_WORDS: ClassVar[frozenset[str]] = frozenset({
        'today', 'tomorrow', 'tonight', 'morning', 'evening', 'afternoon',
        'week', 'month', 'year', 'century', 'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday'
    })

    MONTHS: ClassVar[tuple[str, ...]] = (
        "january", "february", "march", "april", "june", "july",
        "august", "september", "october", "november", "december"
    )

    def __init__(self, use_informal: bool = True, use_slang: bool = True, cache_size: int = 1024):
        """Initialize the contraction fixer with optional dictionaries."""
        self._lock = Lock()
        
        try:
            standard = self._load_dict("standard_contractions.json")
            informal = self._load_dict("informal_contractions.json") if use_informal else {}
            slang = self._load_dict("internet_slang.json") if use_slang else {}
            
            for month in self.MONTHS:
                standard[month[:3] + "."] = month
            
            self.combined_dict = {**standard}
            if use_informal:
                self.combined_dict.update(informal)
            if use_slang:
                self.combined_dict.update(slang)
            
            self._add_alt_apostrophes()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ContractionFixer: {str(e)}")

    def _load_dict(self, filename: str) -> Dict[str, str]:
        """Load a dictionary from a JSON file in the package data."""
        try:
            data = pkgutil.get_data("contraction_fix", f"data/{filename}")
            if data is None:
                raise FileNotFoundError(f"Dictionary file {filename} not found")
            return json.loads(data.decode("utf-8"))
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to load dictionary {filename}: {str(e)}")

    def _add_alt_apostrophes(self) -> None:
        """Add alternative apostrophe versions to the combined dictionary."""
        alt_contractions = {k.replace("'", "'"): v for k, v in self.combined_dict.items() if "'" in k}
        self.combined_dict.update(alt_contractions)

    @cached_property
    def pattern(self) -> re.Pattern:
        """Lazily compile and cache the regex pattern for matching contractions."""
        return re.compile(
            r'\b(' + '|'.join(re.escape(k) for k in self.combined_dict.keys()) + r')\b',
            re.IGNORECASE
        )

    def _is_contraction_s(self, word: str) -> bool:
        """Determine if a word ending in 's is a contraction or possessive."""
        base = word[:-2].lower()
        
        if base in self.CONTRACTION_BASES or base in self.TIME_WORDS:
            return True
            
        if base.endswith(('s', 'x', 'z', 'ch', 'sh')) or word[0].isupper():
            return False
            
        return False



    @lru_cache(maxsize=1024)
    def _fix_single(self, text: str) -> str:
        """Fix contractions in a single text with caching."""
        def replace_match(match):
            matched_text = match.group(0)
            
            if matched_text.endswith(("'s", "'s")):
                if not self._is_contraction_s(matched_text):
                    return matched_text
            
            matched_lower = matched_text.lower()
            if matched_lower in self.combined_dict:
                replacement = self.combined_dict[matched_lower]
            elif matched_text in self.combined_dict:
                replacement = self.combined_dict[matched_text]
            else:
                alt_text = matched_text.replace("'", "'")
                alt_lower = alt_text.lower()
                if alt_lower in self.combined_dict:
                    replacement = self.combined_dict[alt_lower]
                elif alt_text in self.combined_dict:
                    replacement = self.combined_dict[alt_text]
                else:
                    return matched_text
            
            return replacement.upper() if matched_text.isupper() else replacement
                
        return self.pattern.sub(replace_match, text)

    def fix(self, text: str) -> str:
        """Fix contractions in the given text."""
        return self._fix_single(text)

    def fix_batch(self, texts: List[str]) -> List[str]:
        """Fix contractions in multiple texts efficiently."""
        return [self._fix_single(text) for text in texts]

    def preview(self, text: str, context_size: int = 10) -> List[Match]:
        """Preview contractions in the text with context."""
        matches = []
        for match in self.pattern.finditer(text):
            start = max(0, match.start() - context_size)
            end = min(len(text), match.end() + context_size)
            context = text[start:end]
            replacement = self.combined_dict.get(match.group(0).lower(), match.group(0))
            
            matches.append(Match(
                text=match.group(0),
                start=match.start(),
                end=match.end(),
                replacement=replacement,
                context=context
            ))
        return matches

    def add_contraction(self, contraction: str, expansion: str) -> None:
        """Add a new contraction to the dictionary."""
        with self._lock:
            self.combined_dict[contraction] = expansion
            self.combined_dict[contraction.replace("'", "'")] = expansion
            if hasattr(self, 'pattern'):
                delattr(self, 'pattern')
            self._fix_single.cache_clear()

    def remove_contraction(self, contraction: str) -> None:
        """Remove a contraction from the dictionary."""
        with self._lock:
            self.combined_dict.pop(contraction, None)
            self.combined_dict.pop(contraction.replace("'", "'"), None)
            if hasattr(self, 'pattern'):
                delattr(self, 'pattern')
            self._fix_single.cache_clear() 