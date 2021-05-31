#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#
import csv

from pathlib import Path
import os

from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import OUTPUT_GROUP
from plugincode.output import output_impl
from plugincode.output import OutputPlugin

from formattedcode import FileOptionType

# Tracing flags
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import sys
    import logging

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str)
                                     and a or repr(a) for a in args))


@output_impl
class CcsvOutput(OutputPlugin):

    options = [
        PluggableCommandLineOption(('--ccsv',),
            type=FileOptionType(mode='w', encoding='utf-8', lazy=True),
            metavar='FILE',
            help='Write scan output as CCSV to FILE.',
            help_group=OUTPUT_GROUP,
            sort_order=30),
    ]

    def is_enabled(self, ccsv, **kwargs):
        return ccsv

    def process_codebase(self, codebase, ccsv, **kwargs):
        results = self.get_files(codebase, **kwargs)
        write_csv(results, ccsv)


def write_csv(results, output_file):
    results = list(results)

    headers = dict([
        ('info', []),
        ('license_expression', []),
        ('license', []),
        ('copyright', []),
        ('email', []),
        ('url', []),
        ('package', []),
    ])

    flatten_scan(results, headers, output_file)    


def flatten_scan(scan, headers, output_file):
    """
    Flattening the sequence data in a single line-separated value and keying always by path,
    given a ScanCode `scan` results list.
    """
    
    mainlist = []
    parent_dict = {}
    keys=[]
    fg_val=0
    i = 0
    
    for scanned_file in scan:
        for k, v in scanned_file.items():
            if k == "path":
                keys.insert(i, "path")
                newlist = dict()
                newlist['path']=v
                path_value = v
            elif k == "type":
                i+=1
                keys.insert(i, "type")
                newlist['type']=v
                if v=="directory":
                    fg_val+=1
                #keys.insert(2, "folder_group")
                newlist['folder_group']=fg_val
                parent_dict[path_value] = fg_val
            '''elif k == "folder_group":
                keys.insert(2, "folder_group")
                newlist['folder_group']=v
                parent_dict[path_value] = v'''
            parentpath = Path(path_value)
            key = str(parentpath.parent)
            if key != '.':
                key = key.replace("\\","/")
                newlist['parent_group'] = parent_dict[key]
                #keys.insert(3, "parent_group")
            if type(v) is list:
                if k == "licenses":
                    for val1 in v:
                        if isinstance(val1, dict):
                            for keyname,keyvalue in val1.items():
                                keyvalue = str(keyvalue)
                                keyvalue = keyvalue.replace(',','')
                                if keyname == "name":
                                    i+=1
                                    keys.insert(i, "license_name")
                                    if 'license_name' in newlist.keys():
                                        if keyvalue not in newlist.get('license_name'):
                                            templist = newlist['license_name']
                                            keyvalue = ", ".join([templist, keyvalue])
                                            newlist['license_name']=keyvalue
                                    else:
                                        newlist['license_name']=keyvalue
                                elif keyname == "text_url" and keyvalue!="":
                                    i+=1
                                    keys.insert(i, "license_text_url")
                                    if 'license_text_url' in newlist.keys():
                                        if keyvalue not in newlist.get('license_text_url'):
                                            templist = newlist['license_text_url']
                                            keyvalue = ", ".join([templist, keyvalue])
                                            newlist['license_text_url']=keyvalue
                                    else:
                                        newlist['license_text_url']=keyvalue
                elif k == "copyrights":
                    for val1 in v:
                        if isinstance(val1, dict):
                            for keyname,keyvalue in val1.items():
                                keyvalue = str(keyvalue)
                                keyvalue = keyvalue.replace(',','')
                                if keyname == "value":
                                    i+=1
                                    keys.insert(i, "copyright")
                                    if 'copyright' in newlist.keys():
                                        if keyvalue not in newlist.get('copyright'):
                                            templist = newlist['copyright']
                                            keyvalue = ", ".join([templist, keyvalue])
                                            newlist['copyright']=keyvalue
                                    else:
                                        newlist['copyright']=keyvalue
                elif k=="packages":
                    for val1 in v:
                        if isinstance(val1, dict):
                            for keyname,keyvalue in val1.items():
                                if keyname == "name":
                                    i+=1
                                    keys.insert(i, "package_name")
                                    newlist['package_name']=keyvalue
                                elif keyname == "version":  
                                    i+=1
                                    keys.insert(i, "package_version")
                                    newlist['package_version']=keyvalue
                                elif keyname == "homepage_url":
                                    i+=1
                                    keys.insert(i, "package_homepage_url")
                                    newlist['package_homepage_url']=keyvalue
                elif k=="urls":
                    for val1 in v:
                        if isinstance(val1, dict):
                            for keyname,keyvalue in val1.items():
                                if keyname == "url":
                                    i+=1
                                    keys.insert(i, "url")
                                    if 'url' in newlist.keys():
                                        if keyvalue not in newlist.get('url'):
                                            templist = newlist['url']
                                            keyvalue = ", ".join([templist, keyvalue])
                                            newlist['url']=keyvalue
                                    else:
                                        newlist['url']=keyvalue
        mainlist.append(newlist)  

    previouspath=''
    previous_packagename=''
    previous_packageversion=''
    previous_packageurl=''
    flag=0
    
    """get the previous path's package name and version"""
    for templist in mainlist: 
        if (templist['type'] == "directory") and ('package_name' not in templist.keys()) and (previouspath in templist['path']) and not templist['path'].endswith("node_modules"):
            if previous_packagename:
                templist['package_name'] = previous_packagename
                templist['package_version'] = previous_packageversion
                templist['package_homepage_url'] = previous_packageurl
                flag=1
        else:
            flag=0 
        if templist['type'] == "directory" and ('package_name' in templist.keys()) and flag==0:
            previouspath = templist['path']
            previous_packagename = templist['package_name']
            previous_packageversion = templist['package_version']
            previous_packageurl = templist['package_homepage_url']
    
    """to print package name matching the folder group"""
    for sublist in mainlist:
        strippedpath, tail = os.path.split(sublist['path'])
        if (sublist['type'] == "directory") and ('package_name' not in sublist.keys()) and not sublist['path'].endswith("node_modules"):
            for templist in mainlist: 
                if templist['path']==strippedpath and 'package_name' in templist.keys():
                    sublist['package_name'] = templist['package_name']
                    sublist['package_version'] = templist['package_version']
                    sublist['package_homepage_url'] = templist['package_homepage_url']
                    
        if 'package_name' in sublist.keys():
            fldr_grp = sublist['folder_group']
            for templist in mainlist:
                if templist['folder_group'] == fldr_grp and 'package_name' not in templist.keys():
                    templist['package_name'] = sublist['package_name']
                    templist['package_version'] = sublist['package_version']
                    templist['package_homepage_url'] = sublist['package_homepage_url']

    mainlist_modified = []
    for sublist in mainlist:
        sublist_modified={}
        for k1, v1 in sublist.items():
            if k1 not in ['folder_group','parent_group']:
                sublist_modified[k1]=v1
        mainlist_modified.append(sublist_modified)

    """to print in csv file"""
    keys_list = []
    for x in keys:
        if x not in keys_list:
            keys_list.append(x)     
    w = csv.DictWriter(output_file, keys_list) 
    w.writeheader()
    w.writerows(mainlist_modified)        
