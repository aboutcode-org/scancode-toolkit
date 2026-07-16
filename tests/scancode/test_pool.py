#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import multiprocessing

import pytest

from commoncode.system import on_linux
from licensedcode import cache
from scancode.pool import get_pool


PARENT_CACHE_SENTINEL = 'parent-warmed-license-cache'


def _get_worker_license_cache_state():
    """
    Return the worker's license cache singleton state and multiprocessing start
    method.
    """
    from licensedcode import cache

    return cache._LICENSE_CACHE, multiprocessing.get_start_method()


@pytest.mark.skipif(not on_linux, reason='Linux-only multiprocessing default')
def test_license_cache_warmup_is_inherited_by_pool_workers(monkeypatch):
    """
    ScanCode warms the license cache before creating its process pool so forked
    child processes inherit the loaded index instead of loading private copies.
    """
    monkeypatch.setattr(cache, '_LICENSE_CACHE', PARENT_CACHE_SENTINEL)

    with get_pool(processes=1) as scan_pool:
        worker_cache_state, worker_start_method = scan_pool.apply(
            _get_worker_license_cache_state,
        )

    assert worker_cache_state == PARENT_CACHE_SENTINEL, (
        'Pool worker did not inherit the parent-warmed license cache. '
        f'Worker start method was {worker_start_method!r}.'
    )
