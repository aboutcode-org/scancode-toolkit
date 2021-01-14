#
# Copyright (c) nexB Inc. and others.
# SPDX-License-Identifier: Apache-2.0
#
# Visit https://aboutcode.org and https://github.com/nexB/ for support and download.
# ScanCode is a trademark of nexB Inc.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
#

import unittest

from commoncode import urn


class URNTestCase(unittest.TestCase):

    def test_encode_license(self):
        u1 = urn.encode('license', key='somekey')
        assert 'urn:dje:license:somekey' == u1

    def test_encode_owner(self):
        u1 = urn.encode('owner', name='somekey')
        assert 'urn:dje:owner:somekey' == u1

    def test_encode_component(self):
        u1 = urn.encode('component', name='name', version='version')
        assert 'urn:dje:component:name:version' == u1

    def test_encode_component_no_version(self):
        u1 = urn.encode('component', name='name', version='')
        assert 'urn:dje:component:name:' == u1

    def test_encode_license_with_extra_fields_are_ignored(self):
        u1 = urn.encode('license', key='somekey', junk='somejunk')
        assert 'urn:dje:license:somekey' == u1

    def test_encode_missing_field_raise_keyerror(self):
        with self.assertRaises(KeyError):
            urn.encode('license')

    def test_encode_missing_field_component_raise_keyerror(self):
        with self.assertRaises(KeyError):
            urn.encode('component', name='this')

    def test_encode_unknown_object_type_raise_keyerror(self):
        with self.assertRaises(KeyError):
            urn.encode('some', key='somekey')

    def test_encode_component_with_spaces_are_properly_quoted(self):
        u1 = urn.encode('component', name='name space',
                        version='version space')
        assert 'urn:dje:component:name+space:version+space' == u1

    def test_encode_leading_and_trailing_spaces_are_trimmed_and_ignored(self):
        u1 = urn.encode(' component ', name=' name space    ',
                        version='''  version space ''')
        assert 'urn:dje:component:name+space:version+space' == u1

    def test_encode_component_with_semicolon_are_properly_quoted(self):
        u1 = urn.encode('component', name='name:', version=':version')
        assert 'urn:dje:component:name%3A:%3Aversion' == u1

    def test_encode_component_with_plus_are_properly_quoted(self):
        u1 = urn.encode('component', name='name+', version='version+')
        assert 'urn:dje:component:name%2B:version%2B' == u1

    def test_encode_component_with_percent_are_properly_quoted(self):
        u1 = urn.encode('component', name='name%', version='version%')
        assert 'urn:dje:component:name%25:version%25' == u1

    def test_encode_object_type_case_is_not_significant(self):
        u1 = urn.encode('license', key='key')
        u2 = urn.encode('lICENSe', key='key')
        assert u1 == u2

    def test_decode_component(self):
        u = 'urn:dje:component:name:version'
        parsed = ('component', {'name': 'name', 'version': 'version'})
        assert parsed == urn.decode(u)

    def test_decode_license(self):
        u = 'urn:dje:license:lic'
        parsed = ('license', {'key': 'lic'})
        assert parsed == urn.decode(u)

    def test_decode_org(self):
        u = 'urn:dje:owner:name'
        parsed = ('owner', {'name': 'name'})
        assert parsed == urn.decode(u)

    def test_decode_build_is_idempotent(self):
        u1 = urn.encode('component', owner__name='org%', name='name%',
                       version='version%')
        m, f = urn.decode(u1)
        u3 = urn.encode(m, **f)
        assert u1 == u3

    def test_decode_raise_exception_if_incorrect_prefix(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('arn:dje:a:a')

    def test_decode_raise_exception_if_incorrect_ns(self):
        with self.assertRaises(urn.URNValidationError):
                urn.decode('urn:x:x:x')

    def test_decode_raise_exception_if_incorrect_prefix_or_ns(self):
        with self.assertRaises(urn.URNValidationError):
                urn.decode('x:x:x:x')

    def test_decode_raise_exception_if_too_short_license(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:license')

    def test_decode_raise_exception_if_too_short_component(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:component')

    def test_decode_raise_exception_if_too_long(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:owner:o:n')

    def test_decode_raise_exception_if_too_long1(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:component:o:n:v:junk')

    def test_decode_raise_exception_if_too_long2(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:owner:org:junk')

    def test_decode_raise_exception_if_too_long3(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:license:key:junk')

    def test_decode_raise_exception_if_unknown_object_type(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje:marshmallows:dsds')

    def test_decode_raise_exception_if_missing_object_type(self):
        with self.assertRaises(urn.URNValidationError):
            urn.decode('urn:dje::dsds')

    def test_encode_decode_is_idempotent(self):
        object_type = 'component'
        fields = {'name': 'SIP Servlets (MSS)', 'version': 'v 1.4.0.FINAL'}
        encoded = 'urn:dje:component:SIP+Servlets+%28MSS%29:v+1.4.0.FINAL'
        assert encoded == urn.encode(object_type, **fields)
        assert object_type, fields == urn.decode(encoded)
