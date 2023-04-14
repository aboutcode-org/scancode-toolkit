#!/bin/bash
# halt script on error
set -e

# Path to the available packages doc
DOC_PATH="source/reference/available_package_parsers.rst"

# Regen docs for available package parsers
regen-package-docs --path "$DOC_PATH"

# Delete whitespace from last line to not fail doc8 tests
sed -i '$ d' "$DOC_PATH"