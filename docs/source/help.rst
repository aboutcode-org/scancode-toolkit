Help
====

ScanCode Toolkit is part of the AboutCode family of open source projects.

AboutCode Projects
******************

- **[ScanCode Toolkit](https://github.com/nexB/scancode-toolkit)**: This is a set of code scanning tools to detect the origin and license of code and dependencies. ScanCode Toolkit uses a plug-in architecture to run a series of scan-related tools in one process flow. This is the most popular project and is used by hundreds of software teams. https://github.com/nexB/scancode-toolkit . The lead maintainer is @pombredanne

- **[Scancode Workbench](https://github.com/nexB/scancode-workbench)** (formerly AboutCode Manager) This is a desktop application (based on Electron) to review the results of a scan and document your conclusions about the origin and license of software components and packages. https://github.com/nexB/aboutcode-manager . The lead maintainer is @majurg

- **[AboutCode Toolkit](https://github.com/nexB/aboutcode-toolkit)**: This is a set of command line tools to document the provenance of your code and generate attribution notices.  AboutCode Toolkit uses small yaml files to document code provenance inside a codebase. https://github.com/nexB/aboutcode-toolkit . The lead maintainer is @chinyeungli

- **[TraceCode Toolkit](https://github.com/nexB/tracecode-toolkit)**: This is a set of tools to trace files from your deployment or distribution packages back to their origin in a development codebase or repository.  The primary tool uses strace https://github.com/strace/strace/ to trace system calls on Linux and construct a build graph from syscalls to show which files are used to build a binary. We are contributors to strace. Maintained by @pombredanne

- **[Conan](https://github.com/nexB/conan)**: "conan" stands for "CONtainer ANalysis" and is a tool to analyze the structure and provenance of software components in Docker images using static analysis. https://github.com/nexB/conan Maintained by @pombredanne

- **[license-expression](https://github.com/nexB/license-expression/)**: This is a library to parse, analyze, compare and normalize SPDX-like license expressions using a boolean logic expression engine. See https://spdx.org/spdx-specification-21-web-version#h.jxpfx0ykyb60 to understand what a license expression is. See https://github.com/nexB/license-expression for the code. The underlying boolean engine is at https://github.com/bastikr/boolean.py . Both are co-maintained by @pombredanne

- **ABCD aka AboutCode Data** is a simple set of conventions to define data structures that all the AboutCode tools can understand and use to exchange data. The specification lives in this repository. .ABOUT files and ScanCode tooklit data are examples of this approach. Other projects such as https://libraries.io and [OSS Review Toolkit](https://github.com/heremaps/oss-review-toolkit) also use these conventions.

- **[DeltaCode](https://github.com/nexB/deltacode)** is a command line tool to compare scans and determine if and where there are material differences that affect licensing. The lead maintainer is @majurg

- **[VulnerableCode](https://github.com/nexB/vulnerablecode)**: an emerging server-side application to collect and track known package vulnerabilities.

