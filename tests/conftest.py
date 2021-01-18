import pytest


def pytest_addoption(parser):
    parser.addoption('--update-goldens', action='store_true', help='reset golden master benchmarks')
