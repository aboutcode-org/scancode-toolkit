# -*- coding: utf-8 -*-
#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import os
import subprocess

import pytest

from commoncode import fileutils
from commoncode.system import on_windows
from commoncode.system import on_linux
from commoncode.testcase import FileDrivenTesting
from formattedcode import validate_output_file_path
from commoncode.testcase import make_non_writable
from commoncode.filetype import is_writable

test_env = FileDrivenTesting()


def test_validate_output_file_path_with_non_existing_file_in_writable_path():
    test_path = test_env.get_temp_dir('test_dir')
    test_file = os.path.join(test_path, 'some-non-existing-path')
    validate_output_file_path(test_file)


def test_validate_output_file_path_with_existing_writable_file():
    test_path = test_env.get_temp_dir('test_dir')
    test_file = os.path.join(test_path, 'some-existing-path')
    with open(test_file, 'w') as tp:
        tp.write("foo")
    validate_output_file_path(test_file)


def test_validate_output_file_path_with_existing_writable_dir_raise_exception():
    test_path = test_env.get_temp_dir('test_dir')
    test_file = os.path.join(test_path, 'non-existing-parent', 'non-existing-path')
    with pytest.raises(Exception):
        validate_output_file_path(test_file)


def test_validate_output_file_path_with_existing_writable_parent_dir_raise_exception():
    test_path = test_env.get_temp_dir('test_dir')
    with pytest.raises(Exception):
        validate_output_file_path(test_path)


@pytest.mark.skipif(not on_linux, reason='This special file is only on Linux')
def test_validate_output_file_path_with_existing_system_device_file_raise_exception():
    test_file = '/dev/ppp'
    with pytest.raises(Exception):
        validate_output_file_path(test_file)


@pytest.mark.skipif(not on_linux, reason='Special files are easier to test on Linux')
def test_validate_output_file_path_with_existing_fifo_pipe_special_file_raise_exception():
    from uuid import uuid4
    test_file = f"/tmp/scancode-test-{uuid4().hex}"
    try:
        # p      create a FIFO
        subprocess.check_call(["mknod", test_file, "p"])
        with pytest.raises(Exception):
            validate_output_file_path(test_file)
    finally:
        fileutils.delete(location=test_file)


@pytest.mark.skipif(on_windows, reason='It is hard to have non-readable files on Windows')
def test_validate_output_file_path_with_non_existing_file_in_non_writable_path_raise_exception():
    test_dir = test_env.get_temp_dir('test_dir')
    # make dir non writable
    test_file = os.path.join(test_dir, 'some-non-existing-path')
    try:
        # make dir non writable
        make_non_writable(test_dir)
        assert not is_writable(test_dir)
        with pytest.raises(Exception):
            validate_output_file_path(test_file)
    finally:
        fileutils.chmod(test_dir, fileutils.RW, recurse=True)

@pytest.mark.skipif(on_windows, reason='It is hard to have non-readable/writable files on Windows')
def test_validate_output_file_path_with_existing_non_writable_file_raise_exception():
    test_dir = test_env.get_temp_dir('test_dir')
    test_file = os.path.join(test_dir, 'some-existing-path')
    with open(test_file, 'w') as tp:
        tp.write("foo")
    try:
        # make file non writable
        make_non_writable(test_file)
        assert not is_writable(test_file)
        with pytest.raises(Exception):
            validate_output_file_path(test_file)
    finally:
        fileutils.chmod(test_dir, fileutils.RW, recurse=True)
