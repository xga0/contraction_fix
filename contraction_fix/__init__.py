from .fixer import ContractionFixer

# Create a default instance for convenience
default_fixer = ContractionFixer()

def fix(text: str, use_informal: bool = True, use_slang: bool = True) -> str:
    """Fix contractions in the given text using the default settings.
    
    Args:
        text: The text to fix
        use_informal: Whether to use the informal contractions dictionary
        use_slang: Whether to use the internet slang dictionary
        
    Returns:
        The text with contractions fixed
    """
    if use_informal == bool(default_fixer.informal) and use_slang == bool(default_fixer.slang):
        return default_fixer.fix(text)
    return ContractionFixer(use_informal, use_slang).fix(text)

__version__ = "0.1.8"
__all__ = ["fix"] 