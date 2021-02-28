#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
from time import sleep
import threading

from commoncode.testcase import FileBasedTesting
from scancode import interrupt


"""
Note that these tests check the active threads count before and after each test to
verify there is no thread leak.
"""


class TestInterrupt(FileBasedTesting):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_interruptible_can_run_function(self):
        before = threading.active_count()

        def some_long_function(exec_time):
            sleep(exec_time)
            return 'OK'

        results = interrupt.interruptible(some_long_function, args=(0.01,), timeout=10)
        expected = None, 'OK'
        assert results == expected

        after = threading.active_count()
        assert after == before

    def test_interruptible_stops_execution_on_timeout(self):
        before = threading.active_count()

        def some_long_function(exec_time):
            for i in range(exec_time):
                sleep(i)
            return 'OK'

        results = interrupt.interruptible(some_long_function, args=(20,), timeout=0.1)
        expected = 'ERROR: Processing interrupted: timeout after 0 seconds.', None
        assert results == expected

        after = threading.active_count()
        assert after == before

    def test_interruptible_stops_execution_on_exception(self):
        before = threading.active_count()

        def some_crashing_function():
            raise Exception('I have to crash. Now!')

        results, _ = interrupt.interruptible(some_crashing_function, timeout=1.0)
        assert 'ERROR: Unknown error:' in results
        assert 'I have to crash. Now!' in results

        after = threading.active_count()
        assert after == before

    def test_fake_interruptible_stops_execution_on_exception(self):
        def some_crashing_function():
            raise Exception('I have to crash. Now!')

        results, _ = interrupt.fake_interruptible(some_crashing_function, timeout=1.0)
        assert 'ERROR: Unknown error:' in results
        assert 'I have to crash. Now!' in results
