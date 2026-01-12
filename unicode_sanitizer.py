"""
Unicode sanitizer for copyright/license scanning.

Handles surrogate ranges (U+D800–U+DFFF) and normalizes text to prevent
false positive "(c)" detection in scanners.
"""

import re
import unicodedata
from pathlib import Path


SURROGATE_PATTERN = re.compile(r'[\uD800-\uDFFF]')


def replace_surrogates(text: str, placeholder: str = '<SURROGATE>') -> str:
    return SURROGATE_PATTERN.sub(placeholder, text)


def normalize_unicode(text: str, form: str = 'NFC') -> str:
    return unicodedata.normalize(form, text)


def read_file_safe(filepath: str) -> str:
    path = Path(filepath)
    try:
        return path.read_text(encoding='utf-8', errors='surrogatepass')
    except UnicodeDecodeError:
        pass
    try:
        return path.read_text(encoding='utf-8', errors='replace')
    except UnicodeDecodeError:
        return path.read_text(encoding='latin-1')


def sanitize_for_scanning(text: str, replace_surrogates_flag: bool = True,
                          normalize: bool = True, normalization_form: str = 'NFC',
                          surrogate_placeholder: str = '<SURROGATE>') -> str:
    result = text
    if replace_surrogates_flag:
        result = replace_surrogates(result, surrogate_placeholder)
    if normalize:
        result = normalize_unicode(result, normalization_form)
    return result


def sanitize_file(input_path: str, output_path: str = None, **kwargs) -> str:
    text = read_file_safe(input_path)
    sanitized = sanitize_for_scanning(text, **kwargs)
    if output_path:
        Path(output_path).write_text(sanitized, encoding='utf-8')
    return sanitized


def find_surrogate_positions(text: str) -> list:
    return [(m.start(), m.end(), repr(m.group())) for m in SURROGATE_PATTERN.finditer(text)]


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Sanitize Unicode files for copyright scanning')
    parser.add_argument('input', help='Input file path')
    parser.add_argument('-o', '--output', help='Output file path')
    parser.add_argument('--no-normalize', action='store_true')
    parser.add_argument('--no-replace-surrogates', action='store_true')
    parser.add_argument('--placeholder', default='<SURROGATE>')
    parser.add_argument('--check', action='store_true', help='Only check for surrogates')
    
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
            args.input, args.output,
            replace_surrogates_flag=not args.no_replace_surrogates,
            normalize=not args.no_normalize,
            surrogate_placeholder=args.placeholder
        )
        if not args.output:
            print(result)
