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
import os
import subprocess


def main():
    cwd = os.getcwd()
    print("Current working directory:", cwd) 
    subprocess.run(["pip3","install","github-release-retry"])
    token = input ("Enter GITHUB_TOKEN :")

    os.environ ["GITHUB_TOKEN"] = token

    tag =  input ("Enter tag_name :")
    repo = input ("Enter name of repository name :")
    body = input ("Enter body string :")
    user = input ("Enter Github user name :")
    limit = input ("Enter retry limit :")
    for subdir, dirs, files in os.walk(cwd+"/thirdparty"):
        for filename in files:
            if fnmatch.fnmatchcase(filename, "*py3*") or fnmatch.fnmatchcase(filename, "*cp36*") or (fnmatch.fnmatchcase(filename, "*tar.gz*") and not fnmatch.fnmatchcase(filename, "*py2*")):
                filepath = subdir + os.sep + filename
                subprocess.run(["python3","-m","github_release_retry.github_release_retry","--user",user,"--repo",repo,"--tag_name",tag,"--body_string",body,"--retry_limit",limit,filepath])

if __name__ == '__main__':
    main()
    