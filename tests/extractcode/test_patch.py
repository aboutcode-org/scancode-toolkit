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


import codecs
import json
import os
from unittest.case import expectedFailure

from commoncode.testcase import FileBasedTesting
from commoncode.text import as_unicode
from extractcode import patch


class TestIsPatch(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_is_not_patch(self):
        test_dir = self.get_test_loc('patch/not_patches', copy=True)
        for r, _, files in os.walk(test_dir):
            for f in files:
                test_file = os.path.join(r, f)
                assert not patch.is_patch(test_file)

    def test_is_patch(self):
        test_dir = self.get_test_loc('patch/patches', copy=True)
        for r, _, files in os.walk(test_dir):
            for f in files:
                if not f.endswith('expected'):
                    test_file = os.path.join(r, f)
                    assert patch.is_patch(test_file)


def check_patch(test_file, expected_file, regen=False):
    result = [list(pi) for pi in patch.patch_info(test_file)]

    result = [[as_unicode(s), as_unicode(t), map(as_unicode, lines)]
              for s, t, lines in result]

    if regen:
        with codecs.open(expected_file, 'wb', encoding='utf-8') as regened:
            json.dump(result, regened, indent=2)
    with codecs.open(expected_file, 'rb', encoding='utf-8') as expect:
        expected = json.load(expect)
        assert expected == result


class TestPatchInfoFailing(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')
    # FIXME: these tests need love and eventually a bug report upstream

    @expectedFailure
    def test_patch_info_patch_patches_misc_webkit_opensource_patches_sync_xhr_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/sync_xhr.patch')
        # fails with Exception Unable to parse patch file
        list(patch.patch_info(test_file))

    @expectedFailure
    def test_patch_info_patch_patches_problematic_opensso_patch(self):
        test_file = self.get_test_loc(u'patch/patches/problematic/OpenSSO.patch')
        # fails with Exception Unable to parse patch file
        list(patch.patch_info(test_file))


class TestPatchInfo(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_patch_info_patch_patches_dnsmasq_2_63_1_diff(self):
        test_file = self.get_test_loc(u'patch/patches/dnsmasq_2.63-1.diff')
        expected_file = self.get_test_loc('patch/patches/dnsmasq_2.63-1.diff.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_dropbear_2012_55_1_diff(self):
        test_file = self.get_test_loc(u'patch/patches/dropbear_2012.55-1.diff')
        expected_file = self.get_test_loc('patch/patches/dropbear_2012.55-1.diff.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_electricfence_2_0_5_longjmp_patch(self):
        test_file = self.get_test_loc(u'patch/patches/ElectricFence-2.0.5-longjmp.patch')
        expected_file = self.get_test_loc('patch/patches/ElectricFence-2.0.5-longjmp.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_electricfence_2_1_vaarg_patch(self):
        test_file = self.get_test_loc(u'patch/patches/ElectricFence-2.1-vaarg.patch')
        expected_file = self.get_test_loc('patch/patches/ElectricFence-2.1-vaarg.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_electricfence_2_2_2_madvise_patch(self):
        test_file = self.get_test_loc(u'patch/patches/ElectricFence-2.2.2-madvise.patch')
        expected_file = self.get_test_loc('patch/patches/ElectricFence-2.2.2-madvise.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_electricfence_2_2_2_pthread_patch(self):
        test_file = self.get_test_loc(u'patch/patches/ElectricFence-2.2.2-pthread.patch')
        expected_file = self.get_test_loc('patch/patches/ElectricFence-2.2.2-pthread.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_libmediainfo_0_7_43_diff(self):
        test_file = self.get_test_loc(u'patch/patches/libmediainfo-0.7.43.diff')
        expected_file = self.get_test_loc('patch/patches/libmediainfo-0.7.43.diff.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_avahi_0_6_25_patches_configure_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/avahi-0.6.25/patches/configure.patch')
        expected_file = self.get_test_loc('patch/patches/misc/avahi-0.6.25/patches/configure.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_avahi_0_6_25_patches_main_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/avahi-0.6.25/patches/main.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/avahi-0.6.25/patches/main.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_busybox_patches_fix_subarch_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/busybox/patches/fix-subarch.patch')
        expected_file = self.get_test_loc('patch/patches/misc/busybox/patches/fix-subarch.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_busybox_patches_gtrick_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/busybox/patches/gtrick.patch')
        expected_file = self.get_test_loc('patch/patches/misc/busybox/patches/gtrick.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_busybox_patches_workaround_old_uclibc_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/busybox/patches/workaround_old_uclibc.patch')
        expected_file = self.get_test_loc('patch/patches/misc/busybox/patches/workaround_old_uclibc.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_curl_patches_ekioh_cookie_fix_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/curl/patches/ekioh_cookie_fix.patch')
        expected_file = self.get_test_loc('patch/patches/misc/curl/patches/ekioh_cookie_fix.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_e2fsprogs_1_37_uuidlibs_blkidlibs_only_target_makefile_in_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/e2fsprogs-1.37/uuidlibs_blkidlibs_only_target_Makefile.in.patch')
        expected_file = self.get_test_loc('patch/patches/misc/e2fsprogs-1.37/uuidlibs_blkidlibs_only_target_Makefile.in.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_ekioh_svg_opensource_patches_patch_ekioh_config_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/ekioh-svg/opensource/patches/patch_ekioh_config.patch')
        expected_file = self.get_test_loc('patch/patches/misc/ekioh-svg/opensource/patches/patch_ekioh_config.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_accelerated_blit_webcore_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/accelerated_blit_webcore.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/accelerated_blit_webcore.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_accelerated_blit_webkit_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/accelerated_blit_webkit.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/accelerated_blit_webkit.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_animated_gif_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/animated_gif.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/animated_gif.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_computed_style_for_transform_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/computed_style_for_transform.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/computed_style_for_transform.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_cookies_fixes_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/cookies_fixes.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/cookies_fixes.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_dlna_image_security_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/dlna_image_security.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/dlna_image_security.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_draw_pattern_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/draw_pattern.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/draw_pattern.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_enable_logs_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/enable_logs.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/enable_logs.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_enable_proxy_setup_log_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/enable_proxy_setup_log.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/enable_proxy_setup_log.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_file_secure_mode_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/file_secure_mode.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/file_secure_mode.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_http_secure_mode_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/http_secure_mode.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/http_secure_mode.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_javascript_screen_resolution_fix_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/javascript_screen_resolution_fix.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/javascript_screen_resolution_fix.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_keycode_webkit_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/keycode_webkit.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/keycode_webkit.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_local_file_access_whitelist_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/local_file_access_whitelist.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/local_file_access_whitelist.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_lower_case_css_attributes_for_transform_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/lower_case_css_attributes_for_transform.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/lower_case_css_attributes_for_transform.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_moving_empty_image_leaves_garbage_on_screen_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/moving_empty_image_leaves_garbage_on_screen.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/moving_empty_image_leaves_garbage_on_screen.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_open_in_new_window_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/open_in_new_window.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/open_in_new_window.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_plugin_thread_async_call_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/plugin_thread_async_call.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/plugin_thread_async_call.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_ram_cache_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/ram_cache.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/ram_cache.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_ram_cache_meta_expires_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/ram_cache_meta_expires.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/ram_cache_meta_expires.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_speedup_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/speedup.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/speedup.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_sync_xhr_https_access_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/sync_xhr_https_access.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/sync_xhr_https_access.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_useragent_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/useragent.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/useragent.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webcore_keyevent_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webcore_keyevent.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webcore_keyevent.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webcore_videoplane_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webcore_videoplane.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webcore_videoplane.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webkit_cssparser_parsetransitionshorthand_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webkit_CSSParser_parseTransitionShorthand.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webkit_CSSParser_parseTransitionShorthand.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webkit_database_support_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webkit_database_support.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webkit_database_support.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webkit_dlna_images_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webkit_dlna_images.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webkit_dlna_images.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webkit_finish_animations_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webkit_finish_animations.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webkit_finish_animations.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_patches_webkit_xmlhttprequest_cross_domain_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/patches/webkit_xmlhttprequest_cross_domain.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/patches/webkit_xmlhttprequest_cross_domain.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_moto_createobject_null_check_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/moto-createobject-null-check.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/moto-createobject-null-check.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_moto_dump_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/moto-dump.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/moto-dump.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_moto_getopensourcenotice_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/moto-getopensourcenotice.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/moto-getopensourcenotice.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_moto_jsvalue_equal_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/moto-jsvalue-equal.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/moto-jsvalue-equal.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_moto_timer_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/moto-timer.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/moto-timer.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_support_parallel_idl_gen_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/support_parallel_idl_gen.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/support_parallel_idl_gen.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_webcore_accept_click_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/webcore_accept_click.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/webcore_accept_click.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_webkit_opensource_prepatches_webcore_videoplane_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/webkit/opensource/prepatches/webcore_videoplane.patch')
        expected_file = self.get_test_loc('patch/patches/misc/webkit/opensource/prepatches/webcore_videoplane.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_icu_patches_ekioh_config_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/icu/patches/ekioh-config.patch')
        expected_file = self.get_test_loc('patch/patches/misc/icu/patches/ekioh-config.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_jfsutils_patches_largefile_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/jfsutils/patches/largefile.patch')
        expected_file = self.get_test_loc('patch/patches/misc/jfsutils/patches/largefile.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libasyncns_asyncns_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libasyncns/asyncns.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libasyncns/asyncns.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libasyncns_configure_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libasyncns/configure.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libasyncns/configure.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libdaemon_0_13_patches_configure_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libdaemon-0.13/patches/configure.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libdaemon-0.13/patches/configure.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libiconv_patches_cp932_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libiconv/patches/cp932.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libiconv/patches/cp932.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libiconv_patches_make_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libiconv/patches/make.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libiconv/patches/make.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libjpeg_v6b_patches_config_sub_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libjpeg-v6b/patches/config.sub.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libjpeg-v6b/patches/config.sub.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libjpeg_v6b_patches_configure_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libjpeg-v6b/patches/configure.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libjpeg-v6b/patches/configure.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libjpeg_v6b_patches_makefile_cfg_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libjpeg-v6b/patches/makefile.cfg.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libjpeg-v6b/patches/makefile.cfg.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libpng_1_2_8_makefile_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libpng-1.2.8/makefile.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libpng-1.2.8/makefile.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libpng_1_2_8_pngconf_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libpng-1.2.8/pngconf.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libpng-1.2.8/pngconf.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libpng_1_2_8_pngrutil_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libpng-1.2.8/pngrutil.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libpng-1.2.8/pngrutil.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_libxml2_patches_iconv_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/libxml2/patches/iconv.patch')
        expected_file = self.get_test_loc('patch/patches/misc/libxml2/patches/iconv.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_0001_stmmac_updated_the_driver_and_added_several_fixes_a_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/0001-stmmac-updated-the-driver-and-added-several-fixes-a.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/0001-stmmac-updated-the-driver-and-added-several-fixes-a.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_addrspace_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/addrspace.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/addrspace.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_arch_sh_kernel_cpu_init_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/arch_sh_kernel_cpu_init.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/arch_sh_kernel_cpu_init.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_arch_sh_makefile_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/arch_sh_Makefile.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/arch_sh_Makefile.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_arch_sh_mm_init_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/arch_sh_mm_init.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/arch_sh_mm_init.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_bigphysarea_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/bigphysarea.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/bigphysarea.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_bugs_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/bugs.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/bugs.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_cache_sh4_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/cache-sh4.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/cache-sh4.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_cfi_cmdset_0001_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/cfi_cmdset_0001.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/cfi_cmdset_0001.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_cfi_util_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/cfi_util.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/cfi_util.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_char_build_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/char_build.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/char_build.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_cmdlinepart_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/cmdlinepart.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/cmdlinepart.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_console_printk_loglevel_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/console_printk_loglevel.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/console_printk_loglevel.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_delayed_i2c_read_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/delayed_i2c_read.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/delayed_i2c_read.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_devinet_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/devinet.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/devinet.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_disable_carrier_sense_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/disable_carrier_sense.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/disable_carrier_sense.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_disable_unaligned_printks_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/disable_unaligned_printks.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/disable_unaligned_printks.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_dma_api_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/dma-api.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/dma-api.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_do_mounts_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/do_mounts.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/do_mounts.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_drivers_net_makefile_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/drivers_net_Makefile.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/drivers_net_Makefile.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_fan_ctrl_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/fan_ctrl.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/fan_ctrl.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_hcd_stm_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/hcd_stm.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/hcd_stm.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_head_s_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/head.S.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/head.S.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_i2c_stm_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/i2c-stm.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/i2c-stm.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_i2c_stm_c_patch2(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/i2c-stm.c.patch2')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/i2c-stm.c.patch2.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_i2c_nostop_for_bitbanging_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/i2c_nostop_for_bitbanging.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/i2c_nostop_for_bitbanging.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_i2c_rate_normal_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/i2c_rate_normal.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/i2c_rate_normal.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_i2c_revert_to_117_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/i2c_revert_to_117.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/i2c_revert_to_117.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_if_ppp_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/if_ppp.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/if_ppp.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_inittmpfs_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/inittmpfs.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/inittmpfs.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_init_kconfig_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/init_Kconfig.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/init_Kconfig.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_init_main_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/init_main.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/init_main.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_ioremap_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/ioremap.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/ioremap.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_ipconfig_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/ipconfig.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/ipconfig.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_kernel_extable_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/kernel_extable.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/kernel_extable.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_kernel_resource_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/kernel_resource.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/kernel_resource.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_kexec_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/kexec.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/kexec.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_ksymhash_elflib_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/ksymhash_elflib.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/ksymhash_elflib.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_libata_sense_data_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/libata_sense_data.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/libata_sense_data.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_localversion_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/localversion.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/localversion.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_mach_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/mach.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/mach.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_marvell_88e3015_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/marvell_88e3015.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/marvell_88e3015.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_mb442_setup_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/mb442_setup.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/mb442_setup.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_mmu_context_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/mmu_context.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/mmu_context.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_motorola_make_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/motorola_make.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/motorola_make.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_motorola_rootdisk_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/motorola_rootdisk.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/motorola_rootdisk.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_namespace_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/namespace.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/namespace.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_nand_flash_based_bbt_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/nand_flash_based_bbt.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/nand_flash_based_bbt.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_nand_old_oob_layout_for_yaffs2_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/nand_old_oob_layout_for_yaffs2.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/nand_old_oob_layout_for_yaffs2.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_netconsole_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/netconsole.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/netconsole.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_netconsole_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/netconsole.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/netconsole.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_nfsroot_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/nfsroot.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/nfsroot.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_page_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/page.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/page.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_page_alloc_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/page_alloc.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/page_alloc.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_pgtable_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/pgtable.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/pgtable.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_phy_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/phy.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/phy.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_phy_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/phy.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/phy.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_phy_device_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/phy_device.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/phy_device.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_pid_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/pid.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/pid.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_pio_irq_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/pio-irq.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/pio-irq.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_pmb_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/pmb.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/pmb.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_process_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/process.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/process.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_sample_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/sample.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/sample.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_sched_cfs_v2_6_23_12_v24_1_mod_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/sched-cfs-v2.6.23.12-v24.1.mod.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/sched-cfs-v2.6.23.12-v24.1.mod.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_setup_stb7100_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/setup-stb7100.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/setup-stb7100.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_setup_stx7105_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/setup-stx7105.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/setup-stx7105.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_setup_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/setup.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/setup.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_sh_kernel_setup_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/sh_kernel_setup.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/sh_kernel_setup.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_sh_ksyms_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/sh_ksyms.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/sh_ksyms.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_smsc_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/smsc.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/smsc.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_smsc_makefile_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/smsc_makefile.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/smsc_makefile.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_soc_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/soc.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/soc.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_squashfs3_3_revert_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/squashfs3.3_revert.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/squashfs3.3_revert.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_squashfs3_3_revert1_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/squashfs3.3_revert1.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/squashfs3.3_revert1.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_squashfs3_3_revert2_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/squashfs3.3_revert2.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/squashfs3.3_revert2.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_squashfs3_3_revert3_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/squashfs3.3_revert3.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/squashfs3.3_revert3.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_squashfs3_4_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/squashfs3.4.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/squashfs3.4.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_stasc_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/stasc.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/stasc.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_stmmac_main_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/stmmac_main.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/stmmac_main.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_suppress_igmp_report_listening_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/suppress_igmp_report_listening.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/suppress_igmp_report_listening.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_time_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/time.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/time.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_unionfs_2_5_1_for_2_6_23_17_diff(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/unionfs-2.5.1_for_2.6.23.17.diff')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/unionfs-2.5.1_for_2.6.23.17.diff.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_unionfs_remove_debug_printouts_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/unionfs_remove_debug_printouts.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/unionfs_remove_debug_printouts.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_vip19x0_vidmem_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/vip19x0_vidmem.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/vip19x0_vidmem.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_vip19x3_board_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/vip19x3_board.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/vip19x3_board.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_vip19xx_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/vip19xx.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/vip19xx.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_vip19xx_nand_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/vip19xx_nand.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/vip19xx_nand.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_vip19xx_nor_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/vip19xx_nor.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/vip19xx_nor.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_vt_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/vt.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/vt.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_yaffs2_2008_07_15_for_2_6_23_17_yaffs_guts_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/yaffs2-2008.07.15_for_2.6.23.17-yaffs_guts.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/yaffs2-2008.07.15_for_2.6.23.17-yaffs_guts.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_linux_st710x_patches_yaffs2_2008_07_15_for_2_6_23_17_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/linux-st710x/patches/yaffs2-2008.07.15_for_2.6.23.17.patch')
        expected_file = self.get_test_loc('patch/patches/misc/linux-st710x/patches/yaffs2-2008.07.15_for_2.6.23.17.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_npapi_patches_npapi_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/npapi/patches/npapi.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/npapi/patches/npapi.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_openssl_0_9_8_patches_configure_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/openssl-0.9.8/patches/Configure.patch')
        expected_file = self.get_test_loc('patch/patches/misc/openssl-0.9.8/patches/Configure.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_sqlite_patches_permissions_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/sqlite/patches/permissions.patch')
        expected_file = self.get_test_loc('patch/patches/misc/sqlite/patches/permissions.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_arpping_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/arpping.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/arpping.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_clientpacket_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/clientpacket.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/clientpacket.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_clientpacket_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/clientpacket.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/clientpacket.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_debug_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/debug.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/debug.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_dhcpc_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/dhcpc.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/dhcpc.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_dhcpc_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/dhcpc.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/dhcpc.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_dhcpd_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/dhcpd.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/dhcpd.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_makefile_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/Makefile.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/Makefile.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_options_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/options.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/options.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_options_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/options.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/options.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_packet_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/packet.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/packet.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_packet_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/packet.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/packet.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_route_patch1(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/route.patch1')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/route.patch1.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_script_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/script.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/script.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_udhcp_0_9_8_patch_t1t2_patch1(self):
        test_file = self.get_test_loc(u'patch/patches/misc/udhcp-0.9.8/patch/t1t2.patch1')
        expected_file = self.get_test_loc('patch/patches/misc/udhcp-0.9.8/patch/t1t2.patch1.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_vqec_patch_build_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/vqec/patch/BUILD.patch')
        expected_file = self.get_test_loc('patch/patches/misc/vqec/patch/BUILD.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_vqec_patch_cross_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/vqec/patch/cross.patch')
        expected_file = self.get_test_loc('patch/patches/misc/vqec/patch/cross.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_vqec_patch_uclibc_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/vqec/patch/uclibc.patch')
        expected_file = self.get_test_loc('patch/patches/misc/vqec/patch/uclibc.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_vqec_patch_vqec_ifclient_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/vqec/patch/vqec_ifclient.patch')
        expected_file = self.get_test_loc('patch/patches/misc/vqec/patch/vqec_ifclient.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_vqec_patch_vqec_wv_c_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/vqec/patch/vqec_wv.c.patch')
        expected_file = self.get_test_loc('patch/patches/misc/vqec/patch/vqec_wv.c.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_misc_vqec_patch_vqec_wv_h_patch(self):
        test_file = self.get_test_loc(u'patch/patches/misc/vqec/patch/vqec_wv.h.patch')
        expected_file = self.get_test_loc('patch/patches/misc/vqec/patch/vqec_wv.h.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_postgrey_1_30_group_patch(self):
        test_file = self.get_test_loc(u'patch/patches/postgrey-1.30-group.patch')
        expected_file = self.get_test_loc('patch/patches/postgrey-1.30-group.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_drupal_upload_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/drupal_upload.patch')
        expected_file = self.get_test_loc('patch/patches/windows/drupal_upload.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_ether_patch_1_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/ether_patch_1.patch')
        expected_file = self.get_test_loc('patch/patches/windows/ether_patch_1.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_js_delete_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/js_delete.patch')
        expected_file = self.get_test_loc('patch/patches/windows/js_delete.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_plugin_explorer_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/plugin explorer.patch')
        expected_file = self.get_test_loc('patch/patches/windows/plugin explorer.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_resolveentity32_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/resolveentity32.patch')
        expected_file = self.get_test_loc('patch/patches/windows/resolveentity32.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_sift_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/sift.patch')
        expected_file = self.get_test_loc('patch/patches/windows/sift.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_thumbnail_support_0_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/thumbnail_support_0.patch')
        expected_file = self.get_test_loc('patch/patches/windows/thumbnail_support_0.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_thumbnail_support_0_patch_1(self):
        test_file = self.get_test_loc(u'patch/patches/windows/thumbnail_support_0.patch.1')
        expected_file = self.get_test_loc('patch/patches/windows/thumbnail_support_0.patch.1.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_webform_3_0_conditional_constructor_0_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/webform-3.0-conditional_constructor_0.patch')
        expected_file = self.get_test_loc('patch/patches/windows/webform-3.0-conditional_constructor_0.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_windows_xml_rpc_addspace_patch(self):
        test_file = self.get_test_loc(u'patch/patches/windows/xml_rpc_addSpace.patch')
        expected_file = self.get_test_loc('patch/patches/windows/xml_rpc_addSpace.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_xvidcap_1_1_6_docdir_patch(self):
        test_file = self.get_test_loc(u'patch/patches/xvidcap-1.1.6-docdir.patch')
        expected_file = self.get_test_loc('patch/patches/xvidcap-1.1.6-docdir.patch.expected')
        check_patch(test_file, expected_file)

    def test_patch_info_patch_patches_xvidcap_xorg_patch(self):
        test_file = self.get_test_loc(u'patch/patches/xvidcap-xorg.patch')
        expected_file = self.get_test_loc('patch/patches/xvidcap-xorg.patch.expected')
        check_patch(test_file, expected_file)
