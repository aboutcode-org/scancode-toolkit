Google Summer of Code 2017 - Final report
=========================================

**Project: Plugin architecture for ScanCode**
---------------------------------------------

Yash D. Saraf  `yashdsaraf@gmail.com <mailto:yashdsaraf@gmail.com>`_

----

This project’s purpose was to create a decoupled plugin architecture for
`ScanCode <https://github.com/nexB/scancode-toolkit>`_ such that it can handle plugins at different
stages of a scan and can be coupled at runtime. These stages were,

1. `Format <https://github.com/nexB/scancode-toolkit/issues/639>`_ :
---------------------------------------------------------------------

In this stage, the plugins are supposed to run **after** the scanning is done and ``post-scan``
plugins are called. These plugins could be used for:


- **converting the scanned output to the given format (say csv, json, etc.)**

**HOWTO**

Here, a plugin needs to add an entry in the ``scancode_output_writers`` entry point in the following
format : ``'<format> = <module>:<function>'``.


- ``<format>``  is the format name which will be used as the command line option name
  (e.g ``csv`` or ``json`` ).
- ``<module>`` is a python module which implements the ``output`` hook specification.
- ``<function>`` is the function to which the scan output will be passed if this plugin is called.

The ``<format>`` name will be automatically added to the ``--format`` command line option and
(if called) the scanned data will be passed to the plugin.

2. `Post-scan <https://github.com/nexB/scancode-toolkit/issues/704>`_ :
------------------------------------------------------------------------

In this stage, the plugins are supposed to run **after** the scanning is done. Some uses for these
plugins were:


- **summarization of scan outputs**

    e.g A post-scan plugin for marking ``is_source`` to true for directories with ~90% of source
    files.

- **simplification of scan outputs**

    e.g The ``--only-findings`` option to return files or directories with findings for the
    requested scans. Files and directories without findings are omitted (not considering basic file
    information as findings)).

This option already existed, I just ported it to a post-scan plugin.

**HOWTO**

Here, a plugin needs to add an entry in the ``scancode_post_scan`` entry point in the following
format ``'<name> = <module>:<function>'``

- ``<name>``  is the command line option name (e.g **only-findings**).
- ``<module>`` is a python module which implements the ``post_scan`` hook specification.
- ``<function>`` is the function to which the scanned files will be passed if this plugin is called

The command line option for this plugin will be automatically created using the ``<function>`` 's
doctring as its help text and (if called) the scanned files will be passed to the plugin.

3. `Pre-scan <https://github.com/nexB/scancode-toolkit/issues/719>`_ :
-----------------------------------------------------------------------

In this stage, the plugins are supposed to run **before** the scan starts. So the potential uses
for these types of plugins were to:

- **ignore files based on a given pattern (glob)**
- **ignore files based on their info i.e size, type etc.**
- **extract archives before scanning**

**HOWTO**

Here, a plugin needs to add an entry in the ``scancode_pre_scan`` entry point in the following
format : ``'<name> = <module>:<class>'``


* ``<name>``  is the command line option name (e.g **ignore** ).
* ``<module>`` is a python module which implements the ``pre_scan`` hook specification.
* ``<class>`` is the class which is instantiated and its appropriate method is invoked if this
  plugin is called. This needs to extend the ``plugincode.pre_scan.PreScanPlugin`` class.

The command line option for this plugin will be automatically created using the ``<class>`` 's
doctring as its help text. Since there isn't a single spot where ``pre-scan`` plugins can be
plugged in, more methods to ``PreScanPlugin`` class can be added which can represent different
hooks, say to add or delete a scan there might be a method called ``process_scan``.

If a plugin's option is passed by the user, then the ``<class>`` is instantiated with the user
input and its appropriate aforementioned methods are called.

4. Scan (proper):
-----------------

In this stage, the plugins are supposed to run **before** the scan starts and **after** the
``pre-scan`` plugins are called. These plugins would have been used for

- **adding or deleting scans**
- **adding dependency scans (whose data could be used in other scans)**

No development has been done for this stage, but it will be quite similar to ``pre-scan``.

5. Other work:
--------------

`Group cli options in cli help <https://github.com/nexB/scancode-toolkit/issues/709>`_

Here, the goal was to add command line options to pre-defined groups such that they are displayed
in their respective groups when ``scancode -h`` or ``scancode --help`` is called. This helped to
better visually represent the command line options and determine more easily what context they
belong to.

`Add a Resource class to hold all scanned info <https://github.com/nexB/scancode-toolkit/issues/738>`_
* ``Ongoing`` *

Here, the goal was to create a ``Resource`` class, such that it holds all the scanned data for a
resource (i.e a file or a directory). This class would go on to eventually encapsulate the caching
logic entirely. For now, it just holds the ``info`` and ``path`` of a resource.

6. What's left?
---------------

- Pre-scan plugin for archive extractions
- Scan (proper) plugins
- More complex post-scan plugins
- Support plugins written in languages other than python

**Additionally, all my commits can be found** `here <https://github.com/nexB/scancode-toolkit/commits/develop?author=yashdsaraf>`_.
