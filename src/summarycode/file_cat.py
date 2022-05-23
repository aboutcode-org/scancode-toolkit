#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

from commoncode.datautils import String
from plugincode.post_scan import PostScanPlugin
from plugincode.post_scan import post_scan_impl
from commoncode.cliutils import PluggableCommandLineOption
from commoncode.cliutils import POST_SCAN_GROUP

"""
Categorize files.
"""

# Tracing flag
TRACE = False


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import click

    class ClickHandler(logging.Handler):
        _use_stderr = True

        def emit(self, record):
            try:
                msg = self.format(record)
                click.echo(msg, err=self._use_stderr)
            except Exception:
                self.handleError(record)

    logger = logging.getLogger(__name__)
    logger.handlers = [ClickHandler()]
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(" ".join(isinstance(a, str) and a or repr(a) for a in args))


@post_scan_impl
class FileCategorizer(PostScanPlugin):
    """
    Categorize a file.
    """

    resource_attributes = dict(
        [
            ("analysis_priority", String(help="Analysis priority.")),
            ("file_category", String(help="File category.")),
            ("file_subcategory", String(help="File subcategory.")),
        ]
    )

    sort_order = 50

    options = [
        PluggableCommandLineOption(
            ("--file-cat",),
            is_flag=True,
            default=False,
            help="Categorize files.",
            help_group=POST_SCAN_GROUP,
            sort_order=50,
        )
    ]

    def is_enabled(self, file_cat, **kwargs):
        return file_cat

    def process_codebase(self, codebase, file_cat, **kwargs):
        if not file_cat:
            return

        for resource in codebase.walk(topdown=True):
            category = categorize_resource(resource)
            if not category:
                continue
            resource.analysis_priority = category.analysis_priority
            resource.file_category = category.file_category
            resource.file_subcategory = category.file_subcategory
            resource.save(codebase)


class Categorizer:
    order = 0
    analysis_priority = None
    file_category = None
    file_subcategory = None
    category_notes = None
    rule_applied = None

    @classmethod
    def categorize(cls, resource):
        """
        Return True if this Categorizer applies to this resource or False or None
        otherwise.
        """
        raise NotImplementedError


class ArchiveAndroid(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "archive"
    file_subcategory = "Android"
    rule_applied = "ArchiveAndroid"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".apk", ".aar"])


class ArchiveDebian(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "archive"
    file_subcategory = "debian"
    category_notes = "special type of archive"
    rule_applied = "ArchiveDebian"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".deb"])


class ArchiveGeneral(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "archive"
    file_subcategory = "general"
    rule_applied = "ArchiveGeneral"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension,
            [
                ".7zip",
                ".bz",
                ".bz2",
                ".bzip",
                ".gz",
                ".gzi",
                ".tar",
                ".tgz",
                ".xz",
                ".zip",
            ],
        )


class ArchiveIos(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "archive"
    file_subcategory = "iOS"
    rule_applied = "ArchiveIos"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".ipa"])


class ArchiveRpm(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "archive"
    file_subcategory = "rpm"
    category_notes = "special type of archive"
    rule_applied = "ArchiveRpm"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".rpm"])


class BinaryAr(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "ar"
    rule_applied = "BinaryAr"

    @classmethod
    def categorize(cls, resource):
        return resource.mime_type in ["application/x-archive"]


class BinaryElfExec(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "elf-exec"
    rule_applied = "BinaryElfExec"

    @classmethod
    def categorize(cls, resource):
        return resource.mime_type in ["application/x-executable"]


class BinaryElfKo(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "elf-ko"
    rule_applied = "BinaryElfKo"

    @classmethod
    def categorize(cls, resource):
        return resource.mime_type in ["application/x-object"] and extension_startswith(
            resource.extension, (".ko")
        )


class BinaryElfO(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "elf-o"
    rule_applied = "BinaryElfO"

    @classmethod
    def categorize(cls, resource):
        return resource.mime_type in [
            "application/x-object"
        ] and not extension_startswith(resource.extension, (".ko"))


class BinaryElfSo(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "elf-so"
    rule_applied = "BinaryElfSo"

    @classmethod
    def categorize(cls, resource):
        return resource.mime_type in ["application/x-sharedlib"]


class BinaryJava(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "java"
    rule_applied = "BinaryJava"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension, [".class", ".jar", ".ear", ".sar", ".war"]
        )


class BinaryPython(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "Python"
    rule_applied = "BinaryPython"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".pyc", ".pyo"])


class BinaryWindows(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "binary"
    file_subcategory = "windows"
    category_notes = "For DLL and EXE binaries in Windows"
    rule_applied = "BinaryWindows"

    @classmethod
    def categorize(cls, resource):
        return resource.mime_type in ["application/x-dosexec"]


class BuildBazel(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "build"
    file_subcategory = "Bazel"
    rule_applied = "BuildBazel"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".bzl"]) or (
            name_in(resource.name, ["build.bazel"]) and resource.type == "file"
        )


class BuildBuck(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "build"
    file_subcategory = "BUCK"
    rule_applied = "BuildBuck"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["buck"]) and resource.type == "file"


class BuildDocker(Categorizer):
    order = 0
    analysis_priority = "2"
    file_category = "build"
    file_subcategory = "Docker"
    category_notes = 'May have an "arbitrary" extension'
    rule_applied = "BuildDocker"

    @classmethod
    def categorize(cls, resource):
        return name_substring(resource.name, ["dockerfile"]) and resource.type == "file"


class BuildMake(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "build"
    file_subcategory = "make"
    category_notes = '"Makefile" may have an "arbitrary" extension'
    rule_applied = "BuildMake"

    @classmethod
    def categorize(cls, resource):
        return (
            name_substring(resource.name, ["makefile"]) and resource.type == "file"
        ) or extension_in(resource.extension, [".mk", ".make"])


class BuildQt(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "build"
    file_subcategory = "Qt"
    rule_applied = "BuildQt"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".pri", ".pro"])


class Certificate(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "certificate"
    file_subcategory = ""
    rule_applied = "Certificate"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".crt", ".der", ".pem"])


class ConfigGeneral(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "general"
    rule_applied = "ConfigGeneral"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension,
            [".cfg", ".conf", ".config", ".jxs", ".properties", ".yaml", ".yml"],
        )


class ConfigInitialPeriod(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "initial_period"
    rule_applied = "ConfigInitialPeriod"

    @classmethod
    def categorize(cls, resource):
        return name_startswith(resource.name, (".")) and resource.type == "file"


class ConfigMacro(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "macro"
    rule_applied = "ConfigMacro"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".m4"])


class ConfigPython(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "Python"
    rule_applied = "ConfigPython"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["__init__.py"]) and resource.type == "file"


class ConfigTemplate(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "template"
    rule_applied = "ConfigTemplate"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".tmpl"])


class ConfigVisualCpp(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "Visual-CPP"
    category_notes = "vcproj is older version"
    rule_applied = "ConfigVisualCpp"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".vcxproj", ".vcproj"])


class ConfigXcode(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "xcode"
    rule_applied = "ConfigXcode"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["info.plist"]) and resource.type == "file"


class ConfigXml(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "config"
    file_subcategory = "xml"
    rule_applied = "ConfigXml"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension, [".dtd", ".xml", ".xsd", ".xsl", ".xslt"]
        )


class DataJson(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "data"
    file_subcategory = "json"
    rule_applied = "DataJson"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".json"])


class DataProtoBuf(Categorizer):
    order = 10
    analysis_priority = "2"
    file_category = "data"
    file_subcategory = "ProtoBuf"
    rule_applied = "DataProtoBuf"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".proto"])


class Directory(Categorizer):
    order = 10
    analysis_priority = "4"
    file_category = "directory"
    file_subcategory = ""
    rule_applied = "Directory"

    @classmethod
    def categorize(cls, resource):
        return resource.type == "directory"


class DocGeneral(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "doc"
    file_subcategory = "general"
    rule_applied = "DocGeneral"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension,
            [
                ".csv",
                ".doc",
                ".docx",
                ".man",
                ".md",
                ".odp",
                ".ods",
                ".odt",
                ".pdf",
                ".ppt",
                ".pptx",
                ".rtf",
                ".tex",
                ".txt",
                ".xls",
                ".xlsm",
                ".xlsx",
            ],
        ) or (
            name_in(resource.name, ["changelog", "changes"]) and resource.type == "file"
        )


class DocLicense(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "doc"
    file_subcategory = "license"
    rule_applied = "DocLicense"

    @classmethod
    def categorize(cls, resource):
        return (
            name_substring(resource.name, ["copying", "copyright", "license", "notice"])
            and resource.type == "file"
        )


class DocReadme(Categorizer):
    order = 0
    analysis_priority = "3"
    file_category = "doc"
    file_subcategory = "readme"
    rule_applied = "DocReadme"

    @classmethod
    def categorize(cls, resource):
        return name_substring(resource.name, ["readme"]) and resource.type == "file"


class Font(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "font"
    rule_applied = "Font"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension, [".fnt", ".otf", ".ttf", ".woff", ".woff2", ".eot"]
        )


class ManifestBower(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Bower"
    rule_applied = "ManifestBower"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["bower.json"]) and resource.type == "file"


class ManifestCargo(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Cargo"
    category_notes = "For Rust, Not sure about Cargo.toml ?"
    rule_applied = "ManifestCargo"

    @classmethod
    def categorize(cls, resource):
        return (
            name_in(resource.name, ["cargo.toml", "cargo.lock"])
            and resource.type == "file"
        )


class ManifestCocoaPod(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "CocoaPod"
    rule_applied = "ManifestCocoaPod"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".podspec"])


class ManifestComposer(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Composer"
    category_notes = "For PHP"
    rule_applied = "ManifestComposer"

    @classmethod
    def categorize(cls, resource):
        return (
            name_in(resource.name, ["composer.json", "composer.lock"])
            and resource.type == "file"
        )


class ManifestGolang(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Golang"
    rule_applied = "ManifestGolang"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["go.mod", "go.sum"]) and resource.type == "file"


class ManifestGradle(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Gradle"
    rule_applied = "ManifestGradle"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["build.gradle"]) and resource.type == "file"


class ManifestHaxe(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Haxe"
    rule_applied = "ManifestHaxe"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["haxelib.json"]) and resource.type == "file"


class ManifestIvy(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "Ivy"
    rule_applied = "ManifestIvy"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["ivy.xml"]) and resource.type == "file"


class ManifestMaven(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "maven"
    rule_applied = "ManifestMaven"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["pom.xml"]) and resource.type == "file"


class ManifestNpm(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "npm"
    rule_applied = "ManifestNpm"

    @classmethod
    def categorize(cls, resource):
        return (
            name_in(resource.name, ["package.json", "package-lock.json", "yarn.lock"])
            and resource.type == "file"
        )


class ManifestNuGet(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "NuGet"
    rule_applied = "ManifestNuGet"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".nuspec"])


class ManifestPyPi(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "PyPi"
    rule_applied = "ManifestPyPi"

    @classmethod
    def categorize(cls, resource):
        return name_in(resource.name, ["requirements.txt"]) and resource.type == "file"


class ManifestRubyGem(Categorizer):
    order = 0
    analysis_priority = "1"
    file_category = "manifest"
    file_subcategory = "RubyGem"
    rule_applied = "ManifestRubyGem"

    @classmethod
    def categorize(cls, resource):
        return (
            name_in(resource.name, ["gemfile", "gemfile.lock"])
            and resource.type == "file"
        )


class MediaAudio(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "media"
    file_subcategory = "audio"
    rule_applied = "MediaAudio"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension,
            [
                ".3pg",
                ".aac",
                ".amr",
                ".awb",
                ".m4a",
                ".mp3",
                ".mpa",
                ".ogg",
                ".opus",
                ".wav",
                ".wma",
            ],
        )


class MediaImage(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "media"
    file_subcategory = "image"
    rule_applied = "MediaImage"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension,
            [".bmp", ".gif", ".ico", ".jpg", ".jpeg", ".png", ".svg", ".webp"],
        )


class MediaVideo(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "media"
    file_subcategory = "video"
    rule_applied = "MediaVideo"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension,
            [".avi", ".h264", ".mp4", ".mpg", ".mpeg", ".swf", ".wmv"],
        )


class ScriptBash(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "script"
    file_subcategory = "bash"
    rule_applied = "ScriptBash"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".bash"])


class ScriptBatSh(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "script"
    file_subcategory = "bat_sh"
    rule_applied = "ScriptBatSh"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".bat", ".sh"])


class ScriptBuild(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "script"
    file_subcategory = "build"
    rule_applied = "ScriptBuild"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension, [".cmake", ".cmakelist"]
        ) or resource.mime_type in ["text/x-makefile"]


class ScriptData(Categorizer):
    order = 10
    analysis_priority = "3"
    file_category = "script"
    file_subcategory = "data"
    rule_applied = "ScriptData"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".sql", ".psql"])


class SourceAssembler(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "assembler"
    category_notes = "upper case only"
    rule_applied = "SourceAssembler"

    @classmethod
    def categorize(cls, resource):
        return extension_uppercase_in(resource.extension, [".S"])


class SourceC(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "c"
    rule_applied = "SourceC"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".c"]) or (
            extension_in(resource.extension, [".h"])
            and resource.mime_type in ["text/x-c"]
        )


class SourceCoffeeScript(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "CoffeeScript"
    category_notes = "transcompiles to JS"
    rule_applied = "SourceCoffeeScript"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".coffee"])


class SourceCpp(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "c++"
    rule_applied = "SourceCpp"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".cpp", ".hpp", ".cc"]) or (
            extension_in(resource.extension, [".h"])
            and resource.mime_type in ["text/x-c++"]
        )


class SourceCsharp(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "c#"
    rule_applied = "SourceCsharp"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".cs"])


class SourceGo(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "go"
    rule_applied = "SourceGo"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".go"])


class SourceHaskell(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "haskell"
    rule_applied = "SourceHaskell"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".hs", ".lhs"])


class SourceJava(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "java"
    rule_applied = "SourceJava"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".java"])


class SourceJavascript(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "javascript"
    rule_applied = "SourceJavascript"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".js"])


class SourceJavaserverpage(Categorizer):
    order = 10
    analysis_priority = "2"
    file_category = "source"
    file_subcategory = "javaserverpage"
    rule_applied = "SourceJavaserverpage"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".jsp"])


class SourceKotlin(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "kotlin"
    rule_applied = "SourceKotlin"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".kt"])


class SourceObjectivec(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "objectivec"
    rule_applied = "SourceObjectivec"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".m", ".mm"]) or (
            extension_in(resource.extension, [".h"])
            and resource.mime_type in ["text/x-objective-c"]
        )


class SourcePerl(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "perl"
    rule_applied = "SourcePerl"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".pl", ".pm"])


class SourcePhp(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "php"
    rule_applied = "SourcePhp"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".php", ".php3", ".php4", ".php5"])


class SourcePython(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "python"
    rule_applied = "SourcePython"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".py"])


class SourceRuby(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "ruby"
    rule_applied = "SourceRuby"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".rb", ".rake"])


class SourceRust(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "rust"
    rule_applied = "SourceRust"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".rs"])


class SourceScala(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "scala"
    rule_applied = "SourceScala"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".scala"])


class SourceSwift(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "swift"
    rule_applied = "SourceSwift"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".swift"])


class SourceTypescript(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "source"
    file_subcategory = "typescript"
    category_notes = ".ts extension is not definitive"
    rule_applied = "SourceTypescript"

    @classmethod
    def categorize(cls, resource):
        return extension_in(
            resource.extension, [".ts"]
        ) and resource.programming_language in ["TypeScript"]


class WebCss(Categorizer):
    order = 10
    analysis_priority = "1"
    file_category = "web"
    file_subcategory = "css"
    rule_applied = "WebCss"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".css", ".less", ".scss"])


class WebHtml(Categorizer):
    order = 10
    analysis_priority = "2"
    file_category = "web"
    file_subcategory = "html"
    rule_applied = "WebHtml"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".htm", ".html"])


class WebRuby(Categorizer):
    order = 10
    analysis_priority = "2"
    file_category = "web"
    file_subcategory = "Ruby"
    rule_applied = "WebRuby"

    @classmethod
    def categorize(cls, resource):
        return extension_in(resource.extension, [".erb"])


categories = [
    ArchiveAndroid,
    ArchiveDebian,
    ArchiveGeneral,
    ArchiveIos,
    ArchiveRpm,
    BinaryAr,
    BinaryElfExec,
    BinaryElfKo,
    BinaryElfO,
    BinaryElfSo,
    BinaryJava,
    BinaryPython,
    BinaryWindows,
    BuildBazel,
    BuildBuck,
    BuildDocker,
    BuildMake,
    BuildQt,
    Certificate,
    ConfigGeneral,
    ConfigInitialPeriod,
    ConfigMacro,
    ConfigPython,
    ConfigTemplate,
    ConfigVisualCpp,
    ConfigXcode,
    ConfigXml,
    DataJson,
    DataProtoBuf,
    Directory,
    DocGeneral,
    DocLicense,
    DocReadme,
    Font,
    ManifestBower,
    ManifestCargo,
    ManifestCocoaPod,
    ManifestComposer,
    ManifestGolang,
    ManifestGradle,
    ManifestHaxe,
    ManifestIvy,
    ManifestMaven,
    ManifestNpm,
    ManifestNuGet,
    ManifestPyPi,
    ManifestRubyGem,
    MediaAudio,
    MediaImage,
    MediaVideo,
    ScriptBash,
    ScriptBatSh,
    ScriptBuild,
    ScriptData,
    SourceAssembler,
    SourceC,
    SourceCoffeeScript,
    SourceCpp,
    SourceCsharp,
    SourceGo,
    SourceHaskell,
    SourceJava,
    SourceJavascript,
    SourceJavaserverpage,
    SourceKotlin,
    SourceObjectivec,
    SourcePerl,
    SourcePhp,
    SourcePython,
    SourceRuby,
    SourceRust,
    SourceScala,
    SourceSwift,
    SourceTypescript,
    WebCss,
    WebHtml,
    WebRuby,
]


def category_key(category):
    return category.order


def categorize_resource(resource):
    """
    Return a Categorizer for this ``resource`` Resource object, or None.
    """
    sorted_categories = sorted(categories, key=category_key)
    for category in sorted_categories:
        if category.categorize(resource):
            return category


def extension_in(ext, exts):
    return str(ext).lower() in exts


def extension_uppercase_in(ext, exts):
    return ext in exts


def extension_startswith(ext, exts):
    return str(ext).lower().startswith(exts)


def name_in(name, names):
    return str(name).lower() in names


def name_substring(name, names):
    return any(string in str(name).lower() for string in names)


def name_startswith(name, names):
    return str(name).lower().startswith(names)
