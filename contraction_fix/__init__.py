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
    # Always create a new instance with the requested settings
    # This ensures thread safety and correct dictionary usage
    fixer = ContractionFixer(use_informal=use_informal, use_slang=use_slang)
    return fixer.fix(text)

__version__ = "0.1.10"
__all__ = ["fix", "ContractionFixer"] 