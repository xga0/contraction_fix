from typing import List
from .fixer import ContractionFixer

_default_fixer = ContractionFixer()

def fix(text: str, use_informal: bool = True, use_slang: bool = True) -> str:
    """Fix contractions in the given text using the default settings.
    
    Args:
        text: The text to fix
        use_informal: Whether to use the informal contractions dictionary
        use_slang: Whether to use the internet slang dictionary
        
    Returns:
        The text with contractions fixed
    """
    if use_informal and use_slang:
        return _default_fixer.fix(text)
    else:
        fixer = ContractionFixer(use_informal=use_informal, use_slang=use_slang)
        return fixer.fix(text)

def fix_batch(texts: List[str], use_informal: bool = True, use_slang: bool = True) -> List[str]:
    """Fix contractions in multiple texts efficiently.
    
    Args:
        texts: List of texts to process
        use_informal: Whether to use the informal contractions dictionary
        use_slang: Whether to use the internet slang dictionary
        
    Returns:
        List of texts with contractions fixed
    """
    if use_informal and use_slang:
        return _default_fixer.fix_batch(texts)
    else:
        fixer = ContractionFixer(use_informal=use_informal, use_slang=use_slang)
        return fixer.fix_batch(texts)

def contract(text: str, use_informal: bool = True, use_slang: bool = True) -> str:
    """Contract expanded forms back to contractions in the given text.
    
    Args:
        text: The text to contract
        use_informal: Whether to use the informal contractions dictionary
        use_slang: Whether to use the internet slang dictionary
        
    Returns:
        The text with expanded forms contracted back to contractions
    """
    if use_informal and use_slang:
        return _default_fixer.contract(text)
    else:
        fixer = ContractionFixer(use_informal=use_informal, use_slang=use_slang)
        return fixer.contract(text)

def contract_batch(texts: List[str], use_informal: bool = True, use_slang: bool = True) -> List[str]:
    """Contract expanded forms back to contractions in multiple texts efficiently.
    
    Args:
        texts: List of texts to process
        use_informal: Whether to use the informal contractions dictionary
        use_slang: Whether to use the internet slang dictionary
        
    Returns:
        List of texts with expanded forms contracted back to contractions
    """
    if use_informal and use_slang:
        return _default_fixer.contract_batch(texts)
    else:
        fixer = ContractionFixer(use_informal=use_informal, use_slang=use_slang)
        return fixer.contract_batch(texts)

__version__ = "0.2.2"
__all__ = ["fix", "fix_batch", "contract", "contract_batch", "ContractionFixer"] 