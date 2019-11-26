Print to ``stdout`` (Terminal)
------------------------------

If you want to format the output in JSON and print it at stdout, you can replace the JSON filename
with a "-", like ``--json-pp -`` instead of ``--json-pp output.json``.

The following command will output the scan results in JSON format to ``stdout`` (In the Terminal)::

    ./scancode -clpieu --json-pp - samples/
