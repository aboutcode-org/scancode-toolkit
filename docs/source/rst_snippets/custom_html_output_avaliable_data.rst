Custom HTML Output Available Data
---------------------------------

When using the ``--custom-template`` option, a files dictionary is passed
to Jinja2 for output generation.
This dictionary contains three keys: ``license_copyright``, ``infos``, and
``package_data`` — each of which is also a dictionary.

If you want to access these data, you will need to do something like the following:

::

   {% if files.license_copyright %}
   ...
   {% if files.infos %}
   ...
   {% if files.package_data %}


``license_copyright`` is a dictionary where each key is a file path, and
each value is a list of dictionaries. Each dictionary in the list contains
four keys: ``start``, ``end``, ``what``, and ``value``.


 * ``start`` is the start line from the detection
 * ``end`` is the end line from the detection
 * ``what`` can be either "copyright" or "license"
 * ``value`` is the value of the detected copyright or licnese expression


``infos`` is a dictionary where each key is a file path, and
each value is either a list of dictionaries or a string.

The following is a list of dictionary keys from ``infos`` whose values are strings:

::

  type
  name
  extension
  date
  size
  sha1
  md5
  file_count
  mime_type
  file_type
  programming_language
  is_binary
  is_text
  is_archive
  is_media
  is_source
  is_script


The following is a list of dictionary keys from ``infos`` whose values are lists of dictionaries:

::

  holders - It is a list of dictionaries, each containing the keys: ``holder``, ``start_line``, and ``end_line``
  authors - It is a list of dictionaries, each containing the keys: ``author``, ``start_line``, and ``end_line``
  emails - It is a list of dictionaries, each containing the keys: ``email``, ``start_line``, and ``end_line``
  urls - It is a list of dictionaries, each containing the keys: ``url``, ``start_line``, and ``end_line``


``package_data`` is a dictionary where each key is a file path, and
each value is a list of dictionaries. Each dictionary in the list contains
three keys: ``type``, ``packaging``, and ``primary_language``.


Additionally, a ``license_reference`` list is also provided for output generation.
It is a list of dicionaries with the following keys and value structure:

::

  key - string
  short_name - string
  category - string
  owner - string
  scancode_url - string
  licensedb_url - string
  homepage_url - string
  text_urls - list
  spdx_license_key - string
  spdx_url - string

