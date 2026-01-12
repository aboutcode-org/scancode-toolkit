"""
Unicode sanitizer for copyright/license scanning.

Handles surrogate ranges (U+D800–U+DFFF) and normalizes text to prevent
false positive "(c)" detection in scanners.
"""

import re
import unicodedata
from pathlib import Path


# Surrogate range: U+D800 to U+DFFF
SURROGATE_PATTERN = re.compile(r'[\uD800-\uDFFF]')

# Pattern that scanners might misinterpret as copyright symbol
FALSE_POSITIVE_PATTERNS = [
    (re.compile(r'\(c\)', re.IGNORECASE), '<PAREN_C>'),
    (re.compile(r'©'), '<COPYRIGHT>'),
]


def replace_surrogates(text: str, placeholder: str = '<SURROGATE>') -> str:
    """Replace surrogate code points with a safe placeholder."""
    return SURROGATE_PATTERN.sub(placeholder, text)


def normalize_unicode(text: str, form: str = 'NFC') -> str:
    """
    Normalize Unicode text to a canonical form.
    
    Args:
        text: Input text
        form: Normalization form ('NFC', 'NFD', 'NFKC', 'NFKD')
    
    Returns:
        Normalized text
    """
    return unicodedata.normalize(form, text)


def read_file_safe(filepath: str) -> str:
    """
    Read a file handling encoding errors gracefully.
    
    Uses 'surrogatepass' to preserve surrogate characters for detection,
    then 'replace' as fallback.
    """
    path = Path(filepath)
    
    # Try UTF-8 with surrogate pass first
    try:
        return path.read_text(encoding='utf-8', errors='surrogatepass')
    except UnicodeDecodeError:
        pass
    
    # Fallback: replace errors
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except UnicodeDecodeError:
        # Last resort: read as latin-1 (accepts any byte)
        return path.read_text(encoding='latin-1')


def sanitize_for_scanning(
    text: str,
    replace_surrogates_flag: bool = True,
    normalize: bool = True,
    normalization_form: str = 'NFC',
    surrogate_placeholder: str = '<SURROGATE>'
) -> str:
    """
    Sanitize text for copyright/license scanning.
    
    Args:
        text: Input text
        replace_surrogates_flag: Whether to replace surrogate ranges
        normalize: Whether to apply Unicode normalization
        normalization_form: Which normalization form to use
        surrogate_placeholder: Placeholder string for surrogates
    
    Returns:
        Sanitized text safe for scanning
    """
    result = text
    
    if replace_surrogates_flag:
        result = replace_surrogates(result, surrogate_placeholder)
    
    if normalize:
        result = normalize_unicode(result, normalization_form)
    
    return result


def sanitize_file(
    input_path: str,
    output_path: str = None,
    **kwargs
) -> str:
    """
    Sanitize a file for scanning.
    
    Args:
        input_path: Path to input file
        output_path: Path to output file (if None, returns string only)
        **kwargs: Arguments passed to sanitize_for_scanning()
    
    Returns:
        Sanitized text
    """
    text = read_file_safe(input_path)
    sanitized = sanitize_for_scanning(text, **kwargs)
    
    if output_path:
        Path(output_path).write_text(sanitized, encoding='utf-8')
    
    return sanitized


def contains_surrogates(text: str) -> bool:
    """Check if text contains surrogate code points."""
    return bool(SURROGATE_PATTERN.search(text))


def find_surrogate_positions(text: str) -> list:
    """Find all positions of surrogate characters in text."""
    return [(m.start(), m.end(), repr(m.group())) for m in SURROGATE_PATTERN.finditer(text)]


# CLI interface
if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(
        description='Sanitize Unicode files for copyright scanning'
    )
    parser.add_argument('input', help='Input file path')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--no-normalize', action='store_true',
                        help='Skip Unicode normalization')
    parser.add_argument('--no-replace-surrogates', action='store_true',
                        help='Skip surrogate replacement')
    parser.add_argument('--placeholder', default='<SURROGATE>',
                        help='Placeholder for surrogates')
    parser.add_argument('--check', action='store_true',
                        help='Only check for surrogates, do not modify')
    
    args = parser.parse_args()
    
    if args.check:
        text = read_file_safe(args.input)
        positions = find_surrogate_positions(text)
        if positions:
            print(f'Found {len(positions)} surrogate(s):')
            for start, end, char in positions[:10]:
                print(f'  Position {start}: {char}')
            if len(positions) > 10:
                print(f'  ... and {len(positions) - 10} more')
        else:
            print('No surrogates found.')
    else:
        result = sanitize_file(
            args.input,
            args.output,
            replace_surrogates_flag=not args.no_replace_surrogates,
            normalize=not args.no_normalize,
            surrogate_placeholder=args.placeholder
        )
        if not args.output:
            print(result)
