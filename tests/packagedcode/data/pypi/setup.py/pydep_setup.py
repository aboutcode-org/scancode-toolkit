from setuptools import setup

setup(
    name='pydep',
    version='0.0',
    url='http://github.com/sourcegraph/pydep',
    packages=['pydep'],
    scripts=['pydep-run.py'],
    author='Beyang Liu',
    description='A simple module that will print the dependencies of a python project'
    'Usage: python -m pydep <dir>',
    zip_safe=False,
    install_requires=[
        "pip==7.1.2",
    ],
)
