Custom Output Format
--------------------

While the three built-in output formats are convenient for a verity of use-cases, one may wish to
create their own output template, using the following arguments::

    ``--custom-output FILE --custom-template TEMP_FILE``

ScanCode makes this very easy, as it uses the popular Jinja2 template engine. Simply pass the path
to the custom template to the ``--custom-template`` argument, or drop it in a folder to
``src/scancode/templates`` directory.

For example, if I wanted a simple CLI output I would create a ``template2.html`` with the
particular data I wish to see. In this case, I am only interested in the license and copyright
data for this particular scan.

::

   ## template.txt:
   [
       {% if files.license_copyright %}
           {% for location, data in files.license_copyright.items() %}
               {% for row in data %}
     location:"{{ location }}",
     {% if row.what == 'copyright' %}copyright:"{{ row.value|escape }}",{% endif %}
                {% endfor %}
            {% endfor %}
       {% endif %}
   ]

   .. note::

       File name and extension does not matter for the template file.

Now I can run ScanCode using my newly created template:

::

   $ scancode -clpeui --custom-output output.txt --custom-template template.txt samples
   Scanning files...
     [####################################]  46
   Scanning done.

Now the results are saved in ``output.txt`` and we can easily view them with ``head output.txt``:

::

   [
     location:"samples/JGroups/LICENSE",
     copyright:"Copyright (c) 1991, 1999 Free Software Foundation, Inc.",

     location:"samples/JGroups/LICENSE",
     copyright:"copyrighted by the Free Software Foundation",
   ]

For a more elaborate template, refer this `default template <https://github.com/aboutcode-org/scancode-toolkit/blob/develop/src/formattedcode/templates/html/template.html>`_
given with ScanCode, to generate HTML output with the ``--html`` output format option.

Documentation on `Jinja templates <https://jinja.palletsprojects.com/en/2.10.x/>`_.
