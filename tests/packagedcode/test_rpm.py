# # -*- coding: utf-8 -*-

# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import os

from commoncode.testcase import FileBasedTesting

from packagedcode import rpm
from scancode_config import REGEN_TEST_FIXTURES
from packages_test_utils import check_result_equals_expected_json


class TestRpmBasics(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_parse_to_package(self):
        test_file = self.get_test_loc('rpm/header/libproxy-bin-0.3.0-4.el6_3.x86_64.rpm')
        package_datas = rpm.RpmArchiveHandler.parse(test_file)
        result = [pd.to_dict() for pd in package_datas]

        expected_loc = self.get_test_loc(
            'rpm/header/libproxy-bin-0.3.0-4.el6_3.x86_64.rpm-package-expected.json',
            must_exist=False,
        )
        check_result_equals_expected_json(result, expected_loc, regen=REGEN_TEST_FIXTURES)

    def test_pyrpm_basic(self):
        test_file = self.get_test_loc('rpm/header/python-glc-0.7.1-1.src.rpm')
        from packagedcode.pyrpm import RPM
        raw_rpm = RPM(open(test_file, 'rb'))
        alltags = raw_rpm.get_tags()
        expected = {
            'arch': 'noarch',
            'epoch': None,
            'files_digest_algo': None,
            'description': 'These bindings permit access to QuesoGLC, an '
                           'open source\nimplementation of TrueType font '
                           'rendering for OpenGL.',
            'dist_url': None,
            'distribution': None,
            'group': 'Development/Libraries',
            'license': 'LGPL',
            'name': 'python-glc',
            'os': 'linux',
            'packager': None,
            'release': '1',
            'patch': None,
            'source_rpm': None,
            'summary': 'ctypes Python bindings for QuesoGLC',
            'url': 'ftp://ftp.graviscom.de/pub/python-glc/',
            'vendor': 'Arno Pähler <paehler@graviscom.de>',
            'version': '0.7.1',
        }

        assert alltags == expected
        # tests that tags are all unicode
        assert all([isinstance(v, str) for v in alltags.values() if v])

    def test_get_rpm_tags_(self):
        test_file = self.get_test_loc('rpm/header/python-glc-0.7.1-1.src.rpm')

        expected = rpm.RPMtags(
            name='python-glc',
            version='0.7.1',
            release='1',
            epoch=None,
            summary='ctypes Python bindings for QuesoGLC',
            distribution=None,
            vendor='Arno P\xe4hler <paehler@graviscom.de>',
            license='LGPL',
            packager=None,
            group='Development/Libraries',
            url='ftp://ftp.graviscom.de/pub/python-glc/',
            os='linux',
            arch='noarch',
            source_rpm=None,
            description='These bindings permit access to QuesoGLC, an open source\nimplementation of TrueType font rendering for OpenGL.',
            dist_url=None,
            is_binary=False,
        )
        assert rpm.get_rpm_tags(test_file, include_desc=True) == expected
        expected = expected._replace(description=None)
        assert rpm.get_rpm_tags(test_file, include_desc=False) == expected

    def test_rpm_is_manifest_non_rpm_file(self):
        test_file = self.get_test_loc('rpm/README.txt')
        assert not rpm.RpmArchiveHandler.is_datafile(test_file)

    def test_rpm_is_manifest_rpm_file(self):
        test_file = self.get_test_loc('rpm/header/python-glc-0.7.1-1.src.rpm')
        assert rpm.RpmArchiveHandler.is_datafile(test_file)


def check_json(result, expected_file, regen=REGEN_TEST_FIXTURES):
    if regen:
        mode = 'w'
        with io.open(expected_file, mode) as reg:
            reg.write(json.dumps(result, indent=4, separators=(',', ': ')))

    with io.open(expected_file, encoding='utf-8') as exp:
        expected = json.load(exp)
    assert json.dumps(result) == json.dumps(expected)


class TestRpmTags(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def check_rpm_tags(self, test_file):
        suffix = '-expected.json'
        expected_file = test_file + suffix
        result = rpm.get_rpm_tags(test_file)._asdict()
        check_json(result, expected_file, regen=REGEN_TEST_FIXTURES)

    def test_rpm_tags_alfandega_2_0_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/alfandega-2.0-1.7.3.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_alfandega_2_2_2_rh80_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/alfandega-2.2-2.rh80.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_alfandega_2_2_2_rh80_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/alfandega-2.2-2.rh80.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_berry_mkdiscicons_0_07_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/berry-mkdiscicons-0.07-b1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_berry_service_0_05_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/berry-service-0.05-b1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_broken_rpm(self):
        test_file = self.get_test_loc('rpm/header/broken.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_cndrvcups_common_2_00_2_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/cndrvcups-common-2.00-2.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_cndrvcups_lipslx_2_00_2_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/cndrvcups-lipslx-2.00-2.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_elfinfo_1_0_1_fc9_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/elfinfo-1.0-1.fc9.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_faxmail_2_3_12mdv2007_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/FaxMail-2.3-12mdv2007.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_firefox_3_5_6_b1_nosrc_rpm(self):
        test_file = self.get_test_loc('rpm/header/firefox-3.5.6-b1.nosrc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_2b1_1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.2b1-1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_2b1_49607cl_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.2b1-49607cl.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4_0_b2_rhfc1_dag_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4-0.b2.rhfc1.dag.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_10_fc12_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-10.fc12.ppc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_10_fc12_x86_64_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-10.fc12.x86_64.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_114_1_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-114.1.ppc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_5_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-5.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_7_el4_asp101_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-7.el4.asp101.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_7_el5_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-7.el5.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_8mdv2007_1_sparc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-8mdv2007.1.sparc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2_9_fc11_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2-9.fc11.ppc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fping_2_4b2to_20080101_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fping-2.4b2to-20080101.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_fxload_2002_04_11_212_1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/fxload-2002_04_11-212.1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_kimera_1_40_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/kimera-1.40+-b1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_libsqueeze0_2_0_0_2_3_8mdv2010_0_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/libsqueeze0.2_0-0.2.3-8mdv2010.0.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_m4ri_20081028_5_fc12_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/m4ri-20081028-5.fc12.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_m4ri_devel_20081028_5_fc12_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/m4ri-devel-20081028-5.fc12.ppc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_mdcp_0_1_2_2_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdcp-0.1.2-2.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_mdcp_0_1_2_2_i686_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdcp-0.1.2-2.i686.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_mdcp_0_1_2_2_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdcp-0.1.2-2.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_mdv_rpm_summary_0_9_3_1mdv2010_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/mdv-rpm-summary-0.9.3-1mdv2010.0.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_mvlutils_2_8_4_7_0_2_0801061_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/mvlutils-2.8.4-7.0.2.0801061.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_nec_multiwriter_1700c_1_0_1_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/NEC-MultiWriter_1700C-1.0-1.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_necsul_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-1.2.0-2.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_necsul_devel_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-devel-1.2.0-2.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_necsul_suse_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-suse-1.2.0-2.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_necsul_suse_devel_1_2_0_2_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/necsul-suse-devel-1.2.0-2.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_cgi_3_42_8_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-CGI-3.42-8.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_class_methodmaker_1_06_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Class-MethodMaker-1.06-1.7.3.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_class_methodmaker_1_06_1_8_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Class-MethodMaker-1.06-1.8.0.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_class_methodmaker_1_06_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Class-MethodMaker-1.06-1.8.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_compress_zlib_1_16_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Compress-Zlib-1.16-1.7.3.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_compress_zlib_1_16_1_8_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Compress-Zlib-1.16-1.8.0.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_compress_zlib_1_16_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Compress-Zlib-1.16-1.8.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_crypt_idea_1_08_2_fc10_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Crypt-IDEA-1.08-2.fc10.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_crypt_idea_1_08_2_fc10_x86_64_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Crypt-IDEA-1.08-2.fc10.x86_64.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_io_interface_0_97_3_7_3_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-IO-Interface-0.97-3.7.3.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_io_interface_0_97_3_8_0_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-IO-Interface-0.97-3.8.0.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_io_interface_0_97_3_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-IO-Interface-0.97-3.8.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_net_ip_1_15_1_7_3_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Net-IP-1.15-1.7.3.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_net_ip_1_15_1_8_0_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Net-IP-1.15-1.8.0.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_net_ip_1_15_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Net-IP-1.15-1.8.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_term_progressbar_2_00_1_7_3_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ProgressBar-2.00-1.7.3.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_term_progressbar_2_00_1_8_0_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ProgressBar-2.00-1.8.0.noarch.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_term_progressbar_2_00_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ProgressBar-2.00-1.8.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_term_readkey_2_20_1_7_3_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ReadKey-2.20-1.7.3.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_term_readkey_2_20_1_8_0_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ReadKey-2.20-1.8.0.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_perl_term_readkey_2_20_1_8_0_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/perl-Term-ReadKey-2.20-1.8.0.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_ping_0_17_30994cl_ppc_rpm(self):
        test_file = self.get_test_loc('rpm/header/ping-0.17-30994cl.ppc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_ping_0_17_30994cl_sparc_rpm(self):
        test_file = self.get_test_loc('rpm/header/ping-0.17-30994cl.sparc.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_ping_ss020927_54702cl_i386_rpm(self):
        test_file = self.get_test_loc('rpm/header/ping-ss020927-54702cl.i386.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_renamed_rpm(self):
        test_file = self.get_test_loc('rpm/header/renamed.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_rpm_trailing_rpm(self):
        test_file = self.get_test_loc('rpm/header/rpm_trailing.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_setup_2_5_49_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/setup-2.5.49-b1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_svgalib_1_9_25_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/svgalib-1.9.25-b1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_xsetup_0_28_b1_src_rpm(self):
        test_file = self.get_test_loc('rpm/header/xsetup-0.28-b1.src.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_zziplib_0_11_15_3sf_i586_rpm(self):
        test_file = self.get_test_loc('rpm/header/zziplib-0.11.15-3sf.i586.rpm')
        self.check_rpm_tags(test_file)

    def test_rpm_tags_apache_commons_io_2_4_12_el7_noarch_rpm(self):
        test_file = self.get_test_loc('rpm/header/apache-commons-io-2.4-12.el7.noarch.rpm')
        self.check_rpm_tags(test_file)