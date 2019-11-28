.. _how_to_add_post_scan_plugin:

Add A Post-Scan Plugin
======================

Built-In vs. Optional Installation
----------------------------------

Built-In
^^^^^^^^

Some post-scan plugins are installed when ScanCode itself is installed, e.g., the
:ref:`license_policy_plugin`, whose code is located here::

    https://github.com/nexB/scancode-toolkit/blob/develop/src/licensedcode/plugin_license_policy.py

These plugins do not require any additional installation steps and can be used as soon as ScanCode
is up and running.

Optional
^^^^^^^^

ScanCode is also designed to use post-scan plugins that must be installed separately from the
installation of ScanCode. The code for this sort of plugin is located here::

    https://github.com/nexB/scancode-toolkit/tree/develop/plugins/

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

- In the ``/scancode-toolkit/plugins/`` directory, add a folder with a relevant name, e.g.,
  ``scancode-hello``. This folder will hold all of your plugin code.

- Inside the ``/scancode-hello/`` folder you'll need to add a folder named ``src`` and 7 files.

1. ``/src/`` -- This folder will contain your primary Python code and is discussed in more detail
   in the following section.

The 7 Files are:

1. ``.gitignore`` -- See, e.g.,
   `/plugins/scancode-ignore-binaries/.gitignore <https://github.com/nexB/scancode-toolkit/blob/develop/plugins/scancode-ignore-binaries/.gitignore>`_

::

    /build/
    /dist/

2. ``apache-2.0.LICENSE`` -- See, e.g.,
   `/plugins/scancode-ignore-binaries/apache-2.0.LICENSE <https://github.com/nexB/scancode-toolkit/blob/develop/plugins/scancode-ignore-binaries/apache-2.0.LICENSE>`_

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
   `/plugins/scancode-ignore-binaries/NOTICE <https://github.com/nexB/scancode-toolkit/blob/develop/plugins/scancode-ignore-binaries/NOTICE>`__

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
        url='https://github.com/nexB/scancode-toolkit/plugins/scancode-categories',
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
            'Programming Language :: Python :: 2.7',
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

Notice at the top of the file
"""""""""""""""""""""""""""""

::

    #
    # Copyright (c) 2019 nexB Inc. and others. All rights reserved.
    # http://nexb.com and https://github.com/nexB/scancode-toolkit/
    # The ScanCode software is licensed under the Apache License version 2.0.
    # Data generated with ScanCode require an acknowledgment.
    # ScanCode is a trademark of nexB Inc.
    #
    # You may not use this software except in compliance with the License.
    # You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
    # Unless required by applicable law or agreed to in writing, software distributed
    # under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
    # CONDITIONS OF ANY KIND, either express or implied. See the License for the
    # specific language governing permissions and limitations under the License.
    #
    # When you publish or redistribute any data created with ScanCode or any ScanCode
    # derivative work, you must accompany this data with the following acknowledgment:
    #
    #  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
    #  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
    #  ScanCode should be considered or used as legal advice. Consult an Attorney
    #  for any legal advice.
    #  ScanCode is a free software code scanning tool from nexB Inc. and others.
    #  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

Imports
"""""""

::

    from __future__ import absolute_import
    from __future__ import division
    from __future__ import print_function
    from __future__ import unicode_literals

    from plugincode.post_scan import PostScanPlugin
    from plugincode.post_scan import post_scan_impl
    from scancode import CommandLineOption
    from scancode import POST_SCAN_GROUP

Create a ``PostScanPlugin`` class
"""""""""""""""""""""""""""""""""

The ``PostScanPlugin`` class (see L40-L45
`code <https://github.com/nexB/scancode-toolkit/blob/develop/src/plugincode/post_scan.py>`__)
inherits from the ``CodebasePlugin`` class (see L139-L150
`code <https://github.com/nexB/scancode-toolkit/blob/794d7acf78480823084def703b5d61ade12efdf2/src/plugincode/__init__.py>`_ ),
which inherits from the ``BasePlugin`` class (see L38-L136
`code <https://github.com/nexB/scancode-toolkit/blob/794d7acf78480823084def703b5d61ade12efdf2/src/plugincode/__init__.py>`__ ).

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

            print('\nHello ScanCode!!\n')

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
`/scancode-toolkit/src/licensedcode/plugin_license_policy.py <https://github.com/nexB/scancode-toolkit/blob/develop/src/licensedcode/plugin_license_policy.py>`_
and illustrates how a plugin can be used to analyze the results of a ScanCode scan using external
data files and add the results of that analysis as a new field in the ScanCode JSON output file.
