Print to ``stdout`` / terminal
------------------------------

If you want to format the output in JSON and print it at stdout, you can replace the JSON filename
with a "-", like ``--compact-json -`` instead of ``--compact-json output.json``.

The following command will output the scan results in JSON format to ``stdout`` (in the terminal)::

    ./scancode -clpieu --compact-json - samples/
