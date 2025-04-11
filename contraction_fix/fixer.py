from __future__ import annotations
from typing import Dict, List, Optional, Tuple, Union, ClassVar
import json
import pkgutil
from functools import lru_cache, cached_property
from dataclasses import dataclass
import re
from collections import defaultdict
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
    CONTRACTION_BASES: ClassVar[set[str]] = {
        'he', 'she', 'it', 'what', 'who', 'that', 'there', 'here', 'where',
        'when', 'why', 'how', 'this', 'everyone', 'somebody', 'someone',
        'something', 'nobody', 'let'
    }
    
    TIME_WORDS: ClassVar[set[str]] = {
        'today', 'tomorrow', 'tonight', 'morning', 'evening', 'afternoon',
        'week', 'month', 'year', 'century', 'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday'
    }

    MONTHS: ClassVar[list[str]] = [
        "january", "february", "march", "april", "june", "july",
        "august", "september", "october", "november", "december"
    ]

    def __init__(self, use_informal: bool = True, use_slang: bool = True, cache_size: int = 1024):
        """Initialize the contraction fixer with optional dictionaries.
        
        Args:
            use_informal: Whether to use the informal contractions dictionary
            use_slang: Whether to use the internet slang dictionary
            cache_size: Size of the LRU cache for the fix method
        """
        self._lock = Lock()
        self.cache_size = cache_size
        self._pattern = None  # Lazy initialization of regex pattern
        
        # Load and combine dictionaries
        try:
            standard = self._load_dict("standard_contractions.json")
            informal = self._load_dict("informal_contractions.json") if use_informal else {}
            slang = self._load_dict("internet_slang.json") if use_slang else {}
            
            # Add month abbreviations
            for month in self.MONTHS:
                standard[month[:3] + "."] = month
            
            # Build combined dict
            self.combined_dict = {}
            self.combined_dict.update(standard)
            if use_informal:
                self.combined_dict.update(informal)
            if use_slang:
                self.combined_dict.update(slang)
            
            # Add alternative apostrophes
            self._add_alt_apostrophes()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ContractionFixer: {str(e)}")

    def _load_dict(self, filename: str) -> Dict[str, str]:
        """Load a dictionary from a JSON file in the package data.
        
        Args:
            filename: Name of the JSON file to load
            
        Returns:
            Dictionary loaded from the JSON file
            
        Raises:
            FileNotFoundError: If the dictionary file is not found
            ValueError: If the JSON is invalid
            RuntimeError: For other loading errors
        """
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
        alt_contractions = {k.replace("'", "'"): v for k, v in self.combined_dict.items()}
        self.combined_dict.update(alt_contractions)

    @cached_property
    def pattern(self) -> re.Pattern:
        """Lazily compile and cache the regex pattern for matching contractions."""
        if not self._pattern:
            self._pattern = re.compile(
                r'\b(' + '|'.join(re.escape(k) for k in self.combined_dict.keys()) + r')\b',
                re.IGNORECASE
            )
        return self._pattern

    def _is_contraction_s(self, word: str) -> bool:
        """Determine if a word ending in 's is a contraction or possessive.
        
        Args:
            word: The word to check (including the 's)
            
        Returns:
            True if it's a contraction, False if it's possessive
        """
        # Remove the 's from the end
        base = word[:-2].lower()
        
        # Check if it's a common contraction base
        if base in self.CONTRACTION_BASES:
            return True
            
        # Check if it's a time word (these can be both, but more commonly contractions)
        if base in self.TIME_WORDS:
            return True
            
        # If the base word ends in s, x, z, ch, sh - likely possessive
        if base.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return False
            
        # If the word is capitalized (not at start of sentence) - likely possessive (proper noun)
        if word[0].isupper() and not self._is_sentence_start(word):
            return False
            
        # Default to possessive for unknown cases
        return False

    def _is_sentence_start(self, word: str, context: str = '', position: int = 0) -> bool:
        """Check if a word appears at the start of a sentence.
        
        Args:
            word: The word to check
            context: The surrounding text (optional)
            position: The position of the word in the text (optional)
            
        Returns:
            True if the word is likely at the start of a sentence
        """
        if not context or position == 0:
            return True
            
        # Check previous character for sentence endings
        prev_char = context[position - 1] if position > 0 else ''
        return prev_char in '.!?'

    @property
    def fix(self):
        """Property that returns a cached version of the fix function."""
        if not hasattr(self, '_fix'):
            @lru_cache(maxsize=self.cache_size)
            def _fix(text: str) -> str:
                """Fix contractions in the given text.
                
                Args:
                    text: The text to fix
                    
                Returns:
                    The text with contractions fixed
                """
                def replace_match(match):
                    matched_text = match.group(0)
                    
                    # Special handling for 's cases
                    if matched_text.endswith("'s") or matched_text.endswith("'s"):
                        if not self._is_contraction_s(matched_text):
                            return matched_text  # Keep possessive forms unchanged
                    
                    # Try different apostrophe versions for lookup
                    replacement = None
                    lookup_versions = [
                        matched_text,
                        matched_text.lower(),
                        matched_text.replace("'", "'"),
                        matched_text.lower().replace("'", "'")
                    ]
                    
                    for version in lookup_versions:
                        if version in self.combined_dict:
                            replacement = self.combined_dict[version]
                            break
                    
                    # If no replacement found, return original
                    if not replacement:
                        return matched_text
                    
                    # Preserve case if original was uppercase
                    if matched_text.isupper():
                        return replacement.upper()
                    return replacement
                    
                return self.pattern.sub(replace_match, text)
            
            self._fix = _fix
        return self._fix

    def preview(self, text: str, context_size: int = 10) -> List[Match]:
        """Preview contractions in the text with context.
        
        Args:
            text: The text to analyze
            context_size: Number of characters to show before and after each match
            
        Returns:
            List of Match objects containing match information and context
        """
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
        """Add a new contraction to the dictionary.
        
        Args:
            contraction: The contraction to add
            expansion: The expanded form
        """
        with self._lock:
            self.combined_dict[contraction] = expansion
            self.combined_dict[contraction.replace("'", "'")] = expansion
            # Invalidate cached properties
            if hasattr(self, '_pattern'):
                delattr(self, '_pattern')

    def remove_contraction(self, contraction: str) -> None:
        """Remove a contraction from the dictionary.
        
        Args:
            contraction: The contraction to remove
        """
        with self._lock:
            if contraction in self.combined_dict:
                del self.combined_dict[contraction]
            alt_contraction = contraction.replace("'", "'")
            if alt_contraction in self.combined_dict:
                del self.combined_dict[alt_contraction]
            # Invalidate cached properties
            if hasattr(self, '_pattern'):
                delattr(self, '_pattern') 