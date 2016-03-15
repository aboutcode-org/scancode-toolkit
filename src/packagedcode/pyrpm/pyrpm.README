=====
PyRPM
=====

:author: Mário Morgado
:license: BSD

PyRPM is a pure python module to extract information from a RPM package.

Usage
-----

        >>> from pyrpm.rpm import RPM
        >>> frpm pyrpm import rpmdefs
        >>> rpm = RPM(file('package-1.0-r1.i586.rpm')
        >>> rpm.binary # this means that the package is a rpm and not a src.rpm
        True
        >>> rpm.name()
        'package'
        >>> rpm.package()
        'package-1.0'
        >>> rpm[rpmdefs.RPMTAG_DESCRIPTION]
        'package description'
        >>> rpm[rpmdefs.RPMTAG_ARCH]
        'i586'

