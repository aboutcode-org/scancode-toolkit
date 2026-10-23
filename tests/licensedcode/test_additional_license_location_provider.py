#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from unittest import mock
import pytest

from licensedcode.additional_license_location_provider import (
    AdditionalLicenseLocationProviderPlugin,
    AdditionalLicensePluginManager,
    ProvidedLocationError,
    get_location,
    location_provider_spec,
    location_provider_impl,
)


class DummyBase(object):
    pass


class ValidPlugin(DummyBase):
    pass


class InvalidPlugin(object):
    pass


class ValidLocationPlugin(AdditionalLicenseLocationProviderPlugin):
    def __init__(self, locations=None):
        self._locations = locations or {}

    def get_locations(self):
        return self._locations


def test_decorators_are_callable():
    @location_provider_spec
    class SpecClass:
        pass

    @location_provider_impl
    class ImplClass:
        pass

    assert SpecClass is not None
    assert ImplClass is not None


def test_additional_license_plugin_manager_init():
    mgr = AdditionalLicensePluginManager(
        project_name="test_proj",
        entrypoint="test_entrypoint",
        plugin_base_class=DummyBase,
    )
    assert mgr.project_name == "test_proj"
    assert mgr.entrypoint == "test_entrypoint"
    assert mgr.plugin_base_class is DummyBase
    assert mgr.initialized is False
    assert mgr.plugin_classes == {}


def test_additional_license_plugin_manager_setup_empty():
    mgr = AdditionalLicensePluginManager(
        project_name="test_proj",
        entrypoint="non_existent_entrypoint_group_12345",
        plugin_base_class=DummyBase,
    )
    result = mgr.setup()
    assert list(result) == []
    assert mgr.initialized is True
    # Calling setup again returns cached values
    assert list(mgr.setup()) == []


def test_additional_license_plugin_manager_setup_with_valid_plugin():
    mgr = AdditionalLicensePluginManager(
        project_name="test_proj",
        entrypoint="test_ep",
        plugin_base_class=DummyBase,
    )

    mock_ep = mock.MagicMock()
    mock_ep.name = "valid_plug"
    mock_ep.load.return_value = ValidPlugin

    with mock.patch("importlib.metadata.entry_points", return_value=[mock_ep]):
        classes = list(mgr.setup())

    assert len(classes) == 1
    assert classes[0] is ValidPlugin
    assert ValidPlugin.name == "valid_plug"
    assert mgr.plugin_classes == {"valid_plug": ValidPlugin}
    assert mgr.initialized is True


def test_additional_license_plugin_manager_setup_with_invalid_plugin():
    mgr = AdditionalLicensePluginManager(
        project_name="test_proj",
        entrypoint="test_ep",
        plugin_base_class=DummyBase,
    )

    mock_ep = mock.MagicMock()
    mock_ep.name = "invalid_plug"
    mock_ep.load.return_value = InvalidPlugin

    with mock.patch("importlib.metadata.entry_points", return_value=[mock_ep]):
        with pytest.raises(Exception) as excinfo:
            mgr.setup()

    assert "Invalid plugin: 'invalid_plug'" in str(excinfo.value)
    assert "must extend" in str(excinfo.value)


def test_get_location_from_cache():
    cached = {"key1": "/path/to/key1"}
    assert get_location("key1", _cached_locations=cached) == "/path/to/key1"
    assert get_location("non_existent", _cached_locations=cached) is None


def test_get_location_duplicate_keys(tmp_path):
    existing_dir = str(tmp_path)

    class Plugin1(AdditionalLicenseLocationProviderPlugin):
        def get_locations(self):
            return {"dup_key": existing_dir}

    class Plugin2(AdditionalLicenseLocationProviderPlugin):
        def get_locations(self):
            return {"dup_key": existing_dir}

    mock_mgr = mock.MagicMock()
    mock_mgr.plugin_classes = {
        "p1": Plugin1,
        "p2": Plugin2,
    }

    with mock.patch(
        "licensedcode.additional_license_location_provider.additional_license_location_provider_plugins",
        mock_mgr,
    ):
        with pytest.raises(ProvidedLocationError) as excinfo:
            get_location("dup_key", _cached_locations={})

    assert "Duplicate location key provided: dup_key" in str(excinfo.value)


def test_get_location_non_existing_location():
    class MissingPlugin(AdditionalLicenseLocationProviderPlugin):
        def get_locations(self):
            return {"missing_key": "/this/path/does/not/exist/at/all/12345"}

    mock_mgr = mock.MagicMock()
    mock_mgr.plugin_classes = {
        "missing": MissingPlugin,
    }

    with mock.patch(
        "licensedcode.additional_license_location_provider.additional_license_location_provider_plugins",
        mock_mgr,
    ):
        with pytest.raises(ProvidedLocationError) as excinfo:
            get_location("missing_key", _cached_locations={})

    assert "Non-existing locations provided" in str(excinfo.value)
