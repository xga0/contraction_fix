# Contraction Fix

[![PyPI version](https://img.shields.io/pypi/v/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![Python Versions](https://img.shields.io/pypi/pyversions/contraction-fix.svg)](https://pypi.org/project/contraction-fix/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A fast and efficient Python library for fixing contractions in English text. Expand contractions like "can't" → "cannot" or contract expanded forms like "cannot" → "can't" with high performance and accuracy.

## Installation

```bash
pip install contraction-fix
```

## Quick Start

### Expand Contractions

```python
from contraction_fix import fix

text = "I can't believe it's not butter!"
result = fix(text)
print(result)  # "I cannot believe it is not butter!"
```

### Contract Expanded Forms

```python
from contraction_fix import contract

text = "I cannot believe it is not butter!"
result = contract(text)
print(result)  # "I can't believe it's not butter!"
```

### Batch Processing

```python
from contraction_fix import fix_batch, contract_batch

texts = ["I can't go", "They're here", "We'll see"]
expanded = fix_batch(texts)
# ["I cannot go", "They are here", "We will see"]

contracted = contract_batch(["I cannot go", "They are here", "We will see"])
# ["I can't go", "They're here", "We'll see"]
```

## Key Features

- **Bidirectional processing**: Expand contractions or contract expanded forms
- **High performance**: Optimized with precompiled regex patterns and LRU caching
- **Batch processing**: Process multiple texts efficiently
- **Smart detection**: Distinguishes between contractions and possessives
- **Configurable**: Support for standard, informal, and internet slang
- **Thread-safe**: Safe for concurrent usage
- **Extensible**: Add or remove custom contractions

## Configuration

```python
from contraction_fix import ContractionFixer

# Custom configuration
fixer = ContractionFixer(
    use_informal=True,   # Include "gonna" → "going to"
    use_slang=False,     # Exclude "lol" → "laugh out loud"
    cache_size=2048      # Larger cache for better performance
)

result = fixer.fix("I'm gonna see y'all later")
# "I am going to see you all later"
```

## Dictionary Types

- **Standard**: Common contractions like "can't" → "cannot"
- **Informal**: Casual forms like "gonna" → "going to"
- **Internet Slang**: Modern abbreviations like "btw" → "by the way"

## Smart Processing

The library intelligently preserves possessives while expanding contractions:

```python
text = "I can't find Sarah's keys, and she won't be there."
result = fix(text)
# "I cannot find Sarah's keys, and she will not be there."
```

## Documentation

For complete documentation, API reference, advanced usage examples, and performance tips, see [README_FULL.md](README_FULL.md).

## Contributing

Contributions are welcome! Please submit a Pull Request with tests for new functionality.

## License

MIT License - see the LICENSE file for details.