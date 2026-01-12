import json
import sys

def count_copyrights(scan_file):
    with open(scan_file, 'r', encoding='utf-8') as f:
        data = json.load(f)
    
    total = 0
    for file_entry in data.get('files', []):
        copyrights = file_entry.get('copyrights', [])
        total += len(copyrights)
    return total

if __name__ == '__main__':
    original = count_copyrights('original_scan.json')
    cleaned = count_copyrights('cleaned_scan.json')
    
    print(f'Original copyrights: {original}')
    print(f'Cleaned copyrights: {cleaned}')
    print(f'Difference: {original - cleaned}')
