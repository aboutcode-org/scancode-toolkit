A ScanCode post-scan plugin to return filesets for different types of codebase summarization.

A fileset is a group of Resources that have the same origin. Filesets are currently grouped by
`package`, whether or not a Resource is in a detected package, or by `license-holder`, where
Resources are grouped by whether or not they have the same license expression and holder and if
they are found in 75% or more of files in a directory.
