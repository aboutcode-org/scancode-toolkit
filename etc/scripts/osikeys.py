import urllib.request
import licensedcode.index
import json
from licensedcode.cache import get_index
from licensedcode.models import load_licenses
from licensedcode.models import Rule
from licensedcode.models import rules_data_dir


def find_osi_map(license: "OSI License Object"):
    """
    Return Scancode key mapped to OSI License `license`
    """
    idx = get_index()
    osi_key = license['id']
    matches = list(idx.match(query_string = osi_key))
    if not matches:
        return None
    return matches[0].rule.license_expression


def add_osi_key(obj: "OSI License Object"):
    """
    Add OSI License Key derived from OSI License Object `obj`
    """
    licenses = licensedcode.cache.get_licenses_db()
    result = find_osi_map(obj)
    osi_key = obj['id']
    if not result:
        return None
    mapped_license = licenses[result] # license object from Scancode 
    # modify this license to have an OSI Key
    # mapped_icense.osi_license_key = osi_key
    # throws attribute error
    

def add_osi_keys():
    """
    For every possible OSI License, match and add OSI Key to exiting Scancode License
    """
    contents = urllib.request.urlopen("https://api.opensource.org/licenses/").read().decode()
    data = json.loads(contents)
    for obj in data:
        add_osi_key(obj)
    

if __name__ == '__main__':
    add_osi_keys()