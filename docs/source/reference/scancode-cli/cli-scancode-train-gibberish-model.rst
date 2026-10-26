.. _cli-scancode-train-gibberish-model:

ScanCode train gibberish model
==============================

ScanCode uses a 2-character Markov chain to perform gibberish detection on text.
At a high level, it detects gibberish strings by seeing if a sequence of letters
is part or a whole word, two letters at a time. It does this by checking how
likely it is to go from one letter to another. The probabilities of going from
one letter to another are determined by a model that has been trained on a large
set of valid text, where it counts each transition between letters and computes
a probability based off of that. These probabilities and thresholds are stored
in a model that is saved to a Python pickle.

The training corpus for the gibberish detector can be found in
``src/textcode/data/gibberish/``.

``big.txt`` contains the main source of valid words that the gibberish detector
model is trained on.

``good.txt`` and ``bad.txt`` are used to determine the average threshold, where
any letter transition whose average transition probability falls below this
threshold is classified as gibberish.


Usage: ``scancode-train-gibberish-model [OPTIONS]``

Quick Reference
---------------

  --big FILE   Text file containing main training corpus for the gibberish
               detector
  --good FILE  Text file containing text considered to be not gibberish (good)
  --bad FILE   Text file containing text considered to be gibberish (bad)
  -h, --help   Show this message and exit.

----

.. _cli-scancode-train-gibberish-model-big-option:

``--big`` option
^^^^^^^^^^^^^^^^

The ``--big`` option allows the user to use a different text file to train the
gibberish detector model.

.. _cli-scancode-train-gibberish-model-good-option:

``--good`` option
^^^^^^^^^^^^^^^^^

The ``--good`` option allows the user to use a different text file containing
strings considered to be valid copyrights. This option is used to adjust the
average transition probability threshold that determines whether or not a string
is gibberish.

.. _cli-scancode-train-gibberish-model-bad-option:

``--bad`` option
^^^^^^^^^^^^^^^^

The ``--bad`` option allows the user to use a different text file containing
strings considered to be invalid copyrights. This option is used to adjust the
average transition probability threshold that determines whether or not a string
is gibberish.
