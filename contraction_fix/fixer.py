from typing import Dict, List, ClassVar, FrozenSet, Tuple, Pattern, Optional
import json
import pkgutil
from functools import lru_cache
import re
from threading import Lock

class Match:
    """Represents a contraction match with context information."""
    __slots__ = ('text', 'start', 'end', 'replacement', 'context')
    
    def __init__(self, text: str, start: int, end: int, replacement: str, context: str):
        self.text = text
        self.start = start
        self.end = end
        self.replacement = replacement
        self.context = context
    
    def __repr__(self) -> str:
        return f"Match(text={self.text!r}, start={self.start}, end={self.end}, replacement={self.replacement!r}, context={self.context!r})"

class ContractionFixer:
    # Pre-compiled frozensets for O(1) lookups
    CONTRACTION_BASES: ClassVar[FrozenSet[str]] = frozenset({
        'he', 'she', 'it', 'what', 'who', 'that', 'there', 'here', 'where',
        'when', 'why', 'how', 'this', 'everyone', 'somebody', 'someone',
        'something', 'nobody', 'let'
    })
    
    # Keep TIME_WORDS for test compatibility
    TIME_WORDS: ClassVar[FrozenSet[str]] = frozenset({
        'today', 'tomorrow', 'tonight', 'morning', 'evening', 'afternoon',
        'week', 'month', 'year', 'century', 'monday', 'tuesday', 'wednesday',
        'thursday', 'friday', 'saturday', 'sunday'
    })

    # Keep MONTHS for test compatibility
    MONTHS: ClassVar[Tuple[str, ...]] = (
        "january", "february", "march", "april", "june", "july",
        "august", "september", "october", "november", "december"
    )
    
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
        "I would have", "going to", "want to", "got to", "kind of"
    })
    
    # Pre-compiled safe informal contractions
    SAFE_INFORMAL: ClassVar[Dict[str, str]] = {
        "going": "goin'",
        "doing": "doin'", 
        "nothing": "nothin'"
    }

    __slots__ = ('_lock', 'combined_dict', 'reverse_dict', '_pattern', '_reverse_pattern', 
                 '_use_informal', '_use_slang', '_cache_size', '_fix_cache', '_contract_cache')

    def __init__(self, use_informal: bool = True, use_slang: bool = True, cache_size: int = 1024):
        """Initialize the contraction fixer with optional dictionaries."""
        self._lock = Lock()
        self._use_informal = use_informal
        self._use_slang = use_slang
        self._cache_size = cache_size
        self._pattern: Optional[Pattern[str]] = None
        self._reverse_pattern: Optional[Pattern[str]] = None
        self._fix_cache = None
        self._contract_cache = None
        
        try:
            # Load and build dictionaries efficiently
            self.combined_dict, self.reverse_dict = self._build_dictionaries()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ContractionFixer: {str(e)}")

    def _load_dict_optimized(self, filename: str) -> Dict[str, str]:
        """Load a dictionary from a JSON file with optimized processing."""
        try:
            data = pkgutil.get_data("contraction_fix", f"data/{filename}")
            if data is None:
                raise FileNotFoundError(f"Dictionary file {filename} not found")
            
            raw_dict = json.loads(data.decode("utf-8"))
            # Use dict comprehension for memory efficiency
            return {k.lower(): v for k, v in raw_dict.items()}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to load dictionary {filename}: {str(e)}")

    def _build_dictionaries(self) -> Tuple[Dict[str, str], Dict[str, str]]:
        """Build both dictionaries in a single pass for efficiency."""
        # Load base dictionaries
        standard = self._load_dict_optimized("standard_contractions.json")
        informal = self._load_dict_optimized("informal_contractions.json") if self._use_informal else {}
        slang = self._load_dict_optimized("internet_slang.json") if self._use_slang else {}
        
        # Build combined dictionary
        combined_dict = dict(standard)
        if self._use_informal:
            combined_dict.update(informal)
        if self._use_slang:
            combined_dict.update(slang)
        
        # Add alternative apostrophes in the same loop
        alt_entries = {}
        for k, v in combined_dict.items():
            if "'" in k:
                alt_entries[k.replace("'", "'")] = v
        combined_dict.update(alt_entries)
        
        # Build reverse dictionary efficiently
        reverse_dict = {}
        
        # Process standard contractions for reverse
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
        if self._use_informal:
            reverse_dict.update(self.SAFE_INFORMAL)
        
        # Add alternative apostrophes for reverse dict
        alt_reverse = {}
        for k, v in reverse_dict.items():
            if "'" in v:
                alt_reverse[k] = v.replace("'", "'")
        reverse_dict.update(alt_reverse)
        
        return combined_dict, reverse_dict

    @property
    def pattern(self) -> Pattern[str]:
        """Lazily compile and cache the regex pattern for matching contractions."""
        if self._pattern is not None:
            return self._pattern
            
        # Optimize pattern compilation with single regex construction
        sorted_keys = sorted(self.combined_dict.keys(), key=lambda x: (-len(x), x))
        
        # Build efficient pattern with word boundaries
        escaped_keys = [re.escape(key) for key in sorted_keys]
        
        # Use alternation with optimized word boundary detection
        apostrophe_pattern = '|'.join(k for k in escaped_keys if "'" in k or "'" in k)
        word_pattern = '|'.join(k for k in escaped_keys if "'" not in k and "'" not in k)
        
        pattern_parts = []
        if apostrophe_pattern:
            pattern_parts.append(f"(?<!\\w)(?:{apostrophe_pattern})(?!\\w)")
        if word_pattern:
            pattern_parts.append(f"\\b(?:{word_pattern})\\b")
        
        pattern_str = f"({'|'.join(pattern_parts)})" if pattern_parts else r'(?!.*)'
        self._pattern = re.compile(pattern_str, re.IGNORECASE)
        return self._pattern

    @property
    def reverse_pattern(self) -> Pattern[str]:
        """Lazily compile and cache the regex pattern for matching expanded forms."""
        if self._reverse_pattern is not None:
            return self._reverse_pattern
            
        # Optimize reverse pattern compilation
        sorted_keys = sorted(self.reverse_dict.keys(), key=lambda x: (-len(x), x))
        escaped_keys = [re.escape(key) for key in sorted_keys]
        
        pattern_str = f"\\b({'|'.join(escaped_keys)})\\b" if escaped_keys else r'(?!.*)'
        self._reverse_pattern = re.compile(pattern_str, re.IGNORECASE)
        return self._reverse_pattern

    def _is_contraction_s_optimized(self, word: str) -> bool:
        """Optimized contraction 's detection with early returns."""
        if len(word) < 3:
            return False
            
        base = word[:-2].lower()
        
        # Fast path: check base words that commonly form contractions
        if base in self.CONTRACTION_BASES:
            return True
            
        # Check ending patterns that typically don't form contractions
        if base.endswith(('s', 'x', 'z', 'ch', 'sh')):
            return False
        
        # Check if starts with uppercase (likely proper noun)
        return not word[0].isupper()

    def _fix_single_optimized(self, text: str) -> str:
        """Optimized single text fixing with reduced overhead."""
        # Initialize cache if needed
        if self._fix_cache is None:
            from functools import lru_cache
            self._fix_cache = lru_cache(maxsize=self._cache_size)(self._fix_single_impl)
        
        return self._fix_cache(text)
    
    def _fix_single_impl(self, text: str) -> str:
        """Implementation of single text fixing."""
        def replace_match(match):
            matched_text = match.group(0)
            
            # Fast path for 's contractions
            if matched_text.endswith(("'s", "'s")):
                if not self._is_contraction_s_optimized(matched_text):
                    return matched_text
            
            matched_lower = matched_text.lower()
            replacement = self.combined_dict.get(matched_lower)
            
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

    def _contract_single_optimized(self, text: str) -> str:
        """Optimized contracting with reduced overhead."""
        # Initialize cache if needed
        if self._contract_cache is None:
            from functools import lru_cache
            self._contract_cache = lru_cache(maxsize=self._cache_size)(self._contract_single_impl)
        
        return self._contract_cache(text)
    
    def _contract_single_impl(self, text: str) -> str:
        """Implementation of single text contracting."""
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
            self.combined_dict[contraction_lower.replace("'", "'")] = expansion
            
            # Update reverse dict if applicable
            if "'" in contraction_lower and len(contraction_lower) > 1:
                existing = self.reverse_dict.get(expansion_lower)
                if existing is None or len(contraction_lower) < len(existing):
                    self.reverse_dict[expansion_lower] = contraction_lower
            
            # Clear cached properties
            self._pattern = None
            self._reverse_pattern = None
            
            # Clear instance caches
            if self._fix_cache:
                self._fix_cache.cache_clear()
            if self._contract_cache:
                self._contract_cache.cache_clear()

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
            
            # Clear instance caches
            if self._fix_cache:
                self._fix_cache.cache_clear()
            if self._contract_cache:
                self._contract_cache.cache_clear() 