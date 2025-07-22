from typing import Dict, List, ClassVar, FrozenSet, Tuple, Pattern
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
            
            self.reverse_dict = {}
            
            safe_contractions = {
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
            }
            
            for contraction, expansion in standard.items():
                expansion_lower = expansion.lower()
                if expansion_lower in safe_contractions and "'" in contraction and len(contraction) > 2:
                    if expansion_lower not in self.reverse_dict:
                        self.reverse_dict[expansion_lower] = contraction
                    else:
                        existing = self.reverse_dict[expansion_lower]
                        if (not contraction.startswith("'") and existing.startswith("'")) or \
                           (len(contraction) < len(existing) and not contraction.startswith("'")):
                            self.reverse_dict[expansion_lower] = contraction
            
            if use_informal:
                safe_informal = {
                    "going": "goin'",
                    "doing": "doin'", 
                    "nothing": "nothin'"
                }
                for expansion, contraction in safe_informal.items():
                    if expansion not in self.reverse_dict:
                        self.reverse_dict[expansion] = contraction
            
            self._add_alt_apostrophes()
            
        except Exception as e:
            raise RuntimeError(f"Failed to initialize ContractionFixer: {str(e)}")

    def _load_dict(self, filename: str) -> Dict[str, str]:
        """Load a dictionary from a JSON file in the package data."""
        try:
            data = pkgutil.get_data("contraction_fix", f"data/{filename}")
            if data is None:
                raise FileNotFoundError(f"Dictionary file {filename} not found")
            raw_dict = json.loads(data.decode("utf-8"))
            return {k.lower(): v for k, v in raw_dict.items()}
        except json.JSONDecodeError as e:
            raise ValueError(f"Invalid JSON in {filename}: {str(e)}")
        except Exception as e:
            raise RuntimeError(f"Failed to load dictionary {filename}: {str(e)}")

    def _add_alt_apostrophes(self) -> None:
        """Add alternative apostrophe versions to the combined dictionary."""
        alt_contractions = {k.replace("'", "'"): v for k, v in self.combined_dict.items() if "'" in k}
        self.combined_dict.update(alt_contractions)

    @cached_property
    def pattern(self) -> Pattern[str]:
        """Lazily compile and cache the regex pattern for matching contractions."""
        sorted_keys = sorted(self.combined_dict.keys(), key=len, reverse=True)
        pattern_parts = []
        for key in sorted_keys:
            escaped = re.escape(key)
            if "'" in key:
                pattern_parts.append(r'(?<!\w)' + escaped + r'(?!\w)')
            else:
                pattern_parts.append(r'\b' + escaped + r'\b')
        
        return re.compile(
            '(' + '|'.join(pattern_parts) + ')',
            re.IGNORECASE
        )

    @cached_property
    def reverse_pattern(self) -> Pattern[str]:
        """Lazily compile and cache the regex pattern for matching expanded forms."""
        sorted_keys = sorted(self.reverse_dict.keys(), key=len, reverse=True)
        pattern_parts = [r'\b' + re.escape(key) + r'\b' for key in sorted_keys]
        
        return re.compile(
            '(' + '|'.join(pattern_parts) + ')',
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
            else:
                alt_text = matched_lower.replace("'", "'")
                if alt_text in self.combined_dict:
                    replacement = self.combined_dict[alt_text]
                else:
                    return matched_text
            
            if matched_text.isupper():
                return replacement.upper()
            elif matched_text[0].isupper():
                return replacement.capitalize()
            else:
                return replacement
                
        return self.pattern.sub(replace_match, text)

    @lru_cache(maxsize=1024)
    def _contract_single(self, text: str) -> str:
        """Contract expanded forms to contractions in a single text with caching."""
        def replace_match(match):
            matched_text = match.group(0)
            matched_lower = matched_text.lower()
            
            if matched_lower in self.reverse_dict:
                replacement = self.reverse_dict[matched_lower]
                
                if matched_text.isupper():
                    return replacement.upper()
                elif matched_text[0].isupper():
                    return replacement.capitalize()
                else:
                    return replacement
            
            return matched_text
                
        return self.reverse_pattern.sub(replace_match, text)

    def fix(self, text: str) -> str:
        """Fix contractions in the given text."""
        return self._fix_single(text)

    def fix_batch(self, texts: List[str]) -> List[str]:
        """Fix contractions in multiple texts efficiently."""
        return [self._fix_single(text) for text in texts]

    def contract(self, text: str) -> str:
        """Contract expanded forms back to contractions in the given text."""
        return self._contract_single(text)

    def contract_batch(self, texts: List[str]) -> List[str]:
        """Contract expanded forms back to contractions in multiple texts efficiently."""
        return [self._contract_single(text) for text in texts]

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
            contraction_lower = contraction.lower()
            expansion_lower = expansion.lower()
            
            self.combined_dict[contraction_lower] = expansion
            self.combined_dict[contraction_lower.replace("'", "'")] = expansion
            
            if "'" in contraction_lower and len(contraction_lower) > 1:
                if expansion_lower not in self.reverse_dict:
                    self.reverse_dict[expansion_lower] = contraction_lower
                elif len(contraction_lower) < len(self.reverse_dict[expansion_lower]):
                    self.reverse_dict[expansion_lower] = contraction_lower
            
            if hasattr(self, 'pattern'):
                delattr(self, 'pattern')
            if hasattr(self, 'reverse_pattern'):
                delattr(self, 'reverse_pattern')
            self._fix_single.cache_clear()
            self._contract_single.cache_clear()

    def remove_contraction(self, contraction: str) -> None:
        """Remove a contraction from the dictionary."""
        with self._lock:
            contraction_lower = contraction.lower()
            
            expansion = self.combined_dict.get(contraction_lower)
            
            self.combined_dict.pop(contraction_lower, None)
            self.combined_dict.pop(contraction_lower.replace("'", "'"), None)
            
            if expansion and expansion.lower() in self.reverse_dict:
                if self.reverse_dict[expansion.lower()] == contraction_lower:
                    del self.reverse_dict[expansion.lower()]
            
            if hasattr(self, 'pattern'):
                delattr(self, 'pattern')
            if hasattr(self, 'reverse_pattern'):
                delattr(self, 'reverse_pattern')
            self._fix_single.cache_clear()
            self._contract_single.cache_clear() 