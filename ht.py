from licensedcode.cache import get_index
idx = get_index()
file= "sample.license.txt"
matches = idx.match(location=file)
for match in matches:
    ht = match.get_highlighted_text()
    print(ht)
