import re

def normalize_copyright_symbols(text):
    """
    Replace [C] or [c] with (C) to ensure proper copyright detection.
    """
    # Replace [C] or [c] with (C)
    text = re.sub(r'\[C\]', '(C)', text, flags=re.IGNORECASE)
    return text
