.. _facets:

Facets
======

A `facet <https://docs.clearlydefined.io/docs/resources/defined#facets>`_ is essentially
a file purpose classification label.
It is defined by `ClearlyDefined <https://clearlydefined.io/about>`_ as:

A facet of a component is a subset of the files related to the component. It's really just a
grouping that helps us understand the shape of the project. Each facet is described by a set of
glob expressions, essentially wildcard patterns that are matched against file names.

Each facet definition can have zero or more glob expressions. A file can be captured by more
than one facet. Any file found but not captured by a defined facet is automatically assigned to
the core facet.

- ``core``
    The files that go into making the release of the component. Note that the core
    facet is not explicitly defined. Rather, it is made up of whatever is not in any other facet.
    So, by default, all files are in the core facet unless otherwise specified.
- ``data``
    The files included in any data distribution of the component.
- ``dev``
    Files primarily used at development time (e.g., build utilities) and not
    distributed with the component
- ``docs``
    Documentation files. Docs may be included with the executable component or
    separately or not at all.
- ``examples``
    Like docs, examples may be included in the main component release or separately.
- ``tests``
    Test files may include code, data and other artifacts.

Related ScanCode CLI options
----------------------------
- :ref:`cli-facet-option`
- :ref:`cli-tallies-by-facet-option`
