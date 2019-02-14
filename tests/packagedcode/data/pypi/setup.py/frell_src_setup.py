


from setuptools import setup, find_packages
from setuptools.command.test import test as TestCommand
import imp
import os
import sys


class PyTest(TestCommand):
    user_options = [("pytest-args=", "a", "Arguments to pass to py.test")]

    def initialize_options(self):
        TestCommand.initialize_options(self)
        self.pytest_args = []

    def finalize_options(self):
        TestCommand.finalize_options(self)
        self.test_args = []
        self.test_suite = True

    def run_tests(self):
        # import here, cause outside the eggs aren't loaded
        import pytest
        errno = pytest.main(self.pytest_args)
        sys.exit(errno)


def read_file(filename):
    """Read  file into a string"""
    path = os.path.abspath(os.path.dirname(__file__))
    filepath = os.path.join(path, filename)
    with open(filepath) as fh:
        return fh.read()


setup(
    name="@NAME@",
    version=imp.load_source("@MODULE@.constants",
                            "@MODULE@/constants.py").get_version(),
    description="Python module @MODULE@",
    author="Brett Smith",
    author_email="bc.smith@sas.com",
    license="Apache License 2.0",
    packages=find_packages(),
    install_requires=read_file("requirements.txt"),
    tests_require=["pytest", "mock"],
    cmdclass={"test": PyTest},
)
