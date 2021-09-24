#
# Copyright (c) nexB Inc. and others. All rights reserved.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/commoncode for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os

from commoncode.testcase import FileDrivenTesting
from commoncode.cliutils import progressmanager

class TestProgressBar(FileDrivenTesting):

    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_progressmanager_works(self):
        iterable = range(10)
        with progressmanager(iterable) as it:
            for _ in it:
                pass

    def test_progressmanager_verbose(self):
        iterable = range(10)
        with progressmanager(iterable, verbose=True) as it:
            for _ in it:
                pass
