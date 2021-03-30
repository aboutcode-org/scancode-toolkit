#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode.cliutils import OUTPUT_FILTER_GROUP
from plugincode.output_filter import OutputFilterPlugin
from plugincode.output_filter import output_filter_impl
from commoncode.cliutils import PluggableCommandLineOption

import saneyaml
import licensedcode
from os.path import abspath
from os.path import dirname
from os.path import join
from os.path import exists

@output_filter_impl
class FilterIgnorableCopyrights(OutputFilterPlugin):
    """
    A post-scan plugin to filter out ignorable-copyrights that are read from license's yaml
    file. These copyrights are just noise as these are the copyrights for the license text
    and not for the code itself.
    """

    options = [
        PluggableCommandLineOption(('--filter-ignorable-copyrights',),
        is_flag=True, default=False,
        help='Filter out copyrights that are for the license text and not the code itself',
        help_group=OUTPUT_FILTER_GROUP)
    ]

    def is_enabled(self, filter_ignorable_copyrights, **kwargs):
        return filter_ignorable_copyrights

    def process_codebase(self, codebase, filter_ignorable_copyrights, **kwargs):
        """
        Remove ignorable copyrights from resource that are detected in the same line ranges
        as the licenses.
        """
        if not self.is_enabled(filter_ignorable_copyrights):
            return

        licenses_dir = join(abspath(dirname(licensedcode.__file__)), 'data', 'licenses')
        
        for resource in codebase.walk(topdown=True):
            if not resource.is_file:
                continue
            try:
                licenses = [entry for entry in resource.licenses]
                copyrights = [entry for entry in resource.copyrights]
            except AttributeError:
                continue

            for license in licenses:
                copyrights_temp = []
                for copyright in copyrights:
                    if not self.in_range(license, copyright):
                        continue
                    
                    ignorable_copyrights = self.get_ignorable_copyrights(licenses_dir, license.get('key'))
                    
                    if copyright.get('value') not in ignorable_copyrights:
                        copyrights_temp.append(copyright)
                
                resource.copyrights = copyrights_temp
            
            codebase.save_resource(resource)

    def in_range(self, license, copyright):
        return license.get('start_line') <= copyright.get(
            'start_line') and license.get('end_line') >= copyright.get('end_line')

    def get_ignorable_copyrights(self, licenses_dir, key):
        if not licenses_dir or not exists(licenses_dir):
            return []
        
        file_path = join(licenses_dir, key + '.yml')
        with open(file_path, 'r') as f:
            file_content = f.read()
        
        data =  saneyaml.load(file_content)
        return data.get('ignorable_copyrights', [])
