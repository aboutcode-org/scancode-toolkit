#!/bin/bash
# halt script on error
set -e
# Check for Style Code Violations
doc8 --max-line-length 100 source --ignore D000 --quiet