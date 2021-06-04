#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from packagedcode import nevra


class TestNevra():

    def test_rpm_details_cups(self):
        expected1 = (None, 'cups', '1.1.17', '13.3.29', 'src')
        output1 = nevra.from_name('cups-1.1.17-13.3.29.src')
        assert output1 == expected1

    def test_rpm_details_imagemagick(self):
        expected2 = (None, 'ImageMagick-c++-devel', '6.0.7.1', '14', 'sparc')
        output2 = nevra.from_name('ImageMagick-c++-devel-6.0.7.1-14.sparc')
        assert output2 == expected2

    def test_rpm_details_flash_player(self):
        expected3 = (None, 'flash-player', '11.0.1.152', '2.1.1', 'nosrc')
        output3 = nevra.from_name('flash-player-11.0.1.152-2.1.1.nosrc')
        assert output3 == expected3

    def test_rpm_details_firmware(self):
        expected4 = (None, 'FirmwareUpdateKit', '1.6', '6.1.2', 'src')
        output4 = nevra.from_name('FirmwareUpdateKit-1.6-6.1.2.src')
        assert output4 == expected4

    def test_rpm_details_2048(self):
        expected5 = (None, '2048-cli', '0.9', '4.git20141214.723738c.el6', 'src')
        output5 = nevra.from_name('2048-cli-0.9-4.git20141214.723738c.el6.src')
        assert output5 == expected5

    def test_rpm_details_barebones(self):
        expected6 = (None, 'BareBonesBrowserLaunch', '3.1', '1.el6', 'src')
        output6 = nevra.from_name('BareBonesBrowserLaunch-3.1-1.el6.src')
        assert output6 == expected6

    def test_rpm_details_imagemagickcpp(self):
        expected7 = (None, 'ImageMagick-c++', '5.5.6', '15', 'i386')
        output7 = nevra.from_name('ImageMagick-c++-5.5.6-15.i386.rpm')
        assert output7 == expected7

    def test_rpm_details_xfree(self):
        expected8 = (None, 'XFree86-ISO8859-9-75dpi-fonts', '4.3.0', '97.EL', 'x86_64')
        output8 = nevra.from_name('XFree86-ISO8859-9-75dpi-fonts-4.3.0-97.EL.x86_64.rpm')
        assert output8 == expected8
