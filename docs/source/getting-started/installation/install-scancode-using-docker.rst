.. _install-scancode-using-docker:

Install ScanCode using docker
=============================

You can install ScanCode by building a Docker image from the included Dockerfile.
The prerequisite is a working `docker installation <https://docs.docker.com/engine/install/>`_.


Download ScanCode sources
-------------------------

Run the following once you have `Git <https://git-scm.com/>`_ installed

.. code-block:: shell

    git clone https://github.com/aboutcode-org/scancode-toolkit.git


Build the docker image
----------------------

Run the ``docker build`` source code checkout directory.

.. code-block:: shell

    cd scancode-toolkit
    docker build --tag scancode-toolkit --tag scancode-toolkit:$(git describe --tags) .

.. note::

  As ``$(git describe --tags)`` is a Unix-style command. If you are on
  windows, please run the ``git describe --tags`` separately to get the
  output, then manually insert that value into your Docker command.
  For instance, ::

    C:\scancode-toolkit>git describe --tags
    v32.5.0
    C:\scancode-toolkit>docker build --tag scancode-toolkit --tag scancode-toolkit:v32.5.0 .

Verify installation
-------------------

To verify that ScanCode has been installed correctly,
it is recommended to run the help command.


.. code-block:: shell

    docker run scancode-toolkit --help


Run using docker
----------------

The docker image will forward all arguments it receives directly to the ``scancode`` command.

.. code-block:: shell

    docker run scancode-toolkit --help

Mount current working directory as "/project" and run a scan on a file name
apache-2.0.LICENSE directory. The JSON results will be in scan-result.json

.. code-block:: shell

    docker run -v $PWD/:/project scancode-toolkit -clipeu --json-pp /project/scan-result.json /project/apache-2.0.LICENSE

This will mount your current working from the host into ``/project`` in the container
and then scan the contents. The output ``result.json`` will be written back to your
current working directory on the host.

Note that the parameters *before* ``scancode-toolkit`` are used for docker,
those after will be forwarded to scancode.
