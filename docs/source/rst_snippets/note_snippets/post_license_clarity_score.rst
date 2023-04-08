.. note::

    When the ``--license-clarity-score`` option is used, the output is
    added as the following attributes:

    - declared_license_expression
    - license_clarity_score (with the score and other flags as sub-attributes)

    in the top-level ``summary`` attribute, but the ``--summary`` CLI option
    is not required for this. Using the ``--summary`` CLI option also populates
    the same top-level ``summary`` attribute with the license clarity score.
