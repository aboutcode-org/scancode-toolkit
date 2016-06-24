#
# Copyright (c) 2016 nexB Inc. and others. All rights reserved.
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

from __future__ import absolute_import, print_function

from packagedcode import nevra


class TestNevra():

    def test_rpm_details_cups(self):
        expected1 = (None, 'cups', '1.1.17', '13.3.29', 'src')
        output1 = nevra.from_name('cups-1.1.17-13.3.29.src')
        assert expected1 == output1

    def test_rpm_details_imagemagick(self):
        expected2 = (None, 'ImageMagick-c++-devel', '6.0.7.1', '14', 'sparc')
        output2 = nevra.from_name('ImageMagick-c++-devel-6.0.7.1-14.sparc')
        assert expected2 == output2

    def test_rpm_details_flash_player(self):
        expected3 = (None, 'flash-player', '11.0.1.152', '2.1.1', 'nosrc')
        output3 = nevra.from_name('flash-player-11.0.1.152-2.1.1.nosrc')
        assert expected3 == output3

    def test_rpm_details_firmware(self):
        expected4 = (None, 'FirmwareUpdateKit', '1.6', '6.1.2', 'src')
        output4 = nevra.from_name('FirmwareUpdateKit-1.6-6.1.2.src')
        assert expected4 == output4

    def test_rpm_details_2048(self):
        expected5 = (None, '2048-cli', '0.9', '4.git20141214.723738c.el6', 'src')
        output5 = nevra.from_name('2048-cli-0.9-4.git20141214.723738c.el6.src')
        assert expected5 == output5

    def test_rpm_details_barebones(self):
        expected6 = (None, 'BareBonesBrowserLaunch', '3.1', '1.el6', 'src')
        output6 = nevra.from_name('BareBonesBrowserLaunch-3.1-1.el6.src')
        assert expected6 == output6

    def test_rpm_details_imagemagickcpp(self):
        expected7 = (None, 'ImageMagick-c++', '5.5.6', '15', 'i386')
        output7 = nevra.from_name('ImageMagick-c++-5.5.6-15.i386.rpm')
        assert expected7 == output7

    def test_rpm_details_xfree(self):
        expected8 = (None, 'XFree86-ISO8859-9-75dpi-fonts', '4.3.0', '97.EL', 'x86_64')
        output8 = nevra.from_name('XFree86-ISO8859-9-75dpi-fonts-4.3.0-97.EL.x86_64.rpm')
        assert expected8 == output8
