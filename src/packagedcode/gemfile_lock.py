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
import logging
import re

from six import string_types

from textcode import analysis

"""
Handle Gemfile.lock Rubygems lockfile.

Since there is no specifications of the Gemfile.lock format, this
script is based on and contains code derived from Ruby Bundler:

https://raw.githubusercontent.com/bundler/bundler/77e7050364367d98f9bc96911ea2769b69a4735c/lib/bundler/lockfile_parser.rb
TODO: update to latest https://github.com/bundler/bundler/compare/77e7050364367d98f9bc96911ea2769b69a4735c...master#diff-3c625d3cd7d7604b3e2e3c5487a5ede6

Portions copyright (c) 2010 Andre Arko
Portions copyright (c) 2009 Engine Yard

MIT License

Permission is hereby granted, free of charge, to any person obtaining
a copy of this software and associated documentation files (the
"Software"), to deal in the Software without restriction, including
without limitation the rights to use, copy, modify, merge, publish,
distribute, sublicense, and/or sell copies of the Software, and to
permit persons to whom the Software is furnished to do so, subject to
the following conditions:

The above copyright notice and this permission notice shall be
included in all copies or substantial portions of the Software.

THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND,
EXPRESS OR IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF
MERCHANTABILITY, FITNESS FOR A PARTICULAR PURPOSE AND
NONINFRINGEMENT. IN NO EVENT SHALL THE AUTHORS OR COPYRIGHT HOLDERS BE
LIABLE FOR ANY CLAIM, DAMAGES OR OTHER LIABILITY, WHETHER IN AN ACTION
OF CONTRACT, TORT OR OTHERWISE, ARISING FROM, OUT OF OR IN CONNECTION
WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE SOFTWARE.
"""

"""
Some examples:
SVN
  remote: file://#{lib_path('foo-1.0')}
  revision: 1
  ref: HEAD
  glob: some globs
  specs:
   foo (1.0)

GIT
  remote: #{lib_path("foo-1.0")}
  revision: #{git.ref_for('omg')}
  branch: omg
  ref: xx
  tag: xxx
  submodules: xxx
  glob:xxx
  specs:
    foo (1.0)

PATH
  remote: relative-path
  glob:
  specs:
   foo (1.0)
"""

TRACE = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    import sys
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, string_types) and a or repr(a) for a in args))


class GemDependency(namedtuple('GemDependency', 'name version')):

    def __new__(cls, name, version=None):
        return super(GemDependency, cls).__new__(cls, name, version)


class Gem(object):
    """
    A Gem can be packaged as .gem, or a source gem either fetched from GIT or
    SVN or in a local path.
    """
    supported_opts = 'remote', 'ref', 'revision', 'branch', 'submodules', 'tag',

    def __init__(self, name=None, version=None, platform=None):
        self.name = name
        self.version = version
        self.platform = platform
        # remote which may be a path, git, svn or Gem repo url
        # one of GEM, PATH, GIT or SVN
        self.remote = None
        self.type = None
        self.pinned = False
        self.spec_version = None
        # relative path
        self.path = None

        self.revision = None
        self.ref = None
        self.branch = None
        self.submodules = None
        self.tag = None

        # list of constraints such as '>= 1.1.9'
        self.requirements = []

        # a map of direct dependent Gems, keyed by name
        self.dependencies = OrderedDict()

    def __repr__(self):
        return ('Gem(name=%(name)r, version=%(version)r, type=%(type)r)' % self.__dict__)

    __str__ = __repr__

    def refine(self):
        """
        Apply some refinements to the Gem based on the type:
         - fix version and revisions for Gems checked-out from VCS
        """
        if self.type == PATH:
            self.path = self.remote

        if self.type in (GIT, SVN,):
            # TODO: this may not be correct for SVN
            self.spec_version = self.version
            if self.revision and not self.ref:
                self.version = self.revision
            elif self.revision and self.ref:
                self.version = self.revision
            elif not self.revision and self.ref:
                self.version = self.ref
            elif not self.revision and self.ref:
                self.version = self.ref

    def as_nv_tree(self):
        """
        Return a tree of name/versions dependency tuples from self as nested
        dicts. The tree root is self. Each key is a name/version tuple.
        Values are dicts.
        """
        tree = {}
        root = (self.name, self.version,)
        tree[root] = {}
        for _name, gem in self.dependencies.items():
            tree[root].update(gem.as_nv_tree())
        return tree

    def flatten(self):
        """
        Return a flattened list of parent/child tuples.
        """
        flattened = []
        for gem in self.dependencies.values():
            flattened.append((self, gem,))
            flattened.extend(gem.flatten())
        return sorted(set(flattened))

    def dependency_tree(self):
        """
        Return a tree of dependencies as nested mappings.
        Each key is a "name@version" string and values are dicts.
        """
        tree = OrderedDict()
        root = '{}@{}'.format(self.name or '', self.version or '')
        tree[root] = OrderedDict()
        for _name, gem in self.dependencies.items():
            tree[root].update(gem.dependency_tree())
        return tree

    def to_dict(self):
        """
        Return a native mapping for this Gem.
        """
        return OrderedDict([
            ('name', self.name),
            ('version', self.version),
            ('platform', self.platform),
            ('pinned', self.pinned),
            ('remote', self.remote),
            ('type', self.type),
            ('path', self.path),
            ('revision', self.revision),
            ('ref', self.ref),
            ('branch', self.branch),
            ('submodules', self.submodules),
            ('tag', self.tag),
            ('requirements', self.requirements),
            ('dependencies', self.dependency_tree()),
        ])

    @property
    def gem_name(self):
        return '{}-{}.gem'.format(self.name, self.version)


OPTIONS = re.compile(r'^  (?P<key>[a-z]+): (?P<value>.*)$').match


def get_option(s):
    """
    Parse Gemfile.lock options such as remote, ref, revision, etc.
    """
    key = None
    value = None

    opts = OPTIONS(s)
    if opts:
        key = opts.group('key') or None
        value = opts.group('value') or None
        # normalize truth
        if value == 'true':
            value = True
        if value == 'false':
            value = False
        # only keep known options, discard others
        if key not in Gem.supported_opts:
            key = None
            value = None

    return key, value


# parse name/version/platform
NAME_VERSION = (
    # negative lookahead: not a space
    '(?! )'
    # a Gem name: several chars are not allowed
    '(?P<name>[^ \(\)\,\!\:]+)?'
    # a space then opening parens (
    '(?: \('
    # the version proper which is anything but a dash
    '(?P<version>[^-]*)'
    # and optionally some non-captured dash followed by anything, once
    # pinned version can have this form:
    # version-platform
    # json (1.8.0-java) alpha (1.9.0-x86-mingw32) and may not contain a !
    '(?:-(?P<platform>[^\!]*))?'
    # closing parens )
    '\)'
    # NV is zero or one time
    ')?')

# parse direct dependencies
DEPS = re.compile(
    # two spaces at line start
    '^ {2}'
    # NV proper
    '%(NAME_VERSION)s'
    # optional bang pinned
    '(?P<pinned>\!)?'
    '$' % locals()).match

# parse spec-level dependencies
SPEC_DEPS = re.compile(
    # four spaces at line start
    '^ {4}'
    '%(NAME_VERSION)s'
    '$' % locals()).match

# parse direct dependencies on spec
SPEC_SUB_DEPS = re.compile(
    # six spaces at line start
    '^ {6}'
    '%(NAME_VERSION)s'
    '$' % locals()).match

PLATS = re.compile('^  (?P<platform>.*)$').match

# Section headings: these are also used as switches to track a parsing state
PATH = u'PATH'
GIT = u'GIT'
SVN = u'SVN'
GEM = u'GEM'
PLATFORMS = u'PLATFORMS'
DEPENDENCIES = u'DEPENDENCIES'
SPECS = u'  specs:'

# types of Gems, which is really where they are provisioned from
# RubyGems repo, local path or VCS
GEM_TYPES = (GEM, PATH, GIT, SVN,)


class GemfileLockParser(object):
    """
    Parse a Gemfile.lock. Code originally derived from Bundler's
    /bundler/lib/bundler/lockfile_parser.rb parser

    The parsing use a simple state machine, switching states based on sections
    headings. The result is a tree of Gems objects stored in
    self.dependencies.
    """

    def __init__(self, lockfile):
        self.lockfile = lockfile
        # map of a line start string to the next parsing state function
        self.STATES = {
            DEPENDENCIES: self.parse_dependency,
            PLATFORMS: self.parse_platform,
            GIT: self.parse_options,
            PATH: self.parse_options,
            SVN: self.parse_options,
            GEM: self.parse_options,
            SPECS: self.parse_spec
        }

        # the final tree of dependencies, keyed by name
        self.dependency_tree = OrderedDict()

        # a flat dict of all gems, keyed by name
        self.all_gems = OrderedDict()

        self.platforms = []

        # init parsing state
        self.reset_state()

        # parse proper
        for line in analysis.unicode_text_lines(lockfile):
            line = line.rstrip()

            # reset state
            if not line:
                self.reset_state()
                continue

            # switch to new state
            if line in self.STATES:
                if line in GEM_TYPES:
                    self.current_type = line
                self.state = self.STATES[line]
                continue

            # process state
            if self.state:
                self.state(line)

        # finally refine the collected data
        self.refine()

    def reset_state (self):
        self.state = None
        self.current_options = {}
        self.current_gem = None
        self.current_type = None

    def refine(self):
        for gem in self.all_gems.values():
            gem.refine()

    def get_or_create(self, name, version=None, platform=None):
        """
        Return an existing gem if it exists or creates a new one.
        Update the all_gems registry.
        """
        if name in self.all_gems:
            gem = self.all_gems[name]
            gem.version = gem.version or version
            gem.platform = gem.platform or platform
        else:
            gem = Gem(name, version, platform)
            self.all_gems[name] = gem
        return gem

    def parse_options(self, line):
        key, value = get_option(line)
        if key:
            self.current_options[key] = value

    def parse_spec(self, line):
        spec_dep = SPEC_DEPS(line)
        if spec_dep:
            name = spec_dep.group('name')
            # first level dep is always an exact version
            version = spec_dep.group('version')
            platform = spec_dep.group('platform') or 'ruby'

            # always set a new current gem
            self.current_gem = self.get_or_create(name, version, platform)
            self.current_gem.type = self.current_type

            if version:
                self.current_gem.version = version

            self.current_gem.platform = platform
            for k, v in self.current_options.items():
                setattr(self.current_gem, k, v)
            return

        spec_sub_dep = SPEC_SUB_DEPS(line)
        if spec_sub_dep:
            name = spec_sub_dep.group('name')
            if name == 'bundler':
                return
            # second level dep is always a version constraint
            requirements = spec_sub_dep.group('version') or []
            if requirements:
                requirements = [d.strip() for d in requirements.split(',')]

            if name in self.current_gem.dependencies:
                dep = self.current_gem.dependencies[name]
            else:
                dep = self.get_or_create(name)
                self.current_gem.dependencies[name] = dep
            # unless set , a sub dep is always a gem
            if not dep.type:
                dep.type = GEM

            for v in requirements:
                if v not in dep.requirements:
                    dep.requirements.append(v)

    def parse_dependency(self, line):
        deps = DEPS(line)
        if not deps:
            if TRACE:
                logger_debug('ERROR: parse_dependency: '
                      'line not matched: %(line)r' % locals())
            return

        name = deps.group('name')

        # at this stage ALL gems should already exist except possibly
        # for bundler: not finding one is an error
        try:
            gem = self.all_gems[name]
        except KeyError as e:
            gem = Gem(name)
            self.all_gems[name] = gem
            if name != 'bundler' and TRACE:
                logger_debug('ERROR: parse_dependency: '
                      'gem %(name)r does not yet exists in all_gems: '
                      '%(line)r' % locals())

        if name in self.dependency_tree:
            if TRACE:
                logger_debug('WARNING: parse_dependency: '
                      'dependency %(name)r / %(version)r already declared. '
                      'line: %(line)r' % locals())
        else:
            self.dependency_tree[name] = gem

        version = deps.group('version') or []
        if version:
            version = [v.strip() for v in version.split(',')]
            # the version of a direct dep is always a constraint
            # we append these at the top of the list as this is
            # the main constraint
            for v in version:
                gem.requirements.insert(0, v)
            # assert gem.version == version

        gem.pinned = True if deps.group('pinned') else False

    def parse_platform(self, line):
        plat = PLATS(line)
        if not plat:
            if TRACE:
                logger_debug('ERROR: parse_platform: '
                      'line not matched: %(line)r' % locals())
            return
        plat = plat.group('platform')
        self.platforms.append(plat.strip())

    def flatten(self):
        """
        Return the Gems dependency_tree as a sorted list of unique
        of tuples (parent Gem / child Gem) relationships.
        """
        flattened = []
        for direct in self.dependency_tree.values():
            flattened.append((None, direct,))
            flattened.extend(direct.flatten())
        return sorted(set(flattened))
