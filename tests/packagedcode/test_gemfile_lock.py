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

from collections import OrderedDict
import json
import os
import shutil

from commoncode.testcase import FileBasedTesting
from packagedcode import gemfile_lock


class TestGemfileLock(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_results(self, results, expected_loc, regen=False):
        """
        Helper to test a Gemfile object against an expected JSON file.
        """
        expected_loc = self.get_test_loc(expected_loc)
        if regen:
            regened_exp_loc = self.get_temp_file()

            with open(regened_exp_loc, 'wb') as ex:
                json.dump(results, ex, indent=2, separators=(',', ': '))

            expected_dir = os.path.dirname(expected_loc)
            if not os.path.exists(expected_dir):
                os.makedirs(expected_dir)
            shutil.copy(regened_exp_loc, expected_loc)

        with open(expected_loc) as ex:
            expected = json.load(ex, object_pairs_hook=OrderedDict)

        try:
            assert expected == results
        except AssertionError:
            assert expected.items() == results.items()

    def check_gemfile_lock(self, test_file, expected_loc, regen=False):
        test_file = self.get_test_loc(test_file)
        gfl = gemfile_lock.GemfileLockParser(test_file)
        results = [g.to_dict() for g in gfl.all_gems.values()]
        self.check_results(results, expected_loc, regen=regen)

    def test_get_options(self):
        test = '''GIT
  remote: git://github.com/amatsuda/kaminari.git
  revision: cb5539e0e81188ccadc0e703b32ae7b5dec13cb1
  specs:
    kaminari (0.15.0)
      actionpack (>= 3.0.0)
      activesupport (>= 3.0.0)
  ref: 4e286bf
  ref: 81e5e4d6
  ref: 92d6dac
  remote: .
  remote: ..
  remote: ../
  remote: ../../
  remote: ../gems/encryptor
  remote: /Users/hector/dev/gems/factory
  remote: git://github.com/ahoward/mongoid-grid_fs.git
  remote: git://github.com/amatsuda/kaminari.git
  remote: http://rubygems.org/
  remote: http://www.rubygems.org/
  revision: 059012a2c2a9e0a5d6e67137752c3e918689c88a
  foo: bar'''.splitlines()

        expected = [
            (None, None),
            ('remote', 'git://github.com/amatsuda/kaminari.git'),
            ('revision', 'cb5539e0e81188ccadc0e703b32ae7b5dec13cb1'),
            (None, None),
            (None, None),
            (None, None),
            (None, None),
            ('ref', '4e286bf'),
            ('ref', '81e5e4d6'),
            ('ref', '92d6dac'),
            ('remote', '.'),
            ('remote', '..'),
            ('remote', '../'),
            ('remote', '../../'),
            ('remote', '../gems/encryptor'),
            ('remote', '/Users/hector/dev/gems/factory'),
            ('remote', 'git://github.com/ahoward/mongoid-grid_fs.git'),
            ('remote', 'git://github.com/amatsuda/kaminari.git'),
            ('remote', 'http://rubygems.org/'),
            ('remote', 'http://www.rubygems.org/'),
            ('revision', '059012a2c2a9e0a5d6e67137752c3e918689c88a'),
            (None, None)
        ]
        results = [gemfile_lock.get_option(t) for t in test]
        assert expected == results

    def test_NAME_VERSION_re(self):
        import re
        nv = re.compile(gemfile_lock.NAME_VERSION).match
        test = [
            'brakeman (2.3.1)',
            'erubis (~> 2.6)',
            'fastercsv (~> 1.5)',
            'haml (>= 3.0, < 5.0)',
            'highline (~> 1.6.20)',
            'multi_json (~> 1.2)',
            'ruby2ruby (~> 2.0.5)',
            'ruby_parser (~> 3.2.2)',
            'sass (~> 3.0)',
            'slim (>= 1.3.6, < 3.0)',
            'terminal-table (~> 1.4)',
            'json (1.8.0-java)',
            'json',
            'alpha (1.9.0-x86-mingw32)'
        ]

        expected = [
            ('brakeman', '2.3.1'),
            ('erubis', '~> 2.6'),
            ('fastercsv', '~> 1.5'),
            ('haml', '>= 3.0, < 5.0'),
            ('highline', '~> 1.6.20'),
            ('multi_json', '~> 1.2'),
            ('ruby2ruby', '~> 2.0.5'),
            ('ruby_parser', '~> 3.2.2'),
            ('sass', '~> 3.0'),
            ('slim', '>= 1.3.6, < 3.0'),
            ('terminal-table', '~> 1.4'),
            ('json', '1.8.0'),
            ('json', None),
            ('alpha', '1.9.0')
        ]

        results = [(nv(x).group('name'),
                    nv(x).group('version'),) for x in test]

        assert expected == results

    def test_DEPS_re(self):
        test = '''DEPENDENCIES
  activesupport (~> 3.0)
  addressable
  bcrypt-ruby!
  activemodel (= 3.2.13.rc1)
  activemodel (= 4.0.0.beta)!
  activerecord (~> 3.1.12)
  activerecord (= 2.0.0)
  activerecord (>= 3.0.0)
  activesupport (= 2.3.11)
  msgpack (>= 0.4.4, < 0.6.0, != 0.5.3, != 0.5.2, != 0.5.1, != 0.5.0)
  msgpack (>= 0.4.4, < 0.6.0, != 0.5.3, != 0.5.2, != 0.5.1, != 0.5.0)!
  tilt (~> 1.1, != 1.3.0)!'''.splitlines()

        expected = [
            None,
            ('activesupport', '~> 3.0', False),
            ('addressable', None, False),
            ('bcrypt-ruby', None, True),
            ('activemodel', '= 3.2.13.rc1', False),
            ('activemodel', '= 4.0.0.beta', True),
            ('activerecord', '~> 3.1.12', False),
            ('activerecord', '= 2.0.0', False),
            ('activerecord', '>= 3.0.0', False),
            ('activesupport', '= 2.3.11', False),
            ('msgpack', '>= 0.4.4, < 0.6.0, != 0.5.3, != 0.5.2, != 0.5.1, != 0.5.0', False),
            ('msgpack', '>= 0.4.4, < 0.6.0, != 0.5.3, != 0.5.2, != 0.5.1, != 0.5.0', True),
            ('tilt', '~> 1.1, != 1.3.0', True),
        ]
        results = []
        for t in test:
            dep = gemfile_lock.DEPS(t)
            if dep:
                version = dep.group('version')
                name = dep.group('name')
                pinned = True if dep.group('pinned') else False
                results.append((name, version, pinned,))
            else:
                results.append(None)
        assert expected == results

    def test_SPEC_DEPS_re(self):
        test = '''    specs:
    actionmailer (4.0.0.rc1)
    actionpack (4.0.0.beta1)
    airbrake (3.1.16)
    akami (1.2.1)
    allowy (0.4.0)
    arel (5.0.1.20140414130214)
    bson (1.4.0-java)
    active_attr (0.8.4)'''.splitlines()

        expected = [
            ('actionmailer', '4.0.0.rc1'),
            ('actionpack', '4.0.0.beta1'),
            ('airbrake', '3.1.16'),
            ('akami', '1.2.1'),
            ('allowy', '0.4.0'),
            ('arel', '5.0.1.20140414130214'),
            ('bson', '1.4.0'),
            ('active_attr', '0.8.4')
        ]
        nv = gemfile_lock.SPEC_DEPS
        results = [(nv(x).group('name'), nv(x).group('version'),)
                   for x in test if nv(x)]
        assert expected == results

    def test_SPEC_SUB_DEPS_re(self):
        test = '''  specs:
    akami (1.2.1)
      actionmailer (= 4.0.0)
      actionmailer (= 4.0.0.rc1)
      actionmailer (>= 3, < 5)
      actionpack (~> 3.0)
      active_utils (~> 2.0, >= 2.0.1)
      activemodel (~> 3.0)
      activemodel (~> 3.0.0)
      beefcake (~> 1.2366.0)
      msgpack (>= 0.4.4, < 0.6.0, != 0.5.3, != 0.5.2, != 0.5.1, != 0.5.0)
      tilt (~> 1.1, != 1.3.0)'''.splitlines()

        expected = [
            ('actionmailer', '= 4.0.0'),
            ('actionmailer', '= 4.0.0.rc1'),
            ('actionmailer', '>= 3, < 5'),
            ('actionpack', '~> 3.0'),
            ('active_utils', '~> 2.0, >= 2.0.1'),
            ('activemodel', '~> 3.0'),
            ('activemodel', '~> 3.0.0'),
            ('beefcake', '~> 1.2366.0'),
            ('msgpack', '>= 0.4.4, < 0.6.0, != 0.5.3, != 0.5.2, != 0.5.1, != 0.5.0'),
            ('tilt', '~> 1.1, != 1.3.0'),
            ]
        nv = gemfile_lock.SPEC_SUB_DEPS
        results = [(nv(x).group('name'), nv(x).group('version'),)
                   for x in test if nv(x)]
        assert expected == results

    def test_Gem_as_nv_tree(self):
        Gem = gemfile_lock.Gem
        a = Gem('a', '1')
        b = Gem('b', '2')
        c = Gem('c', '2')
        d = Gem('d', '2')
        e = Gem('e', '2')
        f = Gem('f', '2')

        a.dependencies['b'] = b
        a.dependencies['c'] = c

        b.dependencies['d'] = d
        b.dependencies['e'] = e
        b.dependencies['f'] = f

        c.dependencies['e'] = e
        c.dependencies['f'] = f

        expected = {
            ('a', '1'): {
                ('b', '2'): {
                    ('d', '2'): {},
                    ('e', '2'): {},
                    ('f', '2'): {}
                },
                ('c', '2'): {
                    ('e', '2'): {},
                    ('f', '2'): {}
                }
            }
        }
        self.assertEqual(expected, a.as_nv_tree())

    def test_Gem_flatten_urn(self):
        Gem = gemfile_lock.Gem
        a = Gem('a', 'v1')
        b = Gem('b', 'v2')
        c = Gem('c', 'v3')
        d = Gem('d', 'v4')
        e = Gem('e', 'v5')
        f = Gem('f', 'v6')
        g = Gem('g', 'v7')

        a.dependencies['b'] = b
        a.dependencies['c'] = c

        b.dependencies['d'] = d
        b.dependencies['e'] = e
        b.dependencies['f'] = f

        c.dependencies['e'] = e
        c.dependencies['f'] = f
        c.dependencies['g'] = g

        g.dependencies['b'] = b

        expected = sorted([
            (u'urn:dje:component:a:v1', 'a-v1.gem', u'urn:dje:component:b:v2', 'b-v2.gem'),
            (u'urn:dje:component:a:v1', 'a-v1.gem', u'urn:dje:component:c:v3', 'c-v3.gem'),
            (u'urn:dje:component:b:v2', 'b-v2.gem', u'urn:dje:component:d:v4', 'd-v4.gem'),
            (u'urn:dje:component:b:v2', 'b-v2.gem', u'urn:dje:component:e:v5', 'e-v5.gem'),
            (u'urn:dje:component:b:v2', 'b-v2.gem', u'urn:dje:component:f:v6', 'f-v6.gem'),
            (u'urn:dje:component:c:v3', 'c-v3.gem', u'urn:dje:component:e:v5', 'e-v5.gem'),
            (u'urn:dje:component:c:v3', 'c-v3.gem', u'urn:dje:component:f:v6', 'f-v6.gem'),
            (u'urn:dje:component:c:v3', 'c-v3.gem', u'urn:dje:component:g:v7', 'g-v7.gem'),
            (u'urn:dje:component:g:v7', 'g-v7.gem', u'urn:dje:component:b:v2', 'b-v2.gem'),
            ])
        results = sorted(a.flatten_urn())
        assert expected == results

    def test_Gem_flatten(self):
        Gem = gemfile_lock.Gem
        a = Gem('a', 'v1')
        b = Gem('b', 'v2')
        c = Gem('c', 'v3')
        d = Gem('d', 'v4')
        e = Gem('e', 'v5')
        f = Gem('f', 'v6')
        g = Gem('g', 'v7')

        a.dependencies['b'] = b
        a.dependencies['c'] = c

        b.dependencies['d'] = d
        b.dependencies['e'] = e
        b.dependencies['f'] = f

        c.dependencies['e'] = e
        c.dependencies['f'] = f
        c.dependencies['g'] = g

        g.dependencies['b'] = b

        expected = sorted([
            (a, c),
            (a, b),
            (b, d),
            (b, e),
            (b, f),
            (c, e),
            (c, f),
            (c, g),
            (g, b),
            ])
        results = sorted(a.flatten())
        assert expected == results

    def test_Gem_as_nv_tree_with_no_deps(self):
        Gem = gemfile_lock.Gem
        a = Gem('a', '1')
        expected = {('a', '1'): {}}
        results = a.as_nv_tree()
        assert expected == results


    def test_Gem_to_dict(self):
        Gem = gemfile_lock.Gem
        a = Gem('a', '1')
        b = Gem('b', '2')
        a.dependencies['b'] = b
        expected = [
            (u'name', 'a'),
            (u'version', '1'),
            (u'platform', None),
            (u'pinned', False),
            (u'remote', None),
            (u'type', None),
            (u'path', None),
            (u'revision', None),
            (u'ref', None),
            (u'branch', None),
            (u'submodules', None),
            (u'tag', None),
            (u'requirements', []),
            (u'dependencies',
             OrderedDict([(u'a@1', OrderedDict([(u'b@2', OrderedDict())]))]))
        ]

        results = a.to_dict()
        assert expected == results.items()

    def test_GemfileLockParser_can_parse_a_flat_list_of_deps(self):
        test_file = 'gemfile_lock/as_deps/Gemfile.lock'
        expected_loc = 'gemfile_lock/as_deps/Gemfile.lock.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_simple_files(self):
        test_file = 'gemfile_lock/complete/Gemfile.lock_simple'
        expected_loc = 'gemfile_lock/complete/Gemfile.lock_simple.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_complex_files(self):
        test_file = 'gemfile_lock/complete/Gemfile.lock_complex'
        expected_loc = 'gemfile_lock/complete/Gemfile.lock_complex.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_dependency(self):
        test_file = 'gemfile_lock/dependency/Gemfile.lock'
        expected_loc = 'gemfile_lock/dependency/Gemfile.lock.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_platform(self):
        test_file = 'gemfile_lock/platform/Gemfile.lock'
        expected_loc = 'gemfile_lock/platform/Gemfile.lock.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_spec_single_level(self):
        test_file = 'gemfile_lock/spec/Gemfile.lock1'
        expected_loc = 'gemfile_lock/spec/Gemfile.lock1.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_spec_two_levels(self):
        test_file = 'gemfile_lock/spec/Gemfile.lock2'
        expected_loc = 'gemfile_lock/spec/Gemfile.lock2.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_spec_multi_levels(self):
        test_file = 'gemfile_lock/spec/Gemfile.lock3'
        expected_loc = 'gemfile_lock/spec/Gemfile.lock3.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_complex_multi_levels_deps(self):
        test_file = 'gemfile_lock/spec/Gemfile.lock4'
        expected_loc = 'gemfile_lock/spec/Gemfile.lock4.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_gem(self):
        test_file = 'gemfile_lock/gem/Gemfile.lock1'
        expected_loc = 'gemfile_lock/gem/Gemfile.lock1.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_gem_with_two_remotes(self):
        test_file = 'gemfile_lock/gem/Gemfile.lock3'
        expected_loc = 'gemfile_lock/gem/Gemfile.lock3.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_gem_with_path_before(self):
        test_file = 'gemfile_lock/gem/Gemfile.lock2'
        expected_loc = 'gemfile_lock/gem/Gemfile.lock2.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_with_one_path(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_path1'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_path1.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_with_two_paths(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_path2'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_path2.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_tag_and_remote_mixed_step1(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_mixed1'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_mixed1.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_with_remote(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_mixed2'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_mixed2.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_with_vcs_refs_mixed_step3(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_mixed3'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_mixed3.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_with_vsc_mixed_step4(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_mixed4'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_mixed4.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_with_mixed_step5(self):
        test_file = 'gemfile_lock/source/Gemfile.lock_mixed5'
        expected_loc = 'gemfile_lock/source/Gemfile.lock_mixed5.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_with_multi_paths_in_git(self):
        test_file = 'gemfile_lock/git/Gemfile.lock'
        expected_loc = 'gemfile_lock/git/Gemfile.lock.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)

    def test_GemfileLockParser_can_parse_source_source_with_git_and_no_deps(self):
        test_file = 'gemfile_lock/git/Gemfile.lock_single'
        expected_loc = 'gemfile_lock/git/Gemfile.lock_single.expected.json'
        self.check_gemfile_lock(test_file, expected_loc, regen=False)
