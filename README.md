# Contraction Fix

[![PyPI version](https://img.shields.io/pypi/v/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![Python Versions](https://img.shields.io/pypi/pyversions/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fast and efficient library for fixing contractions in text. This package provides tools to expand contractions in English text while maintaining high performance and accuracy.

## Features

- Fast text processing using precompiled regex patterns
- Support for standard contractions, informal contractions, and internet slang
- Configurable dictionary usage
- Caching for improved performance
- Preview functionality to see contractions before fixing
- Easy addition and removal of custom contractions

## Installation

```bash
pip install contraction-fix
```

## Usage

### Basic Usage

```python
from contraction_fix import fix

text = "I can't believe it's not butter!"
fixed_text = fix(text)
print(fixed_text)  # "I cannot believe it is not butter!"
```

### Instantiating `ContractionFix`

Start by creating an instance of the `ContractionFix` class:

```python
from contraction_fix import ContractionFix

fixer = ContractionFix()
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
fixer = ContractionFix(use_slang=False)
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

# Fix text
text = "I'd like to see y'all tomorrow"
fixed_text = fixer.fix(text)
print(fixed_text)  # "I would like to see you all tomorrow"

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
- Precompiled regex patterns
- LRU caching of results
- Efficient dictionary lookups
- Minimal memory usage

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details. 