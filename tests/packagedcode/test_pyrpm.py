# -*- coding: utf-8 -*-
# -*- Mode: Python; py-ident-offset: 4 -*-
# vim:ts=4:sw=4:et

# Copyright (c) Mário Morgado
#
# Redistribution and use in source and binary forms, with or without modification,
# are permitted provided that the following conditions are met:
#
# 1. Redistributions of source code must retain the above copyright notice, this
# list of conditions and the following disclaimer.
#
# 2. Redistributions in binary form must reproduce the above copyright notice,
# this list of conditions and the following disclaimer in the documentation and/or
# other materials provided with the distribution.
#
# THIS SOFTWARE IS PROVIDED BY THE COPYRIGHT HOLDERS AND CONTRIBUTORS "AS IS" AND
# ANY EXPRESS OR IMPLIED WARRANTIES, INCLUDING, BUT NOT LIMITED TO, THE IMPLIED
# WARRANTIES OF MERCHANTABILITY AND FITNESS FOR A PARTICULAR PURPOSE ARE
# DISCLAIMED. IN NO EVENT SHALL THE COPYRIGHT HOLDER OR CONTRIBUTORS BE LIABLE FOR
# ANY DIRECT, INDIRECT, INCIDENTAL, SPECIAL, EXEMPLARY, OR CONSEQUENTIAL DAMAGES
# (INCLUDING, BUT NOT LIMITED TO, PROCUREMENT OF SUBSTITUTE GOODS OR SERVICES;
# LOSS OF USE, DATA, OR PROFITS; OR BUSINESS INTERRUPTION) HOWEVER CAUSED AND ON
# ANY THEORY OF LIABILITY, WHETHER IN CONTRACT, STRICT LIABILITY, OR TORT
# (INCLUDING NEGLIGENCE OR OTHERWISE) ARISING IN ANY WAY OUT OF THE USE OF THIS
# SOFTWARE, EVEN IF ADVISED OF THE POSSIBILITY OF SUCH DAMAGE.



import io
import os

from commoncode.testcase import FileBasedTesting
from packagedcode import pyrpm


class RPMTest(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_rpm(self):

        rpm_file = self.get_test_loc('pyrpm/Eterm-0.9.3-5mdv2007.0.rpm')
        with io.open(rpm_file, 'rb') as f:
            rpm = pyrpm.RPM(f)

        description = (
            'Eterm is a color vt102 terminal emulator intended as a replacement for Xterm.\n'
            'It is designed with a Freedom of Choice philosophy, leaving as much power,\n'
            'flexibility, and freedom as possible in the hands of the user.\n\n'
            'It is designed to look good and work well, but takes a feature-rich approach\n'
            'rather than one of minimalism while still maintaining speed and efficiency.\n\n'
            'It works on any windowmanager/desktop environment, although it is designed\n'
            'to work and integrate best with Enlightenment.'
        )

        assert rpm[pyrpm.RPMTAG_NAME] == rpm.name == 'Eterm'
        assert rpm[pyrpm.RPMTAG_VERSION] == rpm.version == '0.9.3'
        assert rpm[pyrpm.RPMTAG_RELEASE] == '5mdv2007.0'
        assert rpm[pyrpm.RPMTAG_ARCH] == 'i586'
        assert rpm[pyrpm.RPMTAG_COPYRIGHT] == 'BSD'
        assert rpm[pyrpm.RPMTAG_DESCRIPTION] == description
        assert rpm.is_binary is True
        assert rpm.package == 'Eterm-0.9.3'
        assert rpm.filename == 'Eterm-0.9.3-5mdv2007.0.i586.rpm'

        expected = {
            'arch': u'i586',
            'description': description,
            'dist_url': None,
            'distribution': u'Mandriva Linux',
            'epoch': None,
            'files_digest_algo': None,
            'group': u'Terminals',
            'is_binary': True,
            'license': u'BSD',
            'name': u'Eterm',
            'os': u'linux',
            'packager': u'Jerome Soyer <saispo@mandriva.org>',
            'release': u'5mdv2007.0',
            'source_rpm': None,
            'summary': u'Eterm (Enlightened Terminal Emulator) is a terminal emulator',
            'url': u'http://eterm.sourceforge.net/',
            'vendor': u'Mandriva',
            'version': u'0.9.3'
        }

        assert rpm.to_dict() == expected
