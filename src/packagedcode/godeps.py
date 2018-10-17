#
# Copyright (c) 2017 nexB Inc. and others. All rights reserved.
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
from __future__ import unicode_literals

from collections import namedtuple
from collections import OrderedDict
import io
import json
import logging

"""
Handle Godeps-like Go package dependency data.

Note: there are other dependency tools for Go beside Godeps, yet
several use the same format.
"""
# FIXME: update to use the latest vendor conventions.

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, basestring) and a or repr(a) for a in args))


class Dep(namedtuple('Dep', 'import_path revision comment')):

    def __new__(cls, import_path=None, revision=None, comment=None):
        return super(Dep, cls).__new__(cls, import_path, revision, comment)


# map Godep names to our own attribute names
NAMES = {
    'ImportPath': 'import_path',
    'GoVersion': 'go_version',
    'Packages': 'packages',
    'Deps': 'dependencies',
    'Comment': 'comment',
    'Rev': 'revision',
}


class Godep(object):
    """
    A JSON dep file with this structure:
        type Godeps struct {
            ImportPath string
            GoVersion  string   // Abridged output of 'go version'.
            Packages   []string // Arguments to godep save, if any.
            Deps       []struct {
                ImportPath string
                Comment    string // Description of commit, if present.
                Rev        string // VCS-specific commit ID.
            }
        }

    ImportPath
    GoVersion
    Packages
    Deps
        ImportPath
        Comment
        Rev
    """

    def __init__(self, location=None, import_path=None, go_version=None,
                 packages=None, dependencies=None):

        self.location = location
        self.import_path = None
        self.go_version = None
        self.dependencies = []
        self.packages = []

        if location:
            self.load(location)
        else:
            self.import_path = import_path
            self.go_version = go_version
            self.dependencies = dependencies or []
            self.packages = packages or []

    def load(self, location):
        """
        Load self from a location string or a file-like object
        containing a Godeps JSON.
        """
        if isinstance(location, basestring):
            with io.open(location, encoding='utf-8') as godep:
                data = json.load(godep)
        else:
            data = json.load(location)

        for key, value in data.items():
            name = NAMES.get(key)
            if name == 'dependencies':
                self.dependencies = self.parse_deps(value)
            else:
                setattr(self, name, value)
        return self

    def loads(self, string):
        """
        Load a Godeps JSON string.
        """
        from cStringIO import StringIO
        self.load(StringIO(string))
        return self

    def parse_deps(self, deps):
        deps_list = []
        for dep in deps:
            data = dict((NAMES[key], value) for key, value in dep.items())
            deps_list.append(Dep(**data))
        return deps_list or []

    def to_dict(self):
        dct = OrderedDict()
        dct.update([
            ('import_path', self.import_path),
            ('go_version', self.go_version),
            ('packages', self.packages),
            ('dependencies', [d._asdict() for d in self.dependencies]),
        ])
        return dct

    def __repr__(self):
        return ('Godep(%r)' % self.to_dict())

    __str__ = __repr__


def parse(location):
    """
    Return a mapping of parsed Godeps from the file at `location`.
    """
    return Godep(location).to_dict()
