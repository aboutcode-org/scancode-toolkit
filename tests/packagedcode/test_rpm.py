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

import os

from commoncode.testcase import FileBasedTesting

from packagedcode import rpm
from collections import OrderedDict


class TestRpm(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_to_package(self):
        test_file = self.get_test_loc('rpm/header/libproxy-bin-0.3.0-4.el6_3.x86_64.rpm')
        package = rpm.parse(test_file)
        expected = [
            ('type', u'RPM'),
            ('name', u'libproxy-bin'),
            ('version', u'0.3.0-4.el6_3'),
            ('primary_language', None),
            ('packaging', u'archive'),
            ('description', 
                u'Binary to test libproxy\n'
                u'The libproxy-bin package contains the proxy binary for libproxy'),
            ('payload_type', None),
            ('size', None),
            ('release_date', None),
            ('authors', []),
            ('maintainers', []),
            ('contributors', []),
            ('owners', []),
            ('packagers', []),
            ('distributors',
             [OrderedDict([('type', None), ('name', u''), ('email', None), ('url', None)])]),
            ('vendors',
             [OrderedDict([('type', None), ('name', u'CentOS'), ('email', None), ('url', None)])]),
            ('keywords', []),
            ('homepage_url', u'http://code.google.com/p/libproxy/'),
            ('download_urls', []),
            ('download_sha1', None),
            ('download_sha256', None),
            ('download_md5', None),
            ('bug_tracking_url', None),
            ('support_contacts', []),
            ('code_view_url', None),
            ('vcs_tool', None),
            ('vcs_repository', None),
            ('vcs_revision', None),
            ('copyright', None),
            ('asserted_license', u'LGPLv2+'),
            ('license_expression', None),
            ('license_texts', []),
            ('notice_text', None),
            ('dependencies', {}),
            ('related_packages',
             [OrderedDict([('type', u'RPM'), ('name', u'libproxy'), ('version', u'0.3.0-4.el6_3'), ('payload_type', 'source')])])
        ]

        assert expected == package.to_dict().items()
        package.validate()

    def test_pyrpm_basic(self):
        test_file = self.get_test_loc('rpm/header/python-glc-0.7.1-1.src.rpm')
        from packagedcode.pyrpm.rpm import RPM
        raw_rpm = RPM(open(test_file, 'rb'))
        alltags = raw_rpm.tags()
        expected = {
            'arch': 'noarch',
            'epoch': '',
            'description': 'These bindings permit access to QuesoGLC, an '
                           'open source\nimplementation of TrueType font '
                           'rendering for OpenGL.',
            'dist_url': '',
            'distribution': '',
            'group': 'Development/Libraries',
            'license': 'LGPL',
            'name': 'python-glc',
            'os': 'linux',
            'packager': '',
            'patch': '',
            'release': '1',
            'source_package': '',
            'source_rpm': '',
            'summary': 'ctypes Python bindings for QuesoGLC',
            'url': 'ftp://ftp.graviscom.de/pub/python-glc/',
            'vendor': 'Arno P\xc3\xa4hler <paehler@graviscom.de>',
            'version': '0.7.1',
        }

        assert expected == alltags
        # tests that tags can be converted to unicode without error
        [unicode(v, 'UTF-8', 'replace') for v in alltags.values()]

    def test_packagedcode_rpm_tags(self):
        test_file = self.get_test_loc('rpm/header/python-glc-0.7.1-1.src.rpm')
        expected = {
            'name': u'python-glc',
            'version': u'0.7.1',
            'release': u'1',
            'summary': u'ctypes Python bindings for QuesoGLC',
            'distribution': u'',
            'epoch': u'',
            'vendor': u'Arno P\xe4hler <paehler@graviscom.de>',
            'license': u'LGPL',
            'packager': u'',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'ftp://ftp.graviscom.de/pub/python-glc/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'These bindings permit access to QuesoGLC, an open source\nimplementation of TrueType font rendering for OpenGL.',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file, include_desc=True)
        expected['description'] = u''
        assert expected == rpm.tags(test_file, include_desc=False)

    def test_packagedcode_rpm_info(self):
        test_file = self.get_test_loc('rpm/header/python-glc-0.7.1-1.src.rpm')

        expected = rpm.RPMInfo(
            name=u'python-glc',
            version=u'0.7.1',
            release=u'1',
            epoch=u'',
            summary=u'ctypes Python bindings for QuesoGLC',
            distribution=u'',
            vendor=u'Arno P\xe4hler <paehler@graviscom.de>',
            license=u'LGPL',
            packager=u'',
            group=u'Development/Libraries',
            patch=u'',
            url=u'ftp://ftp.graviscom.de/pub/python-glc/',
            os=u'linux',
            arch=u'noarch',
            source_rpm=u'',
            source_package=u'',
            description=u'These bindings permit access to QuesoGLC, an open source\nimplementation of TrueType font rendering for OpenGL.',
            dist_url=u'',
            bin_or_src=u'src',
        )
        assert expected == rpm.info(test_file, include_desc=True)
        expected = expected._replace(description=u'')
        assert expected == rpm.info(test_file, include_desc=False)

    def test_packagedcode_rpm_tags_and_info_on_non_rpm_file(self):
        test_file = self.get_test_loc('rpm/README.txt')
        assert {} == rpm.tags(test_file, include_desc=True)
        assert {} == rpm.tags(test_file, include_desc=False)
        assert None == rpm.info(test_file, include_desc=True)
        assert None == rpm.info(test_file, include_desc=False)

    def test_rpm_tags_alfandega_2_0_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/alfandega-2.0-1.7.3.noarch.rpm')
        expected = {
            'name': u'alfandega',
            'version': u'2.0',
            'release': u'1.7.3',
            'epoch': u'',
            'summary': u'A perl modules for iptables firewall control.',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'Christian Tosta <c_tosta@yahoo.com.br>',
            'group': u'Applications/Networking/Security',
            'patch': u'',
            'url': u'http://alfandega.sourceforge.net/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'alfandega-2.0-1.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_alfandega_2_2_2_rh80_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/alfandega-2.2-2.rh80.noarch.rpm')
        expected = {
            'name': u'alfandega',
            'version': u'2.2',
            'release': u'2.rh80',
            'epoch': u'',
            'summary': u'A perl modules for iptables firewall control.',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'Christian Tosta <tosta@users.sourceforge.net>',
            'group': u'Applications/Networking/Security',
            'patch': u'',
            'url': u'http://alfandega.sourceforge.net/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'alfandega-2.2-2.rh80.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_alfandega_2_2_2_rh80_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/alfandega-2.2-2.rh80.src.rpm')
        expected = {
            'name': u'alfandega',
            'version': u'2.2',
            'release': u'2.rh80',
            'epoch': u'',
            'summary': u'A perl modules for iptables firewall control.',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'Christian Tosta <tosta@users.sourceforge.net>',
            'group': u'Applications/Networking/Security',
            'patch': u'',
            'url': u'http://alfandega.sourceforge.net/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_berry_mkdiscicons_0_07_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/berry-mkdiscicons-0.07-b1.src.rpm')
        expected = {
            'name': u'berry-mkdiscicons',
            'version': u'0.07',
            'release': u'b1',
            'epoch': u'',
            'summary': u'Automatic KDE/GNOME Desktop Disc Icon Creator for BERRY',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'User Interface/Desktops',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_berry_service_0_05_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/berry-service-0.05-b1.src.rpm')
        expected = {
            'name': u'berry-service',
            'version': u'0.05',
            'release': u'b1',
            'epoch': u'',
            'summary': u'BERRY Service Start',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'System/Tools',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_broken_rpm(self):
        test_file = self.get_test_loc('rpm/header/broken.rpm')
        expected = {
            'name': u'python-glc',
            'version': u'0.7.1',
            'release': u'1',
            'epoch': u'',
            'summary': u'ctypes Python bindings for QuesoGLC',
            'distribution': u'',
            'vendor': u'a',
            'license': u'om.de>',
            'packager': u'',
            'group': u'>',
            'patch': u'',
            'url': u'tar.gz',
            'os': u'n-glc/',
            'arch': u'',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_cndrvcups_common_2_00_2_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/cndrvcups-common-2.00-2.i386.rpm')
        expected = {
            'name': u'cndrvcups-common',
            'version': u'2.00',
            'release': u'2',
            'epoch': u'',
            'summary': u'Canon Printer Driver Common Module for Linux v2.00',
            'distribution': u'',
            'vendor': u'CANON INC.',
            'license': u'See the LICENSE*.txt file.',
            'packager': u'',
            'group': u'Applications/Publishing',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'cndrvcups-common-2.00-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_cndrvcups_lipslx_2_00_2_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/cndrvcups-lipslx-2.00-2.i386.rpm')
        expected = {
            'name': u'cndrvcups-lipslx',
            'version': u'2.00',
            'release': u'2',
            'epoch': u'',
            'summary': u'Canon LIPSLX Printer Driver for Linux v2.00',
            'distribution': u'',
            'vendor': u'CANON INC.',
            'license': u'See the LICENSE*.txt file.',
            'packager': u'',
            'group': u'Applications/Publishing',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'cndrvcups-lb-2.00-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_elfinfo_1_0_1_fc9_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/elfinfo-1.0-1.fc9.src.rpm')
        expected = {
            'name': u'elfinfo',
            'version': u'1.0',
            'release': u'1.fc9',
            'epoch': u'',
            'summary': u'ELF file parser a subset of eu-readelf',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPLv2',
            'packager': u'',
            'group': u'Development/Tools',
            'patch': u'',
            'url': u'http://code.google.com/p/elfinfo/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_faxmail_2_3_12mdv2007_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/FaxMail-2.3-12mdv2007.0.src.rpm')
        expected = {
            'name': u'FaxMail',
            'version': u'2.3',
            'epoch': u'',
            'release': u'12mdv2007.0',
            'summary': u'A program to send faxes for free via email and the TPC system',
            'distribution': u'Mandriva Linux',
            'vendor': u'Mandriva',
            'license': u'GPL',
            'packager': u'Stew Benedict <sbenedict@mandriva.com>',
            'group': u'Networking/Mail',
            'patch': u'FaxMail-2.3-fhs.patch.bz2',
            'url': u'http://www.inference.phy.cam.ac.uk/FaxMail/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_firefox_3_5_6_b1_nosrc_rpm(self):
        test_file = self.get_test_loc('rpm/header/firefox-3.5.6-b1.nosrc.rpm')
        expected = {
            'name': u'firefox',
            'version': u'3.5.6',
            'release': u'b1',
            'epoch': u'',
            'summary': u'Mozilla Firefox Web Browser',
            'distribution': u'',
            'vendor': u'',
            'license': u'MPL/LGPL',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'Applications/Internet',
            'patch': u'',
            'url': u'http://www.mozilla.org/projects/firefox/',
            'os': u'linux',
            'arch': u'i686',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_2b1_1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.2b1-1.src.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.2b1',
            'release': u'1',
            'epoch': u'',
            'summary': u'A tool to ping multiple hosts at once.',
            'distribution': u'',
            'vendor': u'teuto.net Netzdienste GmbH',
            'license': u'GPL',
            'packager': u'Lars Marowsky-Bree <lmb@teuto.net>',
            'group': u'Applications/Internet',
            'patch': u'fping.c.patch',
            'url': u'',
            'os': u'Linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_2b1_49607cl_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.2b1-49607cl.src.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.2b1',
            'release': u'49607cl',
            'epoch': u'',
            'summary': u'A tool to ping multiple hosts at once.',
            'distribution': u'Conectiva Linux',
            'vendor': u'Conectiva',
            'license': u'GPL',
            'packager': u'Conectiva S.A. <security@conectiva.com.br>',
            'group': u'Networking',
            'patch': u'fping-alpha.patch',
            'url': u'http://www.kernel.org/pub/software/admin/mon/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4_0_b2_rhfc1_dag_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4-0.b2.rhfc1.dag.i386.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4',
            'release': u'0.b2.rhfc1.dag',
            'epoch': u'',
            'summary': u'A utility to ping multiple hosts at once.',
            'distribution': u'',
            'vendor': u'Dag Apt Repository, http://dag.wieers.com/apt/',
            'license': u'distributable',
            'packager': u'Dag Wieers <dag@wieers.com>',
            'group': u'Applications/Internet',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'fping-2.4-0.b2.rhfc1.dag.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_10_fc12_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-10.fc12.ppc.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'10.fc12',
            'epoch': u'',
            'summary': u'Scriptable, parallelized ping-like utility',
            'distribution': u'Koji',
            'vendor': u'Fedora Project',
            'license': u'BSD with advertising',
            'packager': u'Fedora Project',
            'group': u'Applications/Internet',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'fping-2.4b2-10.fc12.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_10_fc12_x86_64_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-10.fc12.x86_64.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'10.fc12',
            'epoch': u'',
            'summary': u'Scriptable, parallelized ping-like utility',
            'distribution': u'Koji',
            'vendor': u'Fedora Project',
            'license': u'BSD with advertising',
            'packager': u'Fedora Project',
            'group': u'Applications/Internet',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'x86_64',
            'source_rpm': u'fping-2.4b2-10.fc12.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_114_1_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-114.1.ppc.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'114.1',
            'epoch': u'',
            'summary': u'A Program to Ping Multiple Hosts',
            'distribution': u'openSUSE 11.0 (PPC)',
            'vendor': u'SUSE LINUX Products GmbH, Nuernberg, Germany',
            'license': u'X11/MIT',
            'packager': u'http://bugs.opensuse.org',
            'group': u'Productivity/Networking/Diagnostic',
            'patch': u'',
            'url': u'http://www.fping.com',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'fping-2.4b2-114.1.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'srcrep:16c0b301019ebee17d30ec7abf9417de-fping',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_5_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-5.i586.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'5',
            'epoch': u'',
            'summary': u'fping - pings multiple hosts at once',
            'distribution': u'PLD 1.0 (Ra)',
            'vendor': u'PLD',
            'license': u'distributable',
            'packager': u'PLD bug tracking system ( http://bugs.pld.org.pl/ )',
            'group': u'Networking/Admin',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'fping-2.4b2-5.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_7_el4_asp101_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-7.el4.asp101.src.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'7.el4.asp101',
            'epoch': u'',
            'summary': u'Scriptable, parallelized ping-like utility',
            'distribution': u'',
            'vendor': u'ASPLinux',
            'license': u'BSD',
            'packager': u'ASPLinux Team <packages@asp-linux.com>',
            'group': u'Applications/Internet',
            'patch': u'fping-2.4b2_ipv6-fix.diff',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_7_el5_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-7.el5.i386.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'7.el5',
            'epoch': u'',
            'summary': u'Scriptable, parallelized ping-like utility',
            'distribution': u'Extras Packages for Enterprise Linux',
            'vendor': u'Fedora Project',
            'license': u'BSD',
            'packager': u'Fedora Project <http://bugzilla.redhat.com/bugzilla>',
            'group': u'Applications/Internet',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'fping-2.4b2-7.el5.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_8mdv2007_1_sparc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-8mdv2007.1.sparc.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'8mdv2007.1',
            'epoch': u'',
            'summary': u'Quickly ping N number of hosts to determine their reachability',
            'distribution': u'Mandriva Linux',
            'vendor': u'Mandriva',
            'license': u'GPL',
            'packager': u'Stefan van der Eijk <stefan@mandriva.org>',
            'group': u'Networking/Other',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'sparc',
            'source_rpm': u'fping-2.4b2-8mdv2007.1.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2_9_fc11_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-9.fc11.ppc.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2',
            'release': u'9.fc11',
            'epoch': u'',
            'summary': u'Scriptable, parallelized ping-like utility',
            'distribution': u'Koji',
            'vendor': u'Fedora Project',
            'license': u'BSD with advertising',
            'packager': u'Fedora Project',
            'group': u'Applications/Internet',
            'patch': u'',
            'url': u'http://www.fping.com/',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'fping-2.4b2-9.fc11.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fping_2_4b2to_20080101_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2to-20080101.src.rpm')
        expected = {
            'name': u'fping',
            'version': u'2.4b2to',
            'release': u'20080101',
            'epoch': u'',
            'summary': u'ICMP Host Pinging Tool',
            'distribution': u'OpenPKG Community',
            'vendor': u'Thomas Dzubin',
            'license': u'Open Source',
            'packager': u'OpenPKG Foundation e.V.',
            'group': u'Mapping',
            'patch': u'fping.patch',
            'url': u'http://fping.sourceforge.net/',
            'os': u'freebsd6.2',
            'arch': u'ix86',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_fxload_2002_04_11_212_1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fxload-2002_04_11-212.1.src.rpm')
        expected = {
            'name': u'fxload',
            'version': u'2002_04_11',
            'release': u'212.1',
            'epoch': u'',
            'summary': u'Download Firmware into USB FX and FX2 Devices',
            'distribution': u'openSUSE 11.0 (i586)',
            'vendor': u'SUSE LINUX Products GmbH, Nuernberg, Germany',
            'license': u'LGPL v2.1 or later',
            'packager': u'http://bugs.opensuse.org',
            'group': u'System/Kernel',
            'patch': u'fxload-2002_04_11.dif',
            'url': u'http://linux-hotplug.sf.net/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'srcrep:08daa5aad5d370288b2e472d300afb6c-fxload',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_kimera_1_40_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/kimera-1.40+-b1.src.rpm')
        expected = {
            'name': u'kimera',
            'version': u'1.40+',
            'release': u'b1',
            'epoch': u'',
            'summary': u'Another input method for Japanese',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'System Environment/Libraries',
            'patch': u'',
            'url': u'http://kimera.sourceforge.jp/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_libsqueeze0_2_0_0_2_3_8mdv2010_0_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/libsqueeze0.2_0-0.2.3-8mdv2010.0.i586.rpm')
        expected = {
            'name': u'libsqueeze0.2_0',
            'version': u'0.2.3',
            'release': u'8mdv2010.0',
            'epoch': u'',
            'summary': u'Main library for squeeze',
            'distribution': u'Mandriva Linux',
            'vendor': u'Mandriva',
            'license': u'GPlv2+',
            'packager': u'Thierry Vignaud <tvignaud@mandriva.com>',
            'group': u'System/Libraries',
            'patch': u'',
            'url': u'http://squeeze.xfce.org',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'squeeze-0.2.3-8mdv2010.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_m4ri_20081028_5_fc12_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/m4ri-20081028-5.fc12.src.rpm')
        expected = {
            'name': u'm4ri',
            'version': u'20081028',
            'release': u'5.fc12',
            'epoch': u'',
            'summary': u'Linear Algebra over F_2',
            'distribution': u'Koji',
            'vendor': u'Fedora Project',
            'license': u'GPLv2+',
            'packager': u'Fedora Project',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://m4ri.sagemath.org/',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_m4ri_devel_20081028_5_fc12_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/m4ri-devel-20081028-5.fc12.ppc.rpm')
        expected = {
            'name': u'm4ri-devel',
            'version': u'20081028',
            'release': u'5.fc12',
            'epoch': u'',
            'summary': u'Development files for m4ri',
            'distribution': u'Koji',
            'vendor': u'Fedora Project',
            'license': u'GPLv2+',
            'packager': u'Fedora Project',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://m4ri.sagemath.org/',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'm4ri-20081028-5.fc12.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_mdcp_0_1_2_2_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdcp-0.1.2-2.i386.rpm')
        expected = {
            'name': u'mdcp',
            'version': u'0.1.2',
            'release': u'2',
            'epoch': u'',
            'summary': u'copy from a disk device to many.',
            'distribution': u'OpenSuSE',
            'vendor': u'Monzyne, W.',
            'license': u'GPL',
            'packager': u'Wagner Monzyne <wamonzyne@hotmail.com>',
            'group': u'sysutils',
            'patch': u'',
            'url': u'http://mdcp.sourceforge.net/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'mdcp-0.1.2-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_mdcp_0_1_2_2_i686_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdcp-0.1.2-2.i686.rpm')
        expected = {
            'name': u'mdcp',
            'version': u'0.1.2',
            'release': u'2',
            'epoch': u'',
            'summary': u'copy from a disk device to many.',
            'distribution': u'OpenSuSE',
            'vendor': u'Monzyne, W.',
            'license': u'GPL',
            'packager': u'Wagner Monzyne <wamonzyne@hotmail.com>',
            'group': u'sysutils',
            'patch': u'',
            'url': u'http://mdcp.sourceforge.net/',
            'os': u'linux',
            'arch': u'i686',
            'source_rpm': u'mdcp-0.1.2-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_mdcp_0_1_2_2_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdcp-0.1.2-2.src.rpm')
        expected = {
            'name': u'mdcp',
            'version': u'0.1.2',
            'release': u'2',
            'epoch': u'',
            'summary': u'copy from a disk device to many.',
            'distribution': u'OpenSuSE',
            'vendor': u'Monzyne, W.',
            'license': u'GPL',
            'packager': u'Wagner Monzyne <wamonzyne@hotmail.com>',
            'group': u'sysutils',
            'patch': u'',
            'url': u'http://mdcp.sourceforge.net/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_mdv_rpm_summary_0_9_3_1mdv2010_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdv-rpm-summary-0.9.3-1mdv2010.0.noarch.rpm')
        expected = {
            'name': u'mdv-rpm-summary',
            'version': u'0.9.3',
            'release': u'1mdv2010.0',
            'epoch': u'',
            'summary': u'Localization files for packages summaries',
            'distribution': u'Mandriva Linux',
            'vendor': u'Mandriva',
            'license': u'GPL',
            'packager': u'Anne Nicolas <anne.nicolas@mandriva.com>',
            'group': u'System/Internationalization',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'mdv-rpm-summary-0.9.3-1mdv2010.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_mvlutils_2_8_4_7_0_2_0801061_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/mvlutils-2.8.4-7.0.2.0801061.src.rpm')
        expected = {
            'name': u'mvlutils',
            'version': u'2.8.4',
            'release': u'7.0.2.0801061',
            'epoch': u'',
            'summary': u'Miscellanious system utilites',
            'distribution': u'MontaVista Linux',
            'vendor': u'MontaVista Software, Inc.',
            'license': u'GPL/Other',
            'packager': u'<source@mvista.com>',
            'group': u'base',
            'patch': u'20710-initdconfig.patch',
            'url': u'',
            'os': u'linux',
            'arch': u'mips64_fp_le',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_nec_multiwriter_1700c_1_0_1_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/NEC-MultiWriter_1700C-1.0-1.i386.rpm')
        expected = {
            'name': u'NEC-MultiWriter_1700C',
            'version': u'1.0',
            'release': u'1',
            'epoch': u'',
            'summary': u'Printer Driver for NEC MultiWriter 1700C',
            'distribution': u'',
            'vendor': u'NEC Corporation',
            'license': u'Copyright (C) 2005 Fuji Xerox Co., Ltd.',
            'packager': u'',
            'group': u'Hardware/Printing',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'NEC-MultiWriter_1700C-1.0-1.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_necsul_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-1.2.0-2.i586.rpm')
        expected = {
            'name': u'necsul',
            'version': u'1.2.0',
            'release': u'2',
            'epoch': u'',
            'summary': u'Status Utility for Linux',
            'distribution': u'',
            'vendor': u'Fuji Xerox Co., Ltd.',
            'license': u'(C) 2005-2006 Fuji Xerox Co., Ltd.',
            'packager': u'Fuji Xerox Co., Ltd.',
            'group': u'Applications/System',
            'patch': u'',
            'url': u'http://www.express.nec.co.jp/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'necsul-1.2.0-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_necsul_devel_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-devel-1.2.0-2.i586.rpm')
        expected = {
            'name': u'necsul-devel',
            'version': u'1.2.0',
            'release': u'2',
            'epoch': u'',
            'summary': u'The Status Utility for Linux development toolkit.',
            'distribution': u'',
            'vendor': u'Fuji Xerox Co., Ltd.',
            'license': u'(C) 2005-2006 Fuji Xerox Co., Ltd.',
            'packager': u'Fuji Xerox Co., Ltd.',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://www.express.nec.co.jp/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'necsul-devel-1.2.0-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_necsul_suse_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-suse-1.2.0-2.i586.rpm')
        expected = {
            'name': u'necsul-suse',
            'version': u'1.2.0',
            'release': u'2',
            'epoch': u'',
            'summary': u'Status Utility for Linux',
            'distribution': u'',
            'vendor': u'Fuji Xerox Co., Ltd.',
            'license': u'(C) 2005-2006 Fuji Xerox Co., Ltd.',
            'packager': u'Fuji Xerox Co., Ltd.',
            'group': u'Applications/System',
            'patch': u'',
            'url': u'http://www.express.nec.co.jp/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'necsul-suse-1.2.0-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_necsul_suse_devel_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-suse-devel-1.2.0-2.i586.rpm')
        expected = {
            'name': u'necsul-suse-devel',
            'version': u'1.2.0',
            'release': u'2',
            'epoch': u'',
            'summary': u'The Status Utility for Linux development toolkit.',
            'distribution': u'',
            'vendor': u'Fuji Xerox Co., Ltd.',
            'license': u'(C) 2005-2006 Fuji Xerox Co., Ltd.',
            'packager': u'Fuji Xerox Co., Ltd.',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://www.express.nec.co.jp/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'necsul-suse-devel-1.2.0-2.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_cgi_3_42_8_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-CGI-3.42-8.src.rpm')
        expected = {
            'name': u'perl-CGI',
            'version': u'3.42',
            'release': u'8',
            'epoch': u'',
            'summary': u'CGI modules for perl',
            'distribution': u'',
            'vendor': u'ATrpms.net',
            'license': u'Artistic',
            'packager': u'ATrpms <http://ATrpms.net/>',
            'group': u'Development/Languages',
            'patch': u'',
            'url': u'http://search.cpan.org/~lds/CGI.pm-3.42/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_class_methodmaker_1_06_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Class-MethodMaker-1.06-1.7.3.noarch.rpm')
        expected = {
            'name': u'perl-Class-MethodMaker',
            'version': u'1.06',
            'release': u'1.7.3',
            'epoch': u'',
            'summary': u'A Perl module to show a progress bar in Terminal.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'perl-Class-MethodMaker-1.06-1.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_class_methodmaker_1_06_1_8_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Class-MethodMaker-1.06-1.8.0.noarch.rpm')
        expected = {
            'name': u'perl-Class-MethodMaker',
            'version': u'1.06',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'A Perl module to show a progress bar in Terminal.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'perl-Class-MethodMaker-1.06-1.8.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_class_methodmaker_1_06_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Class-MethodMaker-1.06-1.8.0.src.rpm')
        expected = {
            'name': u'perl-Class-MethodMaker',
            'version': u'1.06',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'A Perl module to show a progress bar in Terminal.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_compress_zlib_1_16_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Compress-Zlib-1.16-1.7.3.noarch.rpm')
        expected = {
            'name': u'perl-Compress-Zlib',
            'version': u'1.16',
            'release': u'1.7.3',
            'epoch': u'',
            'summary': u'A Perl interface to zlib library.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'perl-Compress-Zlib-1.16-1.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_compress_zlib_1_16_1_8_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Compress-Zlib-1.16-1.8.0.noarch.rpm')
        expected = {
            'name': u'perl-Compress-Zlib',
            'version': u'1.16',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'A Perl interface to zlib library.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'perl-Compress-Zlib-1.16-1.8.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_compress_zlib_1_16_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Compress-Zlib-1.16-1.8.0.src.rpm')
        expected = {
            'name': u'perl-Compress-Zlib',
            'version': u'1.16',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'A Perl interface to zlib library.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_crypt_idea_1_08_2_fc10_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Crypt-IDEA-1.08-2.fc10.src.rpm')
        expected = {
            'name': u'perl-Crypt-IDEA',
            'version': u'1.08',
            'release': u'2.fc10',
            'epoch': u'',
            'summary': u'Perl interface to IDEA block cipher',
            'distribution': u'Fedora 10',
            'vendor': u'RPM Fusion',
            'license': u'BSD with advertising',
            'packager': u'<http://free.rpmfusion.org/>',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://search.cpan.org/dist/Crypt-IDEA/',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_crypt_idea_1_08_2_fc10_x86_64_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Crypt-IDEA-1.08-2.fc10.x86_64.rpm')
        expected = {
            'name': u'perl-Crypt-IDEA',
            'version': u'1.08',
            'release': u'2.fc10',
            'epoch': u'',
            'summary': u'Perl interface to IDEA block cipher',
            'distribution': u'Fedora 10',
            'vendor': u'RPM Fusion',
            'license': u'BSD with advertising',
            'packager': u'<http://free.rpmfusion.org/>',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://search.cpan.org/dist/Crypt-IDEA/',
            'os': u'linux',
            'arch': u'x86_64',
            'source_rpm': u'perl-Crypt-IDEA-1.08-2.fc10.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_io_interface_0_97_3_7_3_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-IO-Interface-0.97-3.7.3.i386.rpm')
        expected = {
            'name': u'perl-IO-Interface',
            'version': u'0.97',
            'release': u'3.7.3',
            'epoch': u'',
            'summary': u'A Perl module to find information about network interface cards.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'perl-IO-Interface-0.97-3.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_io_interface_0_97_3_8_0_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-IO-Interface-0.97-3.8.0.i386.rpm')
        expected = {
            'name': u'perl-IO-Interface',
            'version': u'0.97',
            'release': u'3.8.0',
            'epoch': u'',
            'summary': u'A Perl module to find information about network interface cards.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'perl-IO-Interface-0.97-3.8.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_io_interface_0_97_3_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-IO-Interface-0.97-3.8.0.src.rpm')
        expected = {
            'name': u'perl-IO-Interface',
            'version': u'0.97',
            'release': u'3.8.0',
            'epoch': u'',
            'summary': u'A Perl module to find information about network interface cards.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_net_ip_1_15_1_7_3_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Net-IP-1.15-1.7.3.i386.rpm')
        expected = {
            'name': u'perl-Net-IP',
            'version': u'1.15',
            'release': u'1.7.3',
            'epoch': u'',
            'summary': u'Net::IP Perl module',
            'distribution': u'',
            'vendor': u'',
            'license': u'Perl',
            'packager': u'',
            'group': u'Development/Languages',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'perl-Net-IP-1.15-1.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_net_ip_1_15_1_8_0_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Net-IP-1.15-1.8.0.i386.rpm')
        expected = {
            'name': u'perl-Net-IP',
            'version': u'1.15',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'Net::IP Perl module',
            'distribution': u'',
            'vendor': u'',
            'license': u'Perl',
            'packager': u'',
            'group': u'Development/Languages',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'perl-Net-IP-1.15-1.8.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_net_ip_1_15_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Net-IP-1.15-1.8.0.src.rpm')
        expected = {
            'name': u'perl-Net-IP',
            'version': u'1.15',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'Net::IP Perl module',
            'distribution': u'',
            'vendor': u'',
            'license': u'Perl',
            'packager': u'',
            'group': u'Development/Languages',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_term_progressbar_2_00_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ProgressBar-2.00-1.7.3.noarch.rpm')
        expected = {
            'name': u'perl-Term-ProgressBar',
            'version': u'2.00',
            'release': u'1.7.3',
            'epoch': u'',
            'summary': u'A Perl module to show a progress bar in Terminal.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'perl-Term-ProgressBar-2.00-1.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_term_progressbar_2_00_1_8_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ProgressBar-2.00-1.8.0.noarch.rpm')
        expected = {
            'name': u'perl-Term-ProgressBar',
            'version': u'2.00',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'A Perl module to show a progress bar in Terminal.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'perl-Term-ProgressBar-2.00-1.8.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_term_progressbar_2_00_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ProgressBar-2.00-1.8.0.src.rpm')
        expected = {
            'name': u'perl-Term-ProgressBar',
            'version': u'2.00',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'A Perl module to show a progress bar in Terminal.',
            'distribution': u'',
            'vendor': u'',
            'license': u'distributable',
            'packager': u'',
            'group': u'Applications/CPAN',
            'patch': u'',
            'url': u'http://www.cpan.org/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_term_readkey_2_20_1_7_3_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ReadKey-2.20-1.7.3.i386.rpm')
        expected = {
            'name': u'perl-Term-ReadKey',
            'version': u'2.20',
            'release': u'1.7.3',
            'epoch': u'',
            'summary': u'Term::ReadKey perl module',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'Mirko Zeibig <mirko@zeibig.net>',
            'group': u'Development/Languages/Perl',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'perl-Term-ReadKey-2.20-1.7.3.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_term_readkey_2_20_1_8_0_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ReadKey-2.20-1.8.0.i386.rpm')
        expected = {
            'name': u'perl-Term-ReadKey',
            'version': u'2.20',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'Term::ReadKey perl module',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'Mirko Zeibig <mirko@zeibig.net>',
            'group': u'Development/Languages/Perl',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'perl-Term-ReadKey-2.20-1.8.0.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_perl_term_readkey_2_20_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ReadKey-2.20-1.8.0.src.rpm')
        expected = {
            'name': u'perl-Term-ReadKey',
            'version': u'2.20',
            'release': u'1.8.0',
            'epoch': u'',
            'summary': u'Term::ReadKey perl module',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'Mirko Zeibig <mirko@zeibig.net>',
            'group': u'Development/Languages/Perl',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_ping_0_17_30994cl_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/ping-0.17-30994cl.ppc.rpm')
        expected = {
            'name': u'ping',
            'version': u'0.17',
            'release': u'30994cl',
            'epoch': u'',
            'summary': u'The ping networking program',
            'distribution': u'Conectiva Linux',
            'vendor': u'Conectiva',
            'license': u'BSD',
            'packager': u'Testadora (testing system) <antoniojr@conectiva.com.br>',
            'group': u'Networking',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'ppc',
            'source_rpm': u'netkit-base-0.17-30994cl.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_ping_0_17_30994cl_sparc_rpm(self):
        test_file = self.get_test_loc('rpm/header/ping-0.17-30994cl.sparc.rpm')
        expected = {
            'name': u'ping',
            'version': u'0.17',
            'release': u'30994cl',
            'epoch': u'',
            'summary': u'The ping networking program',
            'distribution': u'Conectiva Linux',
            'vendor': u'Conectiva',
            'license': u'BSD',
            'packager': u'',
            'group': u'Networking',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'sparc',
            'source_rpm': u'netkit-base-0.17-30994cl.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_ping_ss020927_54702cl_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/ping-ss020927-54702cl.i386.rpm')
        expected = {
            'name': u'ping',
            'version': u'ss020927',
            'release': u'54702cl',
            'epoch': u'',
            'summary': u'The ping networking program',
            'distribution': u'Conectiva Linux',
            'vendor': u'Conectiva',
            'license': u'BSD',
            'packager': u'Conectiva S.A. <security@conectiva.com.br>',
            'group': u'Networking',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'iputils-ss020927-54702cl.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_renamed_rpm(self):
        test_file = self.get_test_loc('rpm/header/renamed.rpm')
        expected = {
            'name': u'python-glc',
            'version': u'0.7.1',
            'release': u'1',
            'epoch': u'',
            'summary': u'ctypes Python bindings for QuesoGLC',
            'distribution': u'',
            'vendor': u'Arno P\xe4hler <paehler@graviscom.de>',
            'license': u'LGPL',
            'packager': u'',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'ftp://ftp.graviscom.de/pub/python-glc/',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_rpm_trailing_rpm(self):
        test_file = self.get_test_loc('rpm/header/rpm_trailing.rpm')
        expected = {
            'name': u'elfinfo',
            'version': u'1.0',
            'release': u'1.fc9',
            'epoch': u'',
            'summary': u'ELF file parser a subset of eu-readelf',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPLv2',
            'packager': u'',
            'group': u'Development/Tools',
            'patch': u'',
            'url': u'http://code.google.com/p/elfinfo/',
            'os': u'linux',
            'arch': u'i386',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_setup_2_5_49_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/setup-2.5.49-b1.src.rpm')
        expected = {
            'name': u'setup',
            'version': u'2.5.49',
            'release': u'b1',
            'epoch': u'',
            'summary': u'A set of system configuration and setup files.',
            'distribution': u'',
            'vendor': u'',
            'license': u'public domain',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'System Environment/Base',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_svgalib_1_9_25_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/svgalib-1.9.25-b1.src.rpm')
        expected = {
            'name': u'svgalib',
            'version': u'1.9.25',
            'release': u'b1',
            'epoch': u'',
            'summary': u'Low-level fullscreen SVGA graphics library',
            'distribution': u'',
            'vendor': u'',
            'license': u'Public Domain',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'System Environment/Libraries',
            'patch': u'',
            'url': u'http://www.svgalib.org/',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_xsetup_0_28_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/xsetup-0.28-b1.src.rpm')
        expected = {
            'name': u'xsetup',
            'version': u'0.28',
            'release': u'b1',
            'epoch': u'',
            'summary': u'X.Org template config files and setup program',
            'distribution': u'',
            'vendor': u'',
            'license': u'GPL',
            'packager': u'yui <yui@po.yui.mine.nu>',
            'group': u'System/Tools',
            'patch': u'',
            'url': u'',
            'os': u'linux',
            'arch': u'noarch',
            'source_rpm': u'',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'src',
        }
        assert expected == rpm.tags(test_file)

    def test_rpm_tags_zziplib_0_11_15_3sf_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/zziplib-0.11.15-3sf.i586.rpm')
        expected = {
            'name': u'zziplib',
            'version': u'0.11.15',
            'release': u'3sf',
            'epoch': u'',
            'summary': u'ZZipLib - libZ-based ZIP-access Library',
            'distribution': u'Sourceforge',
            'vendor': u'Guido Draheim <guidod@gmx.de>',
            'license': u'LGPL',
            'packager': u'Guido Draheim <guidod@gmx.de>',
            'group': u'Development/Libraries',
            'patch': u'',
            'url': u'http://zziplib.sf.net',
            'os': u'linux',
            'arch': u'i586',
            'source_rpm': u'zziplib-0.11.15-3sf.src.rpm',
            'source_package': u'',
            'description': u'',
            'dist_url': u'',
            'bin_or_src': u'bin',
        }
        assert expected == rpm.tags(test_file)
