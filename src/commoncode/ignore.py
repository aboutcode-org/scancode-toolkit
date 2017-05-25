#
# Copyright (c) 2015 nexB Inc. and others. All rights reserved.
# http://nexb.com and https://github.com/nexB/scancode-toolkit/
# The ScanCode software is licensed under the Apache License version 2.0.
# Data generated with ScanCode require an acknowledgment.
# ScanCode is a trademark of nexB Inc.
#
# You may not use this software except in compliance with the License.
# You may obtain a copy of the License at: http://apache.org/licenses/LICENSE-2.0
# Unless required by applicable law or agreed to in writing, software distributed
# under the License is distributed on an "AS IS" BASIS, WITHOUT WARRANTIES OR
# CONDITIONS OF ANY KIND, either express or implied. See the License for the
# specific language governing permissions and limitations under the License.
#
# When you publish or redistribute any data created with ScanCode or any ScanCode
# derivative work, you must accompany this data with the following acknowledgment:
#
#  Generated with ScanCode and provided on an "AS IS" BASIS, WITHOUT WARRANTIES
#  OR CONDITIONS OF ANY KIND, either express or implied. No content created from
#  ScanCode should be considered or used as legal advice. Consult an Attorney
#  for any legal advice.
#  ScanCode is a free software code scanning tool from nexB Inc. and others.
#  Visit https://github.com/nexB/scancode-toolkit/ for support and download.

from __future__ import print_function, absolute_import, unicode_literals
from itertools import chain

from commoncode import fileset
from commoncode import filetype
from commoncode import fileutils

"""
Support for ignoring some file patterns such as .git or .svn directories, used
typically when walking file systems.
Also handle .ignore-like file and provide common default ignores.
"""


def is_ignored(location, ignores, unignores, skip_special=True):
    """
    Return a tuple of (pattern , message) if a file at location is ignored
    or False otherwise.
    `ignores` and `unignores` are mappings of patterns to a reason.
    """
    if skip_special and filetype.is_special(location):
        return True
    return fileset.match(location, includes=ignores, excludes=unignores)


def is_ignore_file(location):
    """
    Return True if the location is an ignore file.
    """
    return (filetype.is_file(location)
            and fileutils.file_name(location) == '.scancodeignore')


def get_ignores(location, include_defaults=True):
    """
    Return a ignores and unignores patterns mappings loaded from the
    file at `location`. Optionally include defaults patterns
    """
    ignores = {}
    unignores = {}
    if include_defaults:
        ignores.update(default_ignores)
    patterns = fileset.load(location)
    ign, uni = fileset.includes_excludes(patterns, location)
    ignores.update(ign)
    unignores.update(uni)
    return ignores, unignores

#
# Default ignores
#

ignores_MacOSX = {
    '.DS_Store': 'Default ignore: MacOSX artifact',
    '._.DS_Store': 'Default ignore: MacOSX artifact',
    '__MACOSX': 'Default ignore: MacOSX artifact',
    '.AppleDouble': 'Default ignore: MacOSX artifact',
    '.LSOverride': 'Default ignore: MacOSX artifact',
    '.DocumentRevisions-V100': 'Default ignore: MacOSX artifact',
    '.fseventsd': 'Default ignore: MacOSX artifact',
    '.Spotlight-V100': 'Default ignore: MacOSX artifact',
    '.VolumeIcon.icns': 'Default ignore: MacOSX artifact',

    '.journal': 'Default ignore: MacOSX DMG/HFS+ artifact',
    '.journal_info_block': 'Default ignore: MacOSX DMG/HFS+ artifact',
    '.Trashes': 'Default ignore: MacOSX DMG/HFS+ artifact',
    '\[HFS+ Private Data\]': 'Default ignore: MacOSX DMG/HFS+ artifact private data',
}

ignores_Windows = {
    'Thumbs.db': 'Default ignore: Windows artifact',
    'ehthumbs.db': 'Default ignore: Windows artifact',
    'Desktop.ini': 'Default ignore: Windows artifact',
    '$RECYCLE.BIN': 'Default ignore: Windows artifact',
    '*.lnk': 'Default ignore: Windows artifact',
    'System Volume Information': 'Default ignore: Windows FS artifact',
    'NTUSER.DAT*': 'Default ignore: Windows FS artifact',
}

ignores_Linux = {
    '.directory': 'Default ignore: KDE artifact',
    '.Trash-*': 'Default ignore: Linux/Gome/KDE artifact',
}

ignores_IDEs = {
    '*.el': 'Default ignore: EMACS Elisp artifact',
    '*.swp': 'Default ignore: VIM artifact',
    '.project': 'Default ignore: Eclipse IDE artifact',
    '.pydevproject': 'Default ignore: Eclipse IDE artifact',
    '.settings': 'Default ignore: Eclipse IDE artifact',
    '.eclipse': 'Default ignore: Eclipse IDE artifact',
    '.loadpath': 'Default ignore: Eclipse IDE artifact',
    '*.launch': 'Default ignore: Eclipse IDE artifact',
    '.cproject': 'Default ignore: Eclipse IDE artifact',
    '.cdtproject': 'Default ignore: Eclipse IDE artifact',
    '.classpath': 'Default ignore: Eclipse IDE artifact',
    '.buildpath': 'Default ignore: Eclipse IDE artifact',
    '.texlipse': 'Default ignore: Eclipse IDE artifact',

    '*.iml': 'Default ignore: JetBrains IDE artifact',
    '*.ipr': 'Default ignore: JetBrains IDE artifact',
    '*.iws': 'Default ignore: JetBrains IDE artifact',
    '.idea/': 'Default ignore: JetBrains IDE artifact',
    '.idea_modules/': 'Default ignore: JetBrains IDE artifact',

    '*.kdev4': 'Default ignore: Kdevelop artifact',
    '.kdev4/': 'Default ignore: Kdevelop artifact',

    '*.nib': 'Default ignore: Apple Xcode artifact',
    '*.plst': 'Default ignore: Apple Xcode plist artifact',
    '*.pbxuser': 'Default ignore: Apple Xcode artifact',
    '*.pbxproj': 'Default ignore: Apple Xcode artifact',
    'xcuserdata': 'Default ignore: Apple Xcode artifact',
    '*.xcuserstate': 'Default ignore: Apple Xcode artifact',

    '*.csproj': 'Default ignore: Microsoft VS project artifact',
    '*.unityproj': 'Default ignore: Microsoft VS project artifact',
    '*.sln': 'Default ignore: Microsoft VS project artifact',
    '*.sluo': 'Default ignore: Microsoft VS project artifact',
    '*.suo': 'Default ignore: Microsoft VS project artifact',
    '*.user': 'Default ignore: Microsoft VS project artifact',
    '*.sln.docstates': 'Default ignore: Microsoft VS project artifact',
    '*.dsw': 'Default ignore: Microsoft VS project artifact',

    '.editorconfig': 'Default ignore: Editor config artifact',

    ' Leiningen.gitignore': 'Default ignore: Leiningen artifact',
    '.architect': 'Default ignore: ExtJS artifact',
    '*.tmproj': 'Default ignore: Textmate artifact',
    '*.tmproject': 'Default ignore: Textmate artifact',
}

ignores_web = {
    '.htaccess': 'Default ignore: .htaccess file',
    'robots.txt': 'Default ignore: robots file',
    'humans.txt': 'Default ignore: robots file',
    'web.config': 'Default ignore: web config',
    '.htaccess.sample': 'Default ignore: .htaccess file',
}

ignores_Maven = {
    'pom.xml.tag': 'Default ignore: Maven artifact',
    'pom.xml.releaseBackup': 'Default ignore: Maven artifact',
    'pom.xml.versionsBackup': 'Default ignore: Maven artifact',
    'pom.xml.next': 'Default ignore: Maven artifact',
    'release.properties': 'Default ignore: Maven artifact',
    'dependency-reduced-pom.xml': 'Default ignore: Maven artifact',
    'buildNumber.properties': 'Default ignore: Maven artifact',
}

ignores_VCS = {
    '.bzr': 'Default ignore: Bazaar artifact',
    '.bzrignore' : 'Default ignore: Bazaar config artifact',

    '.git': 'Default ignore: Git artifact',
    '.gitignore' : 'Default ignore: Git config artifact',
    '.gitattributes': 'Default ignore: Git config artifact',

    '.hg': 'Default ignore: Mercurial artifact',
    '.hgignore' : 'Default ignore: Mercurial config artifact',

    '.repo': 'Default ignore: Multiple Git repository artifact',

    '.svn': 'Default ignore: SVN artifact',
    '.svnignore': 'Default ignore: SVN config artifact',

    '.tfignore': 'Default ignore: Microsft TFS config artifact',

    'vssver.scc': 'Default ignore: Visual Source Safe artifact',

    'CVS': 'Default ignore: CVS artifact',
    '.cvsignore': 'Default ignore: CVS config artifact',
    '*/RCS': 'Default ignore: CVS artifact',
    '*/SCCS': 'Default ignore: CVS artifact',

    '*/_MTN': 'Default ignore: Monotone artifact',
    '*/_darcs': 'Default ignore: Darcs artifact',
    '*/{arch}': 'Default ignore: GNU Arch artifact',
}

ignores_Medias = {
    'pspbrwse.jbf': 'Default ignore: Paintshop browse file',
    'Thumbs.db': 'Default ignore: Image thumbnails DB',
    'Thumbs.db:encryptable': 'Default ignore: Image thumbnails DB',
    'thumbs/': 'Default ignore: Image thumbnails DB',
    '_thumbs/': 'Default ignore: Image thumbnails DB',
}

ignores_Build_scripts = {
    'Makefile.in': 'Default ignore: automake artifact',
    'Makefile.am': 'Default ignore: automake artifact',
    'autom4te.cache': 'Default ignore: autoconf artifact',
    '*.m4': 'Default ignore: autotools artifact',
    'configure': 'Default ignore: Configure script',
    'configure.bat': 'Default ignore: Configure script',
    'configure.sh': 'Default ignore: Configure script',
    'configure.ac': 'Default ignore: Configure script',
    'config.guess': 'Default ignore: Configure script',
    'config.sub': 'Default ignore: Configure script',
    'compile': 'Default ignore: autoconf artifact',
    'depcomp': 'Default ignore: autoconf artifact',
    'ltmain.sh': 'Default ignore: libtool autoconf artifact',
    'install-sh': 'Default ignore: autoconf artifact',
    'missing': 'Default ignore: autoconf artifact',
    'mkinstalldirs': 'Default ignore: autoconf artifact',
    'stamp-h1': 'Default ignore: autoconf artifact',
    'm4/': 'Default ignore: autoconf artifact',
    'autogen.sh': 'Default ignore: autotools artifact',
    'autogen.sh': 'Default ignore: autotools artifact',

    'CMakeCache.txt': 'Default ignore: CMake artifact',
    'cmake_install.cmake': 'Default ignore: CMake artifact',
    'install_manifest.txt': 'Default ignore: CMake artifact',
}

ignores_CI = {
    '.travis.yml' : 'Default ignore: Travis config',
    '.coveragerc' : 'Default ignore: Coverall config',
}

ignores_Python = {
    'pip-selfcheck.json': 'Default ignore: Pip workfile',
    'pytest.ini': 'Default ignore: Python pytest config',
    'tox.ini': 'Default ignore: Python tox config',
    '__pycache__/': 'Default ignore: Python bytecode cache',
    '.installed.cfg': 'Default ignore: Python Buildout artifact',
    'pip-log.txt': 'Default ignore: Python pip artifact',
    'pip-delete-this-directory.txt': 'Default ignore: Python pip artifact',
    'pyvenv.cfg': 'Default ignore: Python virtualenv artifact',
}

ignores_I18N = {
    '*.mo': 'Default ignore: Translation file',
    '*.pot': 'Default ignore: Translation file',
    '.localized': 'Default ignore: localized file',
}

ignores_coverage_and_tests = {
    '*.gcno': 'Default ignore: GCC coverage',
    '*.gcda': 'Default ignore: GCC coverage',
    '*.gcov': 'Default ignore: GCC coverage',
    '.last_cover_stats': 'Default ignore: Perl coverage',
    'htmlcov/': 'Default ignore: Python coverage',
    '.tox/': 'Default ignore: Tox tem dir',
    '.coverage': 'Default ignore: Python coverage',
    '.coverage.*': 'Default ignore: Python coverage',
    'nosetests.xml': 'Default ignore: Python nose tests',
    'coverage.xml': 'Default ignore: Python coverage',
    '/spec/reports/': 'Default ignore: Ruby Rails test report',
    '/rdoc/': 'Default ignore: Ruby doc',
    '.rvmrc': 'Default ignore: Ruby RVM',
    '.sass-cache': 'Default ignore: Saas cache',
    '*.css.map': 'Default ignore: Saas map',
    'phpunit.xml': 'Default ignore: phpunit',
    '*.VisualState.xml': 'Default ignore: Nunit',
    'TestResult.xml': 'Default ignore: Nunit',
}

ignores_Misc = {
    'pax_global_header': 'Default ignore: Pax header file',
    'C++.gitignore': 'Default ignore: C++.gitignore',
    '.gwt/': 'Default ignore: GWT compilation logs',
    '.gwt-tmp/': 'Default ignore: GWT temp files',
    'gradle-app.setting': 'Default ignore: Graddle app settings',
    'hs_err_pid*': 'Default ignore: Java VM crash logs',
    '.grunt': 'Default ignore: Grunt intermediate storage',
    '.history': 'Default ignore: History file',
    '.~lock.*#': 'Default ignore: LibreOffice locks',
    '/.ssh': 'Default ignore: SSH configuration',
}


default_ignores = {}

default_ignores.update(chain(*[d.items() for d in [
    ignores_MacOSX,
    ignores_Windows,
    ignores_Linux,
    ignores_IDEs,
    ignores_web,
    ignores_Maven,
    ignores_VCS,
    ignores_Medias,
    ignores_Build_scripts,
    ignores_CI,
    ignores_Python,
    ignores_I18N,
    ignores_coverage_and_tests,
    ignores_Misc,
    ignores_Build_scripts,
]]))
