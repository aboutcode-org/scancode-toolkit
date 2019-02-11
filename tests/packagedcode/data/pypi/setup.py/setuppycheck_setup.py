from setuptools import setup


def get_version(fname='setuppycheck.py'):
    with open(fname) as f:
        for line in f:
            if line.startswith('__version__'):
                return eval(line.split('=')[-1])


def get_long_description():
    descr = []
    for fname in ('README.rst',):
        with open(fname) as f:
            descr.append(f.read())
    return '\n\n'.join(descr)


setup(
    name='setuppycheck',
    description='Checks for questionable practices in setup.py files.',
    long_description=get_long_description(),
    keywords='setup.py pin dependencies',
    version=get_version(),
    author='Marc Abramowitz',
    author_email='msabramo@gmail.com',
    install_requires=['mock'],
    entry_points="""\
        [console_scripts]
        setuppycheck = setuppycheck:setuppycheck
    """,
    url='https://github.com/msabramo/setuppycheck',
    license='MIT',
    py_modules=['setuppycheck'],
    zip_safe=False,
)
