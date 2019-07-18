#### DESCRIPTION

A ScanCode scan plugin to generate fingerprints using Simhash algorithm. The Simhash algorithm is a dimensionality 
reduction technique. It maps high-dimensional vectors to small-sized fingerprints. 

Shingles are consecutive overlapping sequences of letters. By using these instead of the words directly, we can get an 
idea about how the words are related to each other. Each shingle has its own fingerprint, which can be used to compare 
the similarity between two shingles. The fingerprint is basically a hash with the property that relatively similar 
values will be hashed to relatively similar hashes. After the hashes are computed we use hamming distance algorithm to 
find the similarity between two files.

#### USAGE
`scancode -f --<output_formats> <output_file > <input_directory>`

#### Example
* Scan the `samples/` directory for generating fingerprint.
* Save scan results to the `scancode_result.json` JSON file.
* command : `scancode -f --json-pp scancode_result.json samples`