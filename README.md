# Contraction Fix

[![PyPI version](https://img.shields.io/pypi/v/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![Python Versions](https://img.shields.io/pypi/pyversions/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fast and efficient library for fixing contractions in text. This package provides tools to expand contractions in English text while maintaining high performance and accuracy. **NEW in v0.2.1: Reverse functionality to contract expanded forms back to contractions!**

## Features

- Fast text processing using precompiled regex patterns
- **Batch processing for multiple texts with optimized performance**
- **NEW: Reverse functionality to contract expanded forms back to contractions**
- Support for standard contractions, informal contractions, and internet slang
- Configurable dictionary usage
- Optimized caching for improved performance
- Preview functionality to see contractions before fixing
- Easy addition and removal of custom contractions
- Thread-safe operations

## Installation

```bash
pip install contraction-fix
```

## Usage

### Basic Usage

#### Expanding Contractions

```python
from contraction_fix import fix

text = "I can't believe it's not butter!"
fixed_text = fix(text)
print(fixed_text)  # "I cannot believe it is not butter!"
```

#### Contracting Expanded Forms (NEW!)

```python
from contraction_fix import contract

text = "I cannot believe it is not butter!"
contracted_text = contract(text)
print(contracted_text)  # "I can't believe it's not butter!"
```

### Batch Processing

#### Expanding Contractions in Batch

For processing multiple texts efficiently:

```python
from contraction_fix import fix_batch

texts = [
    "I can't believe it's working!",
    "They're going to the store",
    "We'll see what happens"
]

fixed_texts = fix_batch(texts)
print(fixed_texts)
# Output: ["I cannot believe it is working!", "They are going to the store", "We will see what happens"]
```

#### Contracting Expanded Forms in Batch (NEW!)

```python
from contraction_fix import contract_batch

texts = [
    "I cannot believe it is working!",
    "They are going to the store", 
    "We will see what happens"
]

contracted_texts = contract_batch(texts)
print(contracted_texts)
# Output: ["I can't believe it's working!", "They're goin' to the store", "We'll see what happens"]
```

### Instantiating `ContractionFixer`

Start by creating an instance of the `ContractionFixer` class:

```python
from contraction_fix import ContractionFixer

fixer = ContractionFixer()
```

### Optional Parameters:

- **`use_informal: bool = True`**
    
    - Enables informal contractions like `"gonna"` → `"going to"`.
        
    - Set to `False` to avoid informal style expansions.
        
- **`use_slang: bool = True`**
    
    - Enables slang contractions like `"brb"` → `"be right back"`.
        
    - Set to `False` for more formal or academic applications.
        
- **`cache_size: int = 1024`**
    
    - Sets the LRU cache size for memoization. Improves performance when processing repeated inputs.
        

#### Example – Disabling slang:

```python
fixer = ContractionFixer(use_slang=False)
print(fixer.fix("brb, idk what's up"))  
# Output: "brb, I don't know what is up"  (brb is skipped because use_slang=False)
```

### Contractions vs. Possessives

The package intelligently differentiates between contractions and possessive forms:

```python
from contraction_fix import fix

text = "I can't find Sarah's keys, and she won't be at her brother's house until it's dark."
fixed_text = fix(text)
print(fixed_text)  # "I cannot find Sarah's keys, and she will not be at her brother's house until it is dark."
```

Notice how the package:
- Expands contractions: "can't" → "cannot", "won't" → "will not", "it's" → "it is"
- Preserves possessives: "Sarah's" and "brother's" remain unchanged

### Advanced Usage

```python
from contraction_fix import ContractionFixer

# Create a custom fixer instance
fixer = ContractionFixer(use_informal=True, use_slang=False)

# Fix single text
text = "I'd like to see y'all tomorrow"
fixed_text = fixer.fix(text)
print(fixed_text)  # "I would like to see you all tomorrow"

# Contract single text (NEW!)
expanded_text = "I would like to see you all tomorrow"
contracted_text = fixer.contract(expanded_text)
print(contracted_text)  # "I would like to see y'all tomorrow"

# Fix multiple texts efficiently
texts = [
    "I can't believe it's working",
    "They're going home",
    "We'll see what happens"
]
fixed_texts = fixer.fix_batch(texts)
print(fixed_texts)  # ["I cannot believe it is working", "They are going home", "We will see what happens"]

# Contract multiple texts efficiently (NEW!)
expanded_texts = [
    "I cannot believe it is working",
    "They are going home",
    "We will see what happens"
]
contracted_texts = fixer.contract_batch(expanded_texts)
print(contracted_texts)  # ["I can't believe it's working", "They're goin' home", "We'll see what happens"]

# Preview contractions
matches = fixer.preview(text, context_size=5)
for match in matches:
    print(f"Found '{match.text}' at position {match.start}")
    print(f"Context: '{match.context}'")
    print(f"Will be replaced with: '{match.replacement}'")

# Add custom contraction
fixer.add_contraction("gonna", "going to")

# Remove contraction
fixer.remove_contraction("won't")
```

## Dictionary Types

The package uses three types of dictionaries:

1. **Standard Contractions**: Common English contractions like "can't", "won't", etc.
2. **Informal Contractions**: Less formal contractions and patterns like "goin'", "doin'", etc.
3. **Internet Slang**: Modern internet slang and abbreviations like "lol", "btw", etc.

## Performance

The package is optimized for speed through:
- Precompiled regex patterns with cached compilation
- LRU caching of results for repeated inputs
- Efficient dictionary lookups with optimized key ordering
- **Batch processing for multiple texts**
- Minimal memory usage with frozenset constants
- Thread-safe operations

### Batch Processing Performance

When processing multiple texts, use `fix_batch()` or `contract_batch()` for better performance:

```python
from contraction_fix import fix_batch, contract_batch

# More efficient for multiple texts
texts = ["I can't go", "They're here", "We'll see"]
results = fix_batch(texts)  # Uses shared cache and optimized processing

# For reverse processing
expanded_texts = ["I cannot go", "They are here", "We will see"]
results = contract_batch(expanded_texts)  # Uses shared cache and optimized processing

# Less efficient for multiple texts
results = [fix(text) for text in texts]  # Creates new instances
```

## API Reference

### Functions

- `fix(text: str, use_informal: bool = True, use_slang: bool = True) -> str`
- `fix_batch(texts: List[str], use_informal: bool = True, use_slang: bool = True) -> List[str]`
- `contract(text: str, use_informal: bool = True, use_slang: bool = True) -> str` **(NEW!)**
- `contract_batch(texts: List[str], use_informal: bool = True, use_slang: bool = True) -> List[str]` **(NEW!)**

### Classes

- `ContractionFixer(use_informal: bool = True, use_slang: bool = True, cache_size: int = 1024)`
  - `fix(text: str) -> str`
  - `fix_batch(texts: List[str]) -> List[str]`
  - `contract(text: str) -> str` **(NEW!)**
  - `contract_batch(texts: List[str]) -> List[str]` **(NEW!)**
  - `preview(text: str, context_size: int = 10) -> List[Match]`
  - `add_contraction(contraction: str, expansion: str) -> None`
  - `remove_contraction(contraction: str) -> None`

## What's New in v0.2.1

- **Reverse Functionality**: New `contract()` and `contract_batch()` methods to convert expanded forms back to contractions
- **Enhanced API**: Package-level convenience functions for reverse functionality
- **Comprehensive Testing**: Extensive test coverage for all new functionality
- **Improved Performance**: Optimizations for both expansion and contraction operations

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 