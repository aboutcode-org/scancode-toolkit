import urllib.request
import licensedcode.index
import json
from licensedcode.cache import get_index
from licensedcode.models import load_licenses
from licensedcode.models import Rule
from licensedcode.models import rules_data_dir

def findOSIMap(license):
    """
    Return Scancode key mapped to OSI License `license`
    """
    idx = get_index()
    osiKey = license['id']
    matches = list(idx.match(query_string = osiKey))
    if not matches:
        return None
    return matches[0].rule.license_expression, osiKey

def addOSIKey(obj):
    """
    Add OSI License Key to licenses found to have a Scancode key matching an OSI key
    """
    licenses = licensedcode.cache.get_licenses_db()
    result, osiKey = findOSIMap(obj)
    if not result:
        return None
    mappedLicense = licenses[result] # license object from Scancode 
    # modify this license to have an OSI Key
    # mappedLicense.osi_license_key = osiKey
    # throws attribute error
    
def addOSIKeys():
    """
    For every possible OSI License, match and add OSI Key to exiting Scancode License
    """
    contents = urllib.request.urlopen("https://api.opensource.org/licenses/").read().decode()
    data = json.loads(contents)
    for obj in data:
        addOSIKey(obj)
    

if __name__ == '__main__':
    addOSIKeys()