#
# Copyright (c) 2018 nexB Inc. and others. All rights reserved.
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
from __future__ import division
from __future__ import print_function
from __future__ import unicode_literals

from functools import partial
from itertools import imap

from plugincode import CodebasePlugin
from plugincode import PluginManager
from plugincode import HookimplMarker
from plugincode import HookspecMarker
from scancode.resource import Resource

# Python 2 and 3 support
try:
    # Python 2
    unicode
    str_orig = str
    bytes = str  # NOQA
    str = unicode  # NOQA
except NameError:
    # Python 3
    unicode = str  # NOQA

# Tracing flags
TRACE = False
TRACE_DEEP = False


def logger_debug(*args):
    pass


if TRACE or TRACE_DEEP:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, unicode)
                                     and a or repr(a) for a in args))

stage = 'output'
entrypoint = 'scancode_output'

output_spec = HookspecMarker(project_name=stage)
output_impl = HookimplMarker(project_name=stage)


@output_spec
class OutputPlugin(CodebasePlugin):
    """
    Base plugin class for scan output formatters all output plugins must extend.
    """

    def process_codebase(self, codebase, output, **kwargs):
        """
        Write `codebase` to the `output` file-like object (which could be a
        sys.stdout or a StringIO).

        Note: each subclass is using a differnt arg name for `output`
        """
        raise NotImplementedError

    @classmethod
    def get_results(cls, codebase, **kwargs):
        """
        Return an iterable of serialized scan results from a codebase.
        """
        # FIXME: serialization SHOULD NOT be needed: only some format need it
        # (e.g. JSON) and only these should serialize
        timing = kwargs.get('timing', False)
        info = kwargs.get('info', False) or getattr(codebase, 'with_info', False)
        strip_root = kwargs.get('strip_root', False)
        serializer = partial(Resource.to_dict, with_info=info, with_timing=timing)
        resources = codebase.walk_filtered(topdown=True, skip_root=strip_root)
        return imap(serializer, resources)


output_plugins = PluginManager(
    stage=stage,
    module_qname=__name__,
    entrypoint=entrypoint,
    plugin_base_class=OutputPlugin
)
