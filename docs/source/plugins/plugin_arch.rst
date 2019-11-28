.. _plugin_arch:

Plugin Architecture
===================

Notes: this is the initial design for ScanCode plugins. The actual architecture evolved and is
different.

Abstract:
---------

This project’s purpose is to create a decoupled plugin architecture for scancode such that it can
handle plugins at different stages of a scan and can be coupled at runtime. These stages would be

* Pre - scan: Before starting the scan

E.g Plugins to handle extraction of different archive types or instructions on how to handle
certain types of files.

* Scan proper: During the scan

E.g Plugins to add more options for the scan, maybe to ignore certain files or add some
command line arguments, create new scans (alternative or as a dependency for further scanning) etc.

* Post - scan: After the scan

E.g Plugins for output deduction, formatting or converting output to other formats
(such as json, spdx, csv, xml, etc.)

Upside of building a pluggable system would be to allow easier additions and rare modifications
to code, without having to really fiddle around with core codebase. This will also provide a level
of abstraction between the plugins and scancode so that any erroneous plugin would not affect the
functioning of scancode as a whole.

Description:
------------

This project aims at making scancode a “pluggable” system, where new functionalities can be added
to scancode at runtime as “plugins”. These plugins can be hooked into scancode using some
predefined hooks. I would consider pluggy as the way to go for a plugin management system.

Why pluggy?
^^^^^^^^^^^

Pluggy is well documented and maintained regularly, and has proved its worth in projects such as
py.test. Pluggy relies on hook specifications and hook implementations (callbacks) instead of the
conventional subclassing approach which may encourage tight-coupling in the overlying framework.
Basically a hook specification contains method signatures (no code), these are defined by the
application. A hook implementation contains definitions for methods declared in the corresponding
hook specification implemented by a plugin.

As mentioned in the abstract, the plugin architecture will have 3 hook specifications (can be
increased if required)

1. Pre - scan hook
^^^^^^^^^^^^^^^^^^

- **Structure** -

::

   prescan_hookspec = HookspecMarker('prescan')

   @prescan_hookspec
   def extract_archive(args):

Here the path of the archive to be extracted will be passed as an argument to the extract_archive
function which will be called before scan, at the time of extraction. This will process the archive
type and extract the contents accordingly. This functionality can be further extended by calling
this function if any archive is found inside the scanning tree.

2. Scan proper hook
^^^^^^^^^^^^^^^^^^^


- **Structure**

::

   scanproper_hookspec = HookspecMarker('scanproper')

   @scanproper_hookspec
   def add_cmdline_option(args):

This function will be called before starting the scan, without any arguments, it will return a dict
containing the click extension details and possibly some help text. If this option is called by the
user then the call will be rerouted to the callback defined by the click extension. For instance
say a plugin implements functionality to add regex as a valid ignore pattern, then this function
will return a dict as::

   {
       'name': '--ignore-regex',
       'options' : {
           'default': None,
           'multiple': True,
           'metavar': <pattern>
       },
       'help': 'Ignore files matching regex <pattern>'
       'call_after': 'is_ignored'
   }

According to the above dict, if the option --ignore-regex is supplied, this function will be called
after the is_ignored function and the data returned by the is_ignored function will be supplied to
this function as its argument(s). So if the program flow was::

   scancode() ⇔ scan() ⇔ resource_paths() ⇔ is_ignored()


It will now be edited to

::

   scancode() ⇔ scan() ⇔ resource_paths() ⇔ is_ignored() ⇔ add_cmdline_option()


Options such as **call_after, call_before, call_first, call_last** can be defined to determine
when the function is to be executed.

::

   @scanproper_hookspec
   def dependency_scan(args):

This function will be called before starting the scan without any arguments, it will return a
list of file types or attributes which if encountered in the scanned tree, will call this function
with the path to the file as an argument. This function can do some extra processing on those files
and return the data to be processed as a dependency for the normal scanning process.
E.g. It can return a list such as::

   [ 'debian/copyright' ]

Whenever a file matches this pattern, this function will be called and the data returned will be
supplied to the main scancode function.

3. Post - scan hook
^^^^^^^^^^^^^^^^^^^


- **Structure** -

::

   postscan_hookspec = HookspecMarker('postscan')

   @postscan_hookspec
   def format_output(args):

This function will be called after a scan is finished. It will be supplied with path to the ABC
data generated from the scan, path to the root of the scanned code and a path where the output is
expected to be stored. The function will store the processed data in the output path supplied.
This can be used to convert output to other formats such as CSV, SPDX, JSON, etc.

::

   @postscan_hookspec
   def summarize_output(args):

This function will be called after a scan is finished. It will be supplied the data to be reported
to the user as well as a path to the root of the scanned node. The data returned can then be
reported to the user. This can be used to summarize output, maybe encapsulate the data to be
reported or omit similar file metadata or even classify files such as tests, code proper, licenses,
readme, configs, build scripts etc.


- **Identifying or configuring plugins**

For python plugins, pluggy supports loading modules from setuptools entrypoints,
E.g.

::

       entry_points = {
           'scancode_plugins': [
               'name_of_plugin = ignore_regex',
           ]
       }

This plugin can be loaded using the PluginManager class’s
load_setuptools_entrypoints('scancode_plugins') method which will return a list of loaded plugins.

For non python plugins, all such plugins will be stored in a common directory and each of these
plugins will have a manifest configuration in YAML format. This directory will be scanned at
startup for plugins. After parsing the config file of a plugin, the data will be supplied to the
plugin manager as if it were supplied using setuptools entrypoints.

In case of non python plugins, the plugin executables will be spawned in their own processes and
according to their config data, they will be passed arguments and would return data as necessary.
In addition to this, the desired hook function can be called from a non python plugin using certain
arguments, which again can be mapped in the config file.

Sample config file for a ignore_regex plugin calling scanproper hook would be::

   name: ignore_regex
   hook: scanproper
   hookfunctions:
     add_cmdline_option: '-aco'
     dependency_scan: '-dc'
   data:
     add_cmdline_option':
       - name: '--ignore-regex'
       - options:
           - default: None
           - multiple: True
           - metavar: <pattern>
       - help: 'Ignore files matching regex <pattern>'
       - call_after: 'is_ignored'

Existing solutions:
-------------------

An alternate solution to a “pluggable” system would be the more conventional approach of adding
functionalities directly to the core codebase, which removes the abstraction layer provided by
a plugin management and hook calling system.
