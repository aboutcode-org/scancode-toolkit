from setuptools import setup

# from mpld3
def get_version(f):
    """Get the version info from the mpld3 package without importing it"""
    import ast
    with open(f) as init_file:
        module = ast.parse(init_file.read())

    version = (ast.literal_eval(node.value) for node in ast.walk(module)
               if isinstance(node, ast.Assign)
               and node.targets[0].id == "__version__")
    try:
        return next(version)
    except StopIteration:
        raise ValueError("version could not be located")


setup(
    name='interlap',
    version=get_version('interlap.py'),
    py_modules=['interlap'],
    author='Brent S Pedersen',
    author_email='bpederse@gmail.com',
    url='http://brentp.github.io/interlap',
    description='interlap: fast, simple interval overlap testing',
    long_description = open('README.md').read(),
    license='MIT',
    classifiers=[
            "Development Status :: 4 - Beta",
            "License :: OSI Approved :: MIT License",
            "Intended Audience :: Science/Research",
            "Natural Language :: English",
            "Operating System :: Unix",
            "Operating System :: Microsoft :: Windows",
            "Operating System :: MacOS",


            "Programming Language :: Python :: 2",
            "Programming Language :: Python :: 3",
            "Programming Language :: Python :: Implementation :: PyPy",
            "Topic :: Scientific/Engineering :: Bio-Informatics"
    ]
)
