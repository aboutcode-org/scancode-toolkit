#
# Copyright (c) nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#

from contextlib import contextmanager

import fasteners

"""
An interprocess lockfile with a timeout.
"""


class LockTimeout(Exception):
    pass


class FileLock(fasteners.InterProcessLock):

    @contextmanager
    def locked(self, timeout):
        acquired = self.acquire(timeout=timeout)
        if not acquired:
            raise LockTimeout(timeout=timeout)
        try:
            yield
        finally:
            self.release()
