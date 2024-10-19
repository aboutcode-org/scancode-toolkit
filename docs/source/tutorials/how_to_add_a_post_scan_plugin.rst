.. _how_to_add_post_scan_plugin:

Add A Post-Scan Plugin
======================

Scan plugins in ``scancode-toolkit``
------------------------------------

A lot of scancode features are built-in plugins which are present with scancode-toolkit source code
and are usually enabled via the different scancode-toolkit CLI options and are grouped by the types
of plugins.

Here are the major types of plugins:

1. Pre-scan plugins (`scancode_pre_scan` in entry points)

   These plugins are run before the main scanning steps and are usually
   filtering of input files, or file classification steps, on whose results
   the main scan plugins depend on. The base plugin class to be extended is ``PreScanPlugin`` at
   `/src/plugincode/pre_scan.py <https://github.com/nexB/plugincode/blob/main/src/plugincode/pre_scan.py>`_.

2. Scan plugins (`scancode_scan` in entry points)

   The are the scancode plugins which does the file scanning for useful
   information like license, copyrights, packages and others. These are
   run on multiprocessing for speed as they are done on a per-file basis,
   but there can also be post-processing steps on these which are run afterwards
   and have access to all the per-file scan results. The base plugin class to be extended is
   ``ScanPlugin`` at `/src/plugincode/scan.py <https://github.com/nexB/plugincode/blob/main/src/plugincode/scan.py>`_.

3. Post-scan plugins (`scancode_post_scan` in entry points)

   These are mainly data processing, summerizing and reporting plugins which
   depend on all the results for the scan plugins. These add new codebase level
   or file-level attributes, and even removes/modifies data as required
   for consolidation or summarization. The base plugin class to be extended is ``PostScanPlugin``
   at `/src/plugincode/post_scan.py <https://github.com/nexB/plugincode/blob/main/src/plugincode/post_scan.py>`_.

4. Output plugins (`scancode_output` in entry points)

   Supported output options in scancode-toolkit are all plugins and
   these can also be multiple output options selected. These convert, process
   and writes the data in the specific file format as the output of the scanning
   procedures. The base plugin class to be extended is ``OutputPlugin`` at
   `/src/plugincode/output.py <https://github.com/nexB/plugincode/blob/main/src/plugincode/output.py>`_.

5. Output Filter Plugins (`scancode_output_filter` in entry points)

   There are also output filter plugins which apply filters to the outputs
   and is modified. These filters can be based on whether resources had any
   detections, ignorables present in licenses and others.
   The base plugin class to be extended is ``OutputFilterPlugin`` at
   `/src/plugincode/output_filter.py <https://github.com/nexB/plugincode/blob/main/src/plugincode/output_filter.py>`_.

6. Location Provider Plugins

   These plugins provide pre-built binary libraries and utilities and their locations which
   are packaged to be used in scancode-toolkit. The base plugin class to be extended is
   ``LocationProviderPlugin`` at `/src/plugincode/location_provider.py <https://github.com/nexB/plugincode/blob/main/src/plugincode/location_provider.py>`_.


Built-In vs. Optional Installation
----------------------------------

Built-In
^^^^^^^^

Some post-scan plugins are installed when ScanCode itself is installed, and they are specified at
``[options.entry_points]`` in the `setup.cfg <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/setup.cfg>`_ file.
For example, the :ref:`license_policy_plugin` is a built-in plugin, whose code is located here::

    https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/licensedcode/plugin_license_policy.py

These plugins do not require any additional installation steps and can be used as soon as ScanCode
is up and running.

Optional
^^^^^^^^

ScanCode is also designed to use post-scan plugins that must be installed separately from the
installation of ScanCode. The code for this sort of plugin is located here::

    https://github.com/aboutcode-org/scancode-plugins

This wiki page will focus on optional post-scan plugins.

Example Post-Scan Plugin: Hello ScanCode
----------------------------------------

To illustrate the creation of a simple post-scan plugin, we'll create a hypothetical plugin named
``Hello ScanCode``, which will print ``Hello ScanCode!`` in your terminal after you've run a scan.
Your command will look like something like this::

    scancode -i -n 2 <path to target codebase> --hello --json <path to JSON output file>

We'll start by creating three folders:

1. Top-level folder -- ``/scancode-hello/``
2. 2nd-level folder -- ``/src/``
3. 3rd-level folder -- ``/hello_scancode/``

1. Top-level folder -- ``/scancode-hello/``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

- In the ``scancode-plugins`` repository, in the ``misc`` directory, add a folder with
  a relevant name, e.g., ``scancode-hello``. This folder will hold all of your plugin code.

- Inside the ``/scancode-hello/`` folder you'll need to add a folder named ``src`` and 7 files.
  ``/src/`` -- This folder will contain your primary Python code and is discussed in more detail
  in the following section.

The 7 Files are:

1. ``.gitignore`` -- See, e.g.,
   `/scancode-ignore-binaries/.gitignore <https://github.com/aboutcode-org/scancode-plugins/blob/main/misc/scancode-ignore-binaries/.gitignore>`_

::

    /build/
    /dist/

2. ``apache-2.0.LICENSE`` -- See, e.g.,
   `/scancode-ignore-binaries/apache-2.0.LICENSE <https://github.com/aboutcode-org/scancode-plugins/blob/main/misc/scancode-ignore-binaries/apache-2.0.LICENSE>`_

3. ``MANIFEST.in``

::

    graft src

    include setup.py
    include setup.cfg
    include .gitignore
    include README.md
    include MANIFEST.in
    include NOTICE
    include apache-2.0.LICENSE

    global-exclude *.py[co] __pycache__ *.*~

4. ``NOTICE`` -- See, e.g.,
   `/scancode-ignore-binaries/NOTICE <https://github.com/aboutcode-org/scancode-plugins/blob/main/misc/scancode-ignore-binaries/NOTICE>`__

5. ``README.md``

6. ``setup.cfg``

::

    [metadata]
    license_file = NOTICE

    [bdist_wheel]
    universal = 1

    [aliases]
    release = clean --all  bdist_wheel

7. ``setup.py`` -- This is an example of what our ``setup.py`` file would look like:

::

    #!/usr/bin/env python
    # -*- encoding: utf-8 -*-

    from __future__ import absolute_import
    from __future__ import print_function

    from glob import glob
    from os.path import basename
    from os.path import join
    from os.path import splitext

    from setuptools import find_packages
    from setuptools import setup


    desc = '''A ScanCode post-scan plugin to to illustrate the creation of a simple post-scan plugin.'''

    setup(
        name='scancode-hello',
        version='1.0.0',
        license='Apache-2.0 with ScanCode acknowledgment',
        description=desc,
        long_description=desc,
        author='nexB',
        author_email='info@aboutcode.org',
        url='https://github.com/aboutcode-org/scancode-plugins/blob/main/misc/scancode-hello/',
        packages=find_packages('src'),
        package_dir={'': 'src'},
        py_modules=[splitext(basename(path))[0] for path in glob('src/*.py')],
        include_package_data=True,
        zip_safe=False,
        classifiers=[
            # complete classifier list: http://pypi.python.org/pypi?%3Aaction=list_classifiers
            'Development Status :: 4 - Beta',
            'Intended Audience :: Developers',
            'License :: OSI Approved :: Apache Software License',
            'Programming Language :: Python',
            'Programming Language :: Python :: 3',
            'Topic :: Utilities',
        ],
        keywords=[
            'scancode', 'plugin', 'post-scan'
        ],
        install_requires=[
            'scancode-toolkit',
        ],
        entry_points={
            'scancode_post_scan': [
                'hello = hello_scancode.hello_scancode:SayHello',
            ],
        }
    )

2. 2nd-level folder -- ``/src/``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Add an ``__init__.py`` file inside the ``src`` folder. This file can be empty, and is used to
   indicate that the folder should be treated as a Python package directory.

#. Add a folder that will contain our primary code -- we'll name the folder ``hello_scancode``.
   If you look at the example of the ``setup.py`` file above, you'll see this line in the
   ``entry_points`` section:

::

    'hello = hello_scancode.hello_scancode:SayHello',

- ``hello`` refers to the name of the command flag.
- The first ``hello_scancode`` is the name of the folder we just created.
- The second ``hello_scancode`` is the name of the ``.py`` file containing our code (discussed in
  the next section).
- ``SayHello`` is the name of the ``PostScanPlugin`` class we create in that file (see sample
  code below).

3. 3rd-level folder -- ``/hello_scancode/``
^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^^

#. Add an ``__init__.py`` file inside the ``hello_scancode`` folder. As noted above, this file can
   be empty.

#. Add a ``hello_scancode.py`` file.

Imports
"""""""

::


    from plugincode.post_scan import PostScanPlugin
    from plugincode.post_scan import post_scan_impl
    from scancode import CommandLineOption
    from scancode import POST_SCAN_GROUP

Create a ``PostScanPlugin`` class
"""""""""""""""""""""""""""""""""

The ``PostScanPlugin`` class
`PostScanPlugin code <https://github.com/nexB/plugincode/blob/main/src/plugincode/post_scan.py>`_)
inherits from the ``CodebasePlugin`` class (see
`CodebasePlugin code <https://github.com/nexB/plugincode/blob/main/src/plugincode/__init__.py>`_),
which inherits from the ``BasePlugin`` class (see
`BasePlugin code <https://github.com/nexB/plugincode/blob/main/src/plugincode/__init__.py>`_).

::

    @post_scan_impl
    class SayHello(PostScanPlugin):
        """
        Illustrate a simple "Hello World" post-scan plugin.
        """

        options = [
            CommandLineOption(('--hello',),
            is_flag=True, default=False,
            help='Generate a simple "Hello ScanCode" greeting in the terminal.',
            help_group=POST_SCAN_GROUP)
        ]

        def is_enabled(self, hello, **kwargs):
            return hello

        def process_codebase(self, codebase, hello, **kwargs):
            """
            Say hello.
            """
            if not self.is_enabled(hello):
                return

            print('Hello ScanCode!!')


Load the plugin
---------------

- To load and use the plugin in the normal course, navigate to the plugin's root folder (in this
  example: ``/plugins/scancode-hello/``) and run ``pip install .`` (don't forget the final ``.``).

- If you're developing and want to test your work, save your edits and run ``pip install -e .``
  from the same folder.


More-complex examples
---------------------

This Hello ScanCode example is quite simple. For examples of more-complex structures and
functionalities you can take a look at the other post-scan plugins for guidance and ideas.

One good example is the License Policy post-scan plugin. This plugin is installed when ScanCode
is installed and consequently is not located in the ``/plugins/`` directory used for
manually-installed post-scan plugins. The code for the License Policy plugin can be found at
`/scancode-toolkit/src/licensedcode/plugin_license_policy.py
<https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/licensedcode/plugin_license_policy.py>`_
and illustrates how a plugin can be used to analyze the results of a ScanCode scan using external
data files and add the results of that analysis as a new field in the ScanCode JSON output file.
