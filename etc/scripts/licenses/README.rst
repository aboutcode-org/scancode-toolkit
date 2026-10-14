A set of scripts to update and generate licenses and license rules.


Model-assisted required phrases
===============================

``add_model_required_phrases.py`` delegates to the
`scancode-required-phrases <https://github.com/aboutcode-org/scancode-required-phrases>`_
package. Install or update that package with its ``inference`` extra in the
same environment before running the script.

.. code-block:: console

    python etc/scripts/licenses/add_model_required_phrases.py --help
