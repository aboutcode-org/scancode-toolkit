import json
import os
import tempfile

from packagedcode import nuget
from packages_test_utils import PackageTester


class TestDotNetDepsJson(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_deps_json_is_datafile(self):
        test_file = self.get_test_loc('nuget/deps_json/simple.deps.json')
        assert nuget.DotNetDepsJsonHandler.is_datafile(test_file)

    def test_parse_simple_deps_json(self):
        test_file = self.get_test_loc('nuget/deps_json/simple.deps.json')
        packages = list(nuget.DotNetDepsJsonHandler.parse(test_file))

        assert len(packages) == 2

        # MyApp/1.0.0
        my_app_packages = [p for p in packages if p.name == 'MyApp']
        assert len(my_app_packages) == 1
        my_app = my_app_packages[0]
        assert my_app.name == 'MyApp'
        assert my_app.version == '1.0.0'
        assert my_app.extra_data.get('type') == 'project'
        assert my_app.extra_data.get('target_framework') == '.NETCoreApp,Version=v6.0'

        assert len(my_app.dependencies) == 1
        dep = my_app.dependencies[0]
        assert dep.get('purl') == 'pkg:nuget/Newtonsoft.Json@13.0.1'
        assert dep.get('extracted_requirement') == '13.0.1'
        assert dep.get('is_pinned') is True
        assert dep.get('is_direct') is True

        # Newtonsoft.Json/13.0.1
        json_packages = [p for p in packages if p.name == 'Newtonsoft.Json']
        assert len(json_packages) == 1
        json_pkg = json_packages[0]
        assert json_pkg.name == 'Newtonsoft.Json'
        assert json_pkg.version == '13.0.1'
        assert json_pkg.extra_data.get('type') == 'package'
        assert len(json_pkg.dependencies) == 0


    def test_parse_snoop_deps_json(self):
        test_file = self.get_test_loc('nuget/deps_json/Snoop.Core.deps.json')
        packages = list(nuget.DotNetDepsJsonHandler.parse(test_file))

        # The Snoop file has 45 items in the "libraries" section
        assert len(packages) == 45

        # Check for the main project
        snoop_pkgs = [p for p in packages if p.name == 'Snoop.Core']
        assert len(snoop_pkgs) == 1
        snoop = snoop_pkgs[0]
        assert snoop.name == 'Snoop.Core'
        assert snoop.version == '1.0.0'
        # Snoop.Core has 7 dependencies listed
        assert len(snoop.dependencies) == 7

        # Check one known dependency from the list
        jb_packages = [p for p in packages if p.name == 'JetBrains.Annotations']
        assert len(jb_packages) == 1
        jb = jb_packages[0]
        assert jb.name == 'JetBrains.Annotations'
        assert jb.version == '2023.2.0'


    def test_parse_empty_libraries_deps_json(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "runtimeTarget": {"name": ".NETCoreApp,Version=v6.0"},
                "libraries": {}
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 0
        finally:
            os.remove(temp_path)

    def test_parse_without_runtime_target_uses_targets(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "targets": {
                    ".NETCoreApp,Version=v8.0": {
                        "App/1.0.0": {
                            "dependencies": {
                                "Newtonsoft.Json": "13.0.3"
                            }
                        },
                        "Newtonsoft.Json/13.0.3": {}
                    }
                },
                "libraries": {
                    "App/1.0.0": {"type": "project"},
                    "Newtonsoft.Json/13.0.3": {"type": "package"}
                }
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 2

            app = [p for p in packages if p.name == 'App'][0]
            assert app.extra_data.get('target_framework') == '.NETCoreApp,Version=v8.0'
            assert len(app.dependencies) == 1
            dependency = app.dependencies[0]
            assert dependency.get('purl') == 'pkg:nuget/Newtonsoft.Json@13.0.3'
            assert dependency.get('scope') == '.NETCoreApp,Version=v8.0'
        finally:
            os.remove(temp_path)

    def test_parse_runtime_target_mismatch_falls_back_to_targets(self):
        fd, temp_path = tempfile.mkstemp(suffix='.deps.json')
        with os.fdopen(fd, 'w') as f:
            json.dump({
                "runtimeTarget": {"name": ".NETCoreApp,Version=v8.0/win-x64"},
                "targets": {
                    ".NETCoreApp,Version=v8.0": {
                        "App/1.0.0": {
                            "dependencies": {
                                "Serilog": "3.1.0"
                            }
                        },
                        "Serilog/3.1.0": {}
                    }
                },
                "libraries": {
                    "App/1.0.0": {"type": "project"},
                    "Serilog/3.1.0": {"type": "package"}
                }
            }, f)

        try:
            packages = list(nuget.DotNetDepsJsonHandler.parse(temp_path))
            assert len(packages) == 2

            app = [p for p in packages if p.name == 'App'][0]
            assert app.extra_data.get('target_framework') == '.NETCoreApp,Version=v8.0'
            assert len(app.dependencies) == 1
            dependency = app.dependencies[0]
            assert dependency.get('purl') == 'pkg:nuget/Serilog@3.1.0'
            assert dependency.get('scope') == '.NETCoreApp,Version=v8.0'
        finally:
            os.remove(temp_path)
