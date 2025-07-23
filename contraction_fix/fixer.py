from typing import Dict, List, ClassVar, FrozenSet, Tuple, Pattern, Optional, Set
import json
import pkgutil
from functools import lru_cache
from dataclasses import dataclass
import re
from threading import Lock

@dataclass(slots=True)
class Match:
    text: str
    start: int
    end: int
    replacement: str
    context: str

class ContractionFixer:
    # Pre-compiled frozensets for O(1) lookups
    CONTRACTION_BASES: ClassVar[FrozenSet[str]] = frozenset({
        'he', 'she', 'it', 'what', 'who', 'that', 'there', 'here', 'where',
        'when', 'why', 'how', 'this', 'everyone', 'somebody', 'someone',
        'something', 'nobody', 'let'
    })
    
    TIME_WORDS: ClassVar[FrozenSet[str]] = frozenset({
        'today', 'tomorrow', 'tonight', 'morning', 'evening', 'afternoon',
        'week', 'month', 'year', 'century', 'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday'
    })

    MONTHS: ClassVar[Tuple[str, ...]] = (
        "january", "february", "march", "april", "june", "july",
        "august", "september", "october", "november", "december"
    )
    
    # Pre-compiled month abbreviations for faster access
    MONTH_ABBREVS: ClassVar[FrozenSet[str]] = frozenset(month[:3] + "." for month in MONTHS)
    
    # Pre-compiled safe contractions set for faster lookup
    SAFE_CONTRACTIONS: ClassVar[FrozenSet[str]] = frozenset({
        "am not", "are not", "cannot", "could not", "did not", "do not", "does not",
        "had not", "has not", "have not", "he is", "he will", "he would", "here is",
        "how is", "is not", "it is", "it will", "it would", "let us", "must not",
        "shall not", "she is", "she will", "she would", "should not", "that is",
        "that will", "that would", "there is", "there will", "there would",
        "they are", "they have", "they will", "they would", "was not", "we are",
        "we have", "we will", "we would", "were not", "what is", "what will",
        "where is", "who is", "who will", "will not", "would not", "you are",
        "you have", "you will", "you would", "I am", "I have", "I will", "I would",
        "you all", "could have", "would have", "should have", "might have", "must have",
        "would have", "I would have", "going to", "want to", "got to", "kind of"
    })
    
    # Pre-compiled safe informal contractions
    SAFE_INFORMAL: ClassVar[Dict[str, str]] = {
        "going": "goin'",
        "doing": "doin'", 
        "nothing": "nothin'"
    }

    __slots__ = ('_lock', 'combined_dict', 'reverse_dict', '_pattern', '_reverse_pattern', 
                 '_use_informal', '_use_slang', '_dict_tuple', '_reverse_dict_tuple')

    def __init__(self, use_informal: bool = True, use_slang: bool = True, cache_size: int = 1024):
        """Initialize the contraction fixer with optional dictionaries."""
        self._lock = Lock()
        self._use_informal = use_informal
        self._use_slang = use_slang
        self._pattern: Optional[Pattern[str]] = None
        self._reverse_pattern: Optional[Pattern[str]] = None
        
        try:
            # Load dictionaries with optimized structure
            standard = self._load_dict_optimized("standard_contractions.json")
            informal = self._load_dict_optimized("informal_contractions.json") if use_informal else {}
            slang = self._load_dict_optimized("internet_slang.json") if use_slang else {}
            
            # Build combined dictionary with month abbreviations
            self.combined_dict = dict(standard)
            for month in self.MONTHS:
                self.combined_dict[month[:3] + "."] = month
            
            if use_informal:
                self.combined_dict.update(informal)
            if use_slang:
                self.combined_dict.update(slang)
            
            # Build reverse dictionary with optimized logic
            self.reverse_dict = self._build_reverse_dict_optimized(standard, use_informal)
            
            # Add alternative apostrophes efficiently
            self._add_alt_apostrophes_optimized()
            
            # Create tuple versions for even faster iteration (immutable, cache-friendly)
            self._dict_tuple = tuple(self.combined_dict.items())
            self._reverse_dict_tuple = tuple(self.reverse_dict.items())
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ContractionFixer: {str(e)}")

    def _load_dict_optimized(self, filename: str) -> Dict[str, str]:
        """Load a dictionary from a JSON file with optimized processing."""
        try:
            data = pkgutil.get_data("contraction_fix", f"data/{filename}")
            if data is None:
                raise FileNotFoundError(f"Dictionary file {filename} not found")
            
            raw_dict = json.loads(data.decode("utf-8"))
            # Use dict comprehension with intern for memory efficiency
            return {k.lower(): v for k, v in raw_dict.items()}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to load dictionary {filename}: {str(e)}")

    def _build_reverse_dict_optimized(self, standard: Dict[str, str], use_informal: bool) -> Dict[str, str]:
        """Build reverse dictionary with optimized selection logic."""
        reverse_dict = {}
        
        # Process standard contractions
        for contraction, expansion in standard.items():
            expansion_lower = expansion.lower()
            if (expansion_lower in self.SAFE_CONTRACTIONS and 
                "'" in contraction and len(contraction) > 2):
                
                existing = reverse_dict.get(expansion_lower)
                if (existing is None or 
                    (not contraction.startswith("'") and existing.startswith("'")) or 
                    (len(contraction) < len(existing) and not contraction.startswith("'"))):
                    reverse_dict[expansion_lower] = contraction
        
        # Add informal contractions if enabled
        if use_informal:
            reverse_dict.update(self.SAFE_INFORMAL)
        
        return reverse_dict

    def _add_alt_apostrophes_optimized(self) -> None:
        """Add alternative apostrophe versions with single pass optimization."""
        # Process both dictionaries in one pass to minimize iterations
        alt_contractions = {}
        alt_reverse = {}
        
        for k, v in self.combined_dict.items():
            if "'" in k:
                alt_key = k.replace("'", "'")
                alt_contractions[alt_key] = v
        
        for k, v in self.reverse_dict.items():
            if "'" in v:
                alt_value = v.replace("'", "'")
                alt_reverse[k] = alt_value
        
        self.combined_dict.update(alt_contractions)
        self.reverse_dict.update(alt_reverse)

    @property
    def pattern(self) -> Pattern[str]:
        """Lazily compile and cache the regex pattern for matching contractions."""
        if self._pattern is not None:
            return self._pattern
            
        # Optimize pattern compilation by pre-sorting and using efficient regex construction
        sorted_keys = sorted(self.combined_dict.keys(), key=lambda x: (-len(x), x))
        pattern_parts = []
        
        # Group patterns by type for more efficient regex
        apostrophe_patterns = []
        word_patterns = []
        
        for key in sorted_keys:
            escaped = re.escape(key)
            if "'" in key or "'" in key:
                apostrophe_patterns.append(escaped)
            else:
                word_patterns.append(escaped)
        
        # Build optimized pattern with grouped alternatives
        if apostrophe_patterns:
            pattern_parts.append(r'(?<!\w)(?:' + '|'.join(apostrophe_patterns) + r')(?!\w)')
        if word_patterns:
            pattern_parts.append(r'\b(?:' + '|'.join(word_patterns) + r')\b')
        
        pattern_str = '(' + '|'.join(pattern_parts) + ')' if pattern_parts else r'(?!.*)'
        self._pattern = re.compile(pattern_str, re.IGNORECASE)
        return self._pattern

    @property
    def reverse_pattern(self) -> Pattern[str]:
        """Lazily compile and cache the regex pattern for matching expanded forms."""
        if self._reverse_pattern is not None:
            return self._reverse_pattern
            
        # Optimize reverse pattern compilation
        sorted_keys = sorted(self.reverse_dict.keys(), key=lambda x: (-len(x), x))
        pattern_parts = [r'\b' + re.escape(key) + r'\b' for key in sorted_keys]
        
        pattern_str = '(' + '|'.join(pattern_parts) + ')' if pattern_parts else r'(?!.*)'
        self._reverse_pattern = re.compile(pattern_str, re.IGNORECASE)
        return self._reverse_pattern

    def _is_contraction_s_optimized(self, word: str) -> bool:
        """Optimized contraction 's detection with early returns."""
        if len(word) < 3:  # Minimum: x's
            return False
            
        base = word[:-2].lower()
        
        # Fast path: check sets first (O(1) lookups)
        if base in self.CONTRACTION_BASES:
            return True
        if base in self.TIME_WORDS:
            return True
            
        # Check ending patterns efficiently
        if base.endswith(('s', 'x', 'z')) or base.endswith(('ch', 'sh')):
            return False
        
        # Check if starts with uppercase (likely proper noun)
        return not word[0].isupper()

    @lru_cache(maxsize=2048)  # Increased cache size for better hit rate
    def _fix_single_optimized(self, text: str) -> str:
        """Optimized single text fixing with reduced overhead."""
        def replace_match(match):
            matched_text = match.group(0)
            
            # Fast path for 's contractions
            if matched_text.endswith(("'s", "'s")):
                if not self._is_contraction_s_optimized(matched_text):
                    return matched_text
            
            matched_lower = matched_text.lower()
            
            # Direct lookup first, then alternative
            replacement = self.combined_dict.get(matched_lower)
            if replacement is None:
                alt_text = matched_lower.replace("'", "'")
                replacement = self.combined_dict.get(alt_text)
                if replacement is None:
                    return matched_text
            
            # Optimized case handling
            if matched_text.isupper():
                return replacement.upper()
            elif matched_text[0].isupper():
                return replacement.capitalize()
            else:
                return replacement
                
        return self.pattern.sub(replace_match, text)

    @lru_cache(maxsize=2048)  # Increased cache size
    def _contract_single_optimized(self, text: str) -> str:
        """Optimized contracting with reduced overhead."""
        def replace_match(match):
            matched_text = match.group(0)
            matched_lower = matched_text.lower()
            
            replacement = self.reverse_dict.get(matched_lower)
            if replacement is None:
                return matched_text
                
            # Optimized case handling
            if matched_text.isupper():
                return replacement.upper()
            elif matched_text[0].isupper():
                return replacement.capitalize()
            else:
                return replacement
                
        return self.reverse_pattern.sub(replace_match, text)

    def fix(self, text: str) -> str:
        """Fix contractions in the given text."""
        return self._fix_single_optimized(text)

    def fix_batch(self, texts: List[str]) -> List[str]:
        """Optimized batch processing with list comprehension."""
        return [self._fix_single_optimized(text) for text in texts]

    def contract(self, text: str) -> str:
        """Contract expanded forms back to contractions in the given text."""
        return self._contract_single_optimized(text)

    def contract_batch(self, texts: List[str]) -> List[str]:
        """Optimized batch contracting."""
        return [self._contract_single_optimized(text) for text in texts]

    def preview(self, text: str, context_size: int = 10) -> List[Match]:
        """Preview contractions in the text with context."""
        matches = []
        text_len = len(text)
        
        for match in self.pattern.finditer(text):
            start_idx = max(0, match.start() - context_size)
            end_idx = min(text_len, match.end() + context_size)
            context = text[start_idx:end_idx]
            matched_text = match.group(0)
            replacement = self.combined_dict.get(matched_text.lower(), matched_text)
            
            matches.append(Match(
                text=matched_text,
                start=match.start(),
                end=match.end(),
                replacement=replacement,
                context=context
            ))
        return matches

    def add_contraction(self, contraction: str, expansion: str) -> None:
        """Add a new contraction to the dictionary with optimized updates."""
        with self._lock:
            contraction_lower = contraction.lower()
            expansion_lower = expansion.lower()
            
            # Update dictionaries
            self.combined_dict[contraction_lower] = expansion
            alt_contraction = contraction_lower.replace("'", "'")
            self.combined_dict[alt_contraction] = expansion
            
            # Update reverse dict if applicable
            if "'" in contraction_lower and len(contraction_lower) > 1:
                existing = self.reverse_dict.get(expansion_lower)
                if existing is None or len(contraction_lower) < len(existing):
                    self.reverse_dict[expansion_lower] = contraction_lower
            
            # Clear cached properties and update tuples
            self._pattern = None
            self._reverse_pattern = None
            
            # Clear function caches
            self._fix_single_optimized.cache_clear()
            self._contract_single_optimized.cache_clear()
            
            # Update tuple versions
            self._dict_tuple = tuple(self.combined_dict.items())
            self._reverse_dict_tuple = tuple(self.reverse_dict.items())

    def remove_contraction(self, contraction: str) -> None:
        """Remove a contraction from the dictionary with optimized updates."""
        with self._lock:
            contraction_lower = contraction.lower()
            
            # Get expansion before removal
            expansion = self.combined_dict.get(contraction_lower)
            
            # Remove from dictionaries
            self.combined_dict.pop(contraction_lower, None)
            self.combined_dict.pop(contraction_lower.replace("'", "'"), None)
            
            # Update reverse dict
            if expansion and expansion.lower() in self.reverse_dict:
                if self.reverse_dict[expansion.lower()] == contraction_lower:
                    del self.reverse_dict[expansion.lower()]
            
            # Clear cached properties
            self._pattern = None
            self._reverse_pattern = None
            
            # Clear function caches
            self._fix_single_optimized.cache_clear()
            self._contract_single_optimized.cache_clear()
            
            # Update tuple versions
            self._dict_tuple = tuple(self.combined_dict.items())
            self._reverse_dict_tuple = tuple(self.reverse_dict.items()) 