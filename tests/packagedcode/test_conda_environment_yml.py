import os
from packages_test_utils import PackageTester
from packagedcode import conda
from scancode_config import REGEN_TEST_FIXTURES

class TestCondaEnvironmentYml(PackageTester):
    test_data_dir = os.path.join(os.path.dirname(__file__), 'data')

    def test_conda_environment_yml_is_datafile(self):
        test_file = self.get_test_loc('conda/environment_yml/simple-environment.yml')
        assert conda.CondaEnvironmentYmlHandler.is_datafile(test_file)

    def test_parse_simple_environment_yml(self):
        test_file = self.get_test_loc('conda/environment_yml/simple-environment.yml')
        packages = list(conda.CondaEnvironmentYmlHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        
        assert package.name == 'testenv'
        assert package.extra_data == {'channels': ['conda-forge', 'defaults']}
        
        deps = package.dependencies
        
        numpy_dep = next((d for d in deps if d.purl == 'pkg:conda/numpy'), None)
        assert numpy_dep is not None
        assert numpy_dep.extracted_requirement == '1.24.0'
        
        requests_dep = next((d for d in deps if d.purl == 'pkg:pypi/requests'), None)
        assert requests_dep is not None
        assert requests_dep.extracted_requirement == '2.28.0'

    def test_parse_real_environment_yml(self):
        test_file = self.get_test_loc('conda/environment_yml/multiregex-environment.yml')
        packages = list(conda.CondaEnvironmentYmlHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        
        assert package.name == 'myenv'
        assert len(package.dependencies) > 0
        deps = [d.purl for d in package.dependencies]
        assert 'pkg:conda/pandas' in deps

    def test_parse_empty_dependencies(self):
        test_file = self.get_temp_file('empty-deps.yml')
        with open(test_file, 'w') as f:
            f.write('name: nodeps\nchannels:\n  - defaults\ndependencies:\n')
        
        packages = list(conda.CondaEnvironmentYmlHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert package.name == 'nodeps'
        assert package.dependencies == []

    def test_parse_missing_name(self):
        test_file = self.get_temp_file('noname.yml')
        with open(test_file, 'w') as f:
            f.write('channels:\n  - defaults\ndependencies:\n  - python=3.10\n')
            
        packages = list(conda.CondaEnvironmentYmlHandler.parse(test_file))
        assert len(packages) == 1
        package = packages[0]
        assert package.name is None
        assert len(package.dependencies) == 1
