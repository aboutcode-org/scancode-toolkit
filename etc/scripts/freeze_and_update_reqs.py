# -*- coding: utf-8 -*-
#
# Copyright (c) 2019 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.


from __future__ import absolute_import
from __future__ import print_function


import fnmatch
import hashlib
import io
import os
import re
import subprocess


os.chdir(os.pardir) #go to etc
os.chdir(os.pardir)  # go to scancode-toolkit
cwd = os.getcwd()
print("Current working directory:", cwd) 
fp = open("requirements.txt", "wb")
fp.close()


def is_package_exist_with_hashes(package_name,hash_of_file):
    """ Check if any line in the file contains package with same hashes """
    # Open the file in read only mode
    line_with_hash = package_name + " \\" + "\n" + "    --hash=sha256:"+ hash_of_file
    with open("requirements.txt", 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the package with same hashes
            if line_with_hash in line:
                return True
    return False

def is_package_exist_without_hashes(package_name):
    """ Check if any line in the file contains package without same hash """
    # Open the file in read only mode
    line_with_hash = package_name + " \\" + "\n" 
    with open("requirements.txt", 'r') as read_obj:
        # Read all lines in the file one by one
        for line in read_obj:
            # For each line, check if line contains the string
            if line_with_hash in line:
                return True
    return False


def add_package(package_name,hash_of_file):
    with open("requirements.txt", "a") as file_object:
    # Append package with hashes at the end of file
        line = package_name + " \\" + "\n" + "    --hash=sha256:"+ hash_of_file + " \n"
        file_object.write(line)

def append_requirement_file(package_name,hash_of_file):
    if is_package_exist_with_hashes(package_name,hash_of_file):
        return
    else:
        inputfile = open("requirements.txt", 'r').readlines()
        write_file = open("requirements.txt",'w')
        for line in inputfile:
            write_file.write(line)
            lion= package_name + " \\" + "\n"
            if lion in line:
                new_line = "    --hash=sha256:"+ hash_of_file + " \\"        
                write_file.write(new_line + "\n") 
        write_file.close()
        

def read_chunks(file, size=io.DEFAULT_BUFFER_SIZE):
    """Yield pieces of data from a file-like object until EOF."""
    while True:
        chunk = file.read(size)
        if not chunk:
            break
        yield chunk

def hash_of_file(path):
    # type: (str) -> str
    """Return the hash digest of a file."""
    with open(path, 'rb') as archive:
        hash = hashlib.new('sha256')
        for chunk in read_chunks(archive):
            hash.update(chunk)
    return hash.hexdigest()

def main():
    for subdir, dirs, files in os.walk(cwd+"/thirdparty"):
        for filename in files:
            filepath = subdir + os.sep + filename
            print(filename)
            if filepath.endswith(".whl") and (fnmatch.fnmatchcase(filename, "*py3*") or fnmatch.fnmatchcase(filename, "*cp36*")):
                name = filename.split('-')[0]
                version = filename.split('-')[1]
                package_name = name + "==" + version
                hs= hash_of_file(filepath)
                if is_package_exist_without_hashes(package_name):
                    append_requirement_file(package_name,hs)
                else: add_package(package_name,hs)
            
            elif filepath.endswith(".gz") and not filename.startswith("py2-"):
                name = filename.split('-')[0]
                version = re.findall("\d+\.\d+\.+\d|\d+\.\d+\d*|\d+\d*",filename)
                if len(version)>=2:
                    version[0]= version[0]+version[1]
                if re.search(r'\d', name):
                    version[0]= version[1]
                hs= hash_of_file(filepath)
                package_name = name + "==" + version[0]
                if is_package_exist_without_hashes(package_name):
                    append_requirement_file(package_name,hs)       
                else: add_package(package_name,hs)

if __name__ == '__main__':
    main()
