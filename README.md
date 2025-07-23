# Contraction Fix

[![PyPI version](https://img.shields.io/pypi/v/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![Python Versions](https://img.shields.io/pypi/pyversions/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fast and efficient Python library for fixing contractions in English text. Expand contractions like "can't" → "cannot" or contract expanded forms like "cannot" → "can't" with high performance and accuracy.

## Features

- **Bidirectional processing**: Expand contractions or contract expanded forms
- **High performance**: Optimized with precompiled regex patterns and LRU caching
- **Batch processing**: Efficiently process multiple texts at once
- **Smart detection**: Distinguishes between contractions and possessives
- **Configurable dictionaries**: Support for standard, informal, and internet slang
- **Thread-safe**: Safe for concurrent usage
- **Extensible**: Add or remove custom contractions
- **Preview mode**: See what changes will be made before applying them

## Installation

```bash
pip install contraction-fix
```

## Quick Start

### Expanding Contractions

```python
from contraction_fix import fix

text = "I can't believe it's not butter!"
result = fix(text)
print(result)  # "I cannot believe it is not butter!"
```

### Contracting Expanded Forms

```python
from contraction_fix import contract

text = "I cannot believe it is not butter!"
result = contract(text)
print(result)  # "I can't believe it's not butter!"
```

## Core Functionality

### Single Text Processing

```python
from contraction_fix import fix, contract

# Expand contractions
expanded = fix("I'd like to see y'all tomorrow")
print(expanded)  # "I would like to see you all tomorrow"

# Contract expanded forms
contracted = contract("I would like to see you all tomorrow")
print(contracted)  # "I'd like to see y'all tomorrow"
```

### Batch Processing

For processing multiple texts efficiently:

```python
from contraction_fix import fix_batch, contract_batch

texts = [
    "I can't believe it's working!",
    "They're going to the store",
    "We'll see what happens"
]

# Expand all texts
expanded = fix_batch(texts)
print(expanded)
# ["I cannot believe it is working!", "They are going to the store", "We will see what happens"]

# Contract all texts
contracted = contract_batch([
    "I cannot believe it is working!",
    "They are going to the store", 
    "We will see what happens"
])
print(contracted)
# ["I can't believe it's working!", "They're goin' to the store", "We'll see what happens"]
```

### Smart Contraction Detection

The library intelligently distinguishes between contractions and possessive forms:

```python
from contraction_fix import fix

text = "I can't find Sarah's keys, and she won't be at her brother's house until it's dark."
result = fix(text)
print(result)
# "I cannot find Sarah's keys, and she will not be at her brother's house until it is dark."
```

Notice how:
- Contractions are expanded: "can't" → "cannot", "won't" → "will not", "it's" → "it is"
- Possessives are preserved: "Sarah's" and "brother's" remain unchanged

## Advanced Usage

### Custom Configuration

```python
from contraction_fix import ContractionFixer

# Create a custom fixer with specific settings
fixer = ContractionFixer(
    use_informal=True,   # Include informal contractions like "gonna", "goin'"
    use_slang=False,     # Exclude internet slang like "lol", "brb"
    cache_size=2048      # Increase cache size for better performance
)

text = "I'm gonna see y'all later, brb"
result = fixer.fix(text)
print(result)  # "I am going to see you all later, brb"
# Note: "brb" is preserved because use_slang=False
```

### Preview Changes

See what changes will be made before applying them:

```python
from contraction_fix import ContractionFixer

fixer = ContractionFixer()
text = "I can't believe it's working!"

matches = fixer.preview(text, context_size=5)
for match in matches:
    print(f"Found '{match.text}' at position {match.start}")
    print(f"Context: '{match.context}'")
    print(f"Will replace with: '{match.replacement}'")
    print()
```

### Custom Contractions

Add or remove contractions dynamically:

```python
from contraction_fix import ContractionFixer

fixer = ContractionFixer()

# Add custom contraction
fixer.add_contraction("lemme", "let me")
print(fixer.fix("lemme know"))  # "let me know"

# Remove existing contraction
fixer.remove_contraction("won't")
print(fixer.fix("I won't go"))  # "I won't go" (unchanged)
```

## Dictionary Types

The library uses three configurable dictionary types:

### Standard Contractions
Common English contractions like:
- "can't" → "cannot"
- "won't" → "will not"
- "it's" → "it is"
- "they're" → "they are"

### Informal Contractions
Less formal patterns like:
- "gonna" → "going to"
- "goin'" → "going"
- "doin'" → "doing"
- "nothin'" → "nothing"

### Internet Slang
Modern abbreviations like:
- "btw" → "by the way"
- "lol" → "laugh out loud"
- "idk" → "I do not know"
- "tbh" → "to be honest"

## Performance

The library is highly optimized for speed and efficiency:

- **Precompiled regex patterns** with intelligent grouping
- **LRU caching** for repeated inputs (configurable cache size)
- **Efficient data structures** using frozensets and slots
- **Batch processing optimization** for multiple texts
- **Memory efficient** with minimal allocations
- **Thread-safe operations** with proper locking

### Performance Best Practices

```python
from contraction_fix import fix_batch, ContractionFixer

# ✅ Efficient: Use batch processing for multiple texts
texts = ["I can't go", "They're here", "We'll see"]
results = fix_batch(texts)

# ✅ Efficient: Reuse fixer instance
fixer = ContractionFixer()
results = [fixer.fix(text) for text in texts]

# ❌ Less efficient: Individual function calls
results = [fix(text) for text in texts]
```

## Configuration Options

### ContractionFixer Parameters

- **`use_informal: bool = True`**
  - Include informal contractions like "gonna" → "going to"
  - Set to `False` for formal text processing

- **`use_slang: bool = True`**
  - Include internet slang like "brb" → "be right back"
  - Set to `False` for academic or professional applications

- **`cache_size: int = 1024`**
  - LRU cache size for memoization
  - Increase for better performance with repeated inputs
  - Decrease to reduce memory usage

### Example Configurations

```python
from contraction_fix import ContractionFixer

# Formal text processing
formal_fixer = ContractionFixer(use_informal=False, use_slang=False)

# High performance setup
fast_fixer = ContractionFixer(cache_size=4096)

# Memory conservative setup
light_fixer = ContractionFixer(cache_size=256)
```

## API Reference

### Package Functions

```python
# Expansion functions
fix(text: str, use_informal: bool = True, use_slang: bool = True) -> str
fix_batch(texts: List[str], use_informal: bool = True, use_slang: bool = True) -> List[str]

# Contraction functions
contract(text: str, use_informal: bool = True, use_slang: bool = True) -> str
contract_batch(texts: List[str], use_informal: bool = True, use_slang: bool = True) -> List[str]
```

### ContractionFixer Class

```python
class ContractionFixer:
    def __init__(self, use_informal: bool = True, use_slang: bool = True, cache_size: int = 1024)
    
    # Core methods
    def fix(self, text: str) -> str
    def fix_batch(self, texts: List[str]) -> List[str]
    def contract(self, text: str) -> str
    def contract_batch(self, texts: List[str]) -> List[str]
    
    # Utility methods
    def preview(self, text: str, context_size: int = 10) -> List[Match]
    def add_contraction(self, contraction: str, expansion: str) -> None
    def remove_contraction(self, contraction: str) -> None
```

### Match Class

```python
@dataclass
class Match:
    text: str          # The matched contraction
    start: int         # Start position in original text
    end: int           # End position in original text
    replacement: str   # What it will be replaced with
    context: str       # Surrounding context
```

## Examples

### Text Preprocessing Pipeline

```python
from contraction_fix import ContractionFixer

def preprocess_text(text: str) -> str:
    """Example preprocessing pipeline"""
    fixer = ContractionFixer(use_slang=False)  # Formal processing
    
    # Expand contractions for consistent analysis
    expanded = fixer.fix(text)
    
    # Your other preprocessing steps here
    # (tokenization, lowercasing, etc.)
    
    return expanded

# Usage
raw_text = "I can't believe it's working! They're awesome."
processed = preprocess_text(raw_text)
print(processed)  # "I cannot believe it is working! They are awesome."
```

### Chat Message Processing

```python
from contraction_fix import ContractionFixer

def normalize_chat_message(message: str) -> str:
    """Normalize casual chat messages"""
    fixer = ContractionFixer(use_informal=True, use_slang=True)
    
    # Expand everything for consistent processing
    return fixer.fix(message)

# Usage
chat_msg = "hey btw, i can't make it tonight lol"
normalized = normalize_chat_message(chat_msg)
print(normalized)  # "hey by the way, I cannot make it tonight laugh out loud"
```

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request. Make sure to:

1. Add tests for new functionality
2. Update documentation as needed
3. Follow the existing code style
4. Ensure all tests pass

## License

This project is licensed under the MIT License - see the LICENSE file for details. 