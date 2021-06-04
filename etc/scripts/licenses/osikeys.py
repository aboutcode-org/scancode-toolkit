#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import json
import urllib.request

import licensedcode.cache
from licensedcode.cache import get_index
from licensedcode.models import load_licenses


def find_osi_map(license: "OSI License Object"):
    """
    Return Scancode key mapped to OSI License `license`
    """
    idx = get_index()
    osi_key = license['id']
    # search for Scancode License matching OSI Key
    matches = list(idx.match(query_string = osi_key))
    if not matches:
        return None
    return matches[0].rule.license_expression


def add_osi_key(obj: "OSI License Object"):
    """
    Add OSI License Key derived from OSI License Object `obj`
    """
    licenses = licensedcode.cache.get_licenses_db()
    # find matching Scancode License Object for `obj`
    result = find_osi_map(obj) 
    # derive OSI License Key from `obj`
    osi_key = obj['id'] 
    if not result: # no matching Scancode License found
        return None 
    mapped_license = licenses[result] # license object from Scancode
    licenses_path = "src/licensedcode/data/licenses/" # licenses directory
    file_to_modify = open(licenses_path + mapped_license.key + ".yml", "a")
    file_to_modify.write("osi_license_key: " + osi_key)
    file_to_modify.write("\n")


def add_osi_keys():
    """
    For every possible OSI License, match and add OSI Key to existing Scancode License
    """
    #retrieve OSI License Objects
    contents = urllib.request.urlopen("https://api.opensource.org/licenses/").read().decode()
    data = json.loads(contents)
    # for each OSI License Object, update matching Scancode License Object
    for obj in data:
        add_osi_key(obj)
    

if __name__ == '__main__':
    add_osi_keys()