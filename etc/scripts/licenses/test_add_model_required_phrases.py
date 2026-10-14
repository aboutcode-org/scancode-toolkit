#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import builtins
from pathlib import Path
import runpy
import sys
from types import ModuleType

import pytest


SCRIPT = Path(__file__).with_name("add_model_required_phrases.py")
MISSING_COMMAND = (
    "The scancode-required-phrases model command is required. "
    "Install or update the package with its inference extra."
)


def load_wrapper():
    return runpy.run_path(str(SCRIPT))


def test_import_does_not_load_package_or_ml_libraries(monkeypatch):
    original_import = builtins.__import__

    def guarded_import(name, *args, **kwargs):
        if name.split(".", 1)[0] in {
            "scancode_required_phrases",
            "torch",
            "transformers",
        }:
            pytest.fail(f"unexpected import: {name}")
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", guarded_import)

    assert callable(load_wrapper()["main"])


def test_main_delegates_arguments_and_exit(monkeypatch):
    calls = []

    def command():
        calls.append(tuple(sys.argv))
        raise SystemExit(7)

    package = ModuleType("scancode_required_phrases")
    package.__path__ = []
    model_cli = ModuleType("scancode_required_phrases.model_cli")
    model_cli.add_model_required_phrases = command
    monkeypatch.setitem(sys.modules, "scancode_required_phrases", package)
    monkeypatch.setitem(sys.modules, "scancode_required_phrases.model_cli", model_cli)
    monkeypatch.setattr(sys, "argv", [str(SCRIPT), "--predict-only"])

    with pytest.raises(SystemExit) as error:
        load_wrapper()["main"]()

    assert error.value.code == 7
    assert calls == [(str(SCRIPT), "--predict-only")]


@pytest.mark.parametrize(
    "missing_name",
    [
        "scancode_required_phrases",
        "scancode_required_phrases.model_cli",
    ],
)
def test_main_reports_a_missing_package_command(monkeypatch, missing_name):
    original_import = builtins.__import__

    def missing_import(name, *args, **kwargs):
        if name == "scancode_required_phrases.model_cli":
            raise ModuleNotFoundError(
                f"No module named {missing_name!r}",
                name=missing_name,
            )
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing_import)

    with pytest.raises(SystemExit) as error:
        load_wrapper()["main"]()

    assert error.value.code == MISSING_COMMAND
    assert error.value.__cause__ is None


def test_main_does_not_hide_an_unrelated_import_error(monkeypatch):
    original_import = builtins.__import__
    missing_dependency = ModuleNotFoundError("No module named 'dependency'", name="dependency")

    def missing_import(name, *args, **kwargs):
        if name == "scancode_required_phrases.model_cli":
            raise missing_dependency
        return original_import(name, *args, **kwargs)

    monkeypatch.setattr(builtins, "__import__", missing_import)

    with pytest.raises(ModuleNotFoundError) as error:
        load_wrapper()["main"]()

    assert error.value is missing_dependency
