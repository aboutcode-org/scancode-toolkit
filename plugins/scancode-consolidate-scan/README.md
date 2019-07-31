A ScanCode post-scan plugin to return consolidated components and consolidated
packages for different types of codebase summarization.

A consolidated component is a group of Resources that have the same origin.
Currently, consolidated components are created by grouping Resources that have
the same license expression and copyright holders and the files that contain
this license expression and copyright holders combination make up 75% or more of
the files in the directory where they are found.

A consolidated package is a detected package in the scanned codebase that has
been enhanced with data about other licenses and holders found within it.

If a Resource is part of a consolidated component or consolidated package, then
the identifier of the consolidated component or consolidated package it is part
of is in the Resource's `consolidated_to` field.
