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
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


@post_scan_impl
class FileCategorizer(PostScanPlugin):
    """
    Categorize a file.
    """
    # resource_attributes = dict([
    #     ('category',
    #      String(help='Category.')),

    #     ('subcategory',
    #      String(help='Subcategory.')),
    # ])
    resource_attributes = dict([
        ('file_category',
         String(help='File category.')),

        ('file_subcategory',
         String(help='File subcategory.')),
    ])

    sort_order = 50

    options = [
        # PluggableCommandLineOption(('--categorize',),
        PluggableCommandLineOption(('--file-cat',),
            is_flag=True, default=False,
            help='Categorize files.',
            help_group=POST_SCAN_GROUP,
            sort_order=50,
        )
    ]

    # def is_enabled(self, categorize, **kwargs):
    #     return categorize
    def is_enabled(self, file_cat, **kwargs):
        return file_cat

    # def process_codebase(self, codebase, categorize, **kwargs):
    #     if not categorize:
    #         return
    def process_codebase(self, codebase, file_cat, **kwargs):
        if not file_cat:
            return

        for resource in codebase.walk(topdown=True):
            if resource.is_file:
                category = categorize_resource(resource)
                if not category:
                    continue
                # resource.category = category.file_category
                # resource.subcategory = category.file_subcategory
                resource.file_category = category.file_category
                resource.file_subcategory = category.file_subcategory
                resource.save(codebase)


class Categorizer:
    order = 0
    rule_applied = None
    analysis_priority = None
    file_category = None
    file_subcategory = None
    notes = None

    @classmethod
    def categorize(cls, resource):
        """
        Return True if this Categorizer applies to this resource or False or None
        otherwise.
        """
        raise NotImplementedError


class archive_debian(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'archive'
    file_subcategory = 'debian'
    notes = 'special type of archive'

    @classmethod
    def categorize(cls, resource):
        return (
        resource.extension.lower() in [".deb"]
        )


class archive_general(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'archive'
    file_subcategory = 'general'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".7zip", ".bz", ".bz2", ".bzip", ".gz", ".gzi", ".tar", ".tgz", ".xz", ".zip"]
        )


class archive_rpm(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'archive'
    file_subcategory = 'rpm'
    notes = 'special type of archive'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".rpm"]
        )


class binary_ar(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'ar'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["application/x-archive"]
        )


class binary_elf_exec(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'elf-exec'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["application/x-executable"]
        )


class binary_elf_ko(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'elf-ko'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["application/x-object"]
            and
            resource.extension.lower().startswith('.ko')
        )


class binary_elf_o(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'elf-o'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["application/x-object"]
            and
            not resource.extension.lower().startswith('.ko')
        )


class binary_elf_so(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'elf-so'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["application/x-sharedlib"]
        )


class binary_java(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'java'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".class", ".jar"]
        )


class binary_windows(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'binary'
    file_subcategory = 'windows'
    notes = 'For DLL and EXE binaries in Windows'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["application/x-dosexec"]
        )


class config_general(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'config'
    file_subcategory = 'general'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".bat", ".cfg", ".conf", ".config", ".sh", ".yaml", ".yml"]
        )


class config_xml(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'config'
    file_subcategory = 'xml'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".dtd", ".xml", ".xsd", ".xsl", ".xslt"]
        )


class data_json(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'data'
    file_subcategory = 'json'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".json"]
        )


class doc_general(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'doc'
    file_subcategory = 'general'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".csv", ".doc", ".docx", ".md", ".odp", ".ods", ".odt", ".pdf", ".ppt", ".pptx", ".rtf", ".tex", ".txt", ".xls", ".xlsm", ".xlsx"]
        )


class doc_readme(Categorizer):
    order = 0
    analysis_priority = '3'
    file_category = 'doc'
    file_subcategory = 'readme'

    @classmethod
    def categorize(cls, resource):
        return (
            "readme" in resource.name.lower()
        )


class font(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'font'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".fnt", ".otf", ".ttf", ".woff", ".woff2", ".eot"]
        )


class manifest_npm(Categorizer):
    order = 0
    analysis_priority = '1'
    file_category = 'manifest'
    file_subcategory = 'npm'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.name.lower() in ["package.json", "package-lock.json"]
        )


class media_audio(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'media'
    file_subcategory = 'audio'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".mp3", ".mpa", ".ogg", ".wav", ".wma"]
        )


class media_image(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'media'
    file_subcategory = 'image'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".bmp", ".gif", ".ico", ".jpg", ".jpeg", ".png", ".svg"]
        )


class media_video(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'media'
    file_subcategory = 'video'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".avi", ".h264", ".mp4", ".mpg", ".mpeg", ".swf", ".wmv"]
        )


class script_bash(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'script'
    file_subcategory = 'bash'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".bash"]
        )


class script_build(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'build'
    file_subcategory = 'script'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".cmake", ".cmakelist"]
        )


class script_perl(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'script'
    file_subcategory = 'perl'
    notes = 'We will treat all Perl as script'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.mime_type in ["text/x-perl"]
        )


class script_data(Categorizer):
    order = 1
    analysis_priority = '3'
    file_category = 'data'
    file_subcategory = 'script'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".sql", ".psql"]
        )


class source_c(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'c'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".c"]
            or
            (
                resource.extension.lower() in [".h"]
                and
                resource.mime_type in ["text/x-c"]
            )
        )


class source_cpp(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'c++'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".cpp", ".hpp", ".cc"]
            or
            (
                resource.extension.lower() in [".h"]
                and
                resource.mime_type in ["text/x-c++"]
            )
        )


class source_csharp(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'c#'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".cs"]
        )


class source_go(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'go'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".go"]
        )


class source_haskell(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'haskell'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".hs", ".lhs"]
        )


class source_java(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'java'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".java"]
        )


class source_javascript(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'javascript'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".js"]
        )


class source_javaserverpage(Categorizer):
    order = 1
    analysis_priority = '2'
    file_category = 'source'
    file_subcategory = 'javaserverpage'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".jsp"]
        )


class source_kotlin(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'kotlin'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".kt"]
        )


class source_objectivec(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'objectivec'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".m", ".mm"]
            or
            (
                resource.extension.lower() in [".h"]
                and
                resource.mime_type in ["text/x-objective-c"]
            )
        )


class source_php(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'php'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".php", ".php3", ".php4", ".php5"]
        )


class source_python(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'python'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".py"]
        )


class source_ruby(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'ruby'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".rb", ".rake"]
        )


class source_rust(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'rust'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".rs"]
        )


class source_scala(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'scala'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".scala"]
        )


class source_swift(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'swift'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".swift"]
        )


class source_typescript(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'source'
    file_subcategory = 'typescript'
    notes = '.ts extension is not definitive'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".ts"]
            and
            resource.programming_language in ["TypeScript"]
        )


class web_css(Categorizer):
    order = 1
    analysis_priority = '1'
    file_category = 'web'
    file_subcategory = 'css'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".css"]
        )


class web_html(Categorizer):
    order = 1
    analysis_priority = '2'
    file_category = 'web'
    file_subcategory = 'html'

    @classmethod
    def categorize(cls, resource):
        return (
            resource.extension.lower() in [".htm", ".html"]
        )


categories = [
    archive_debian,
    archive_general,
    archive_rpm,
    binary_ar,
    binary_elf_exec,
    binary_elf_ko,
    binary_elf_o,
    binary_elf_so,
    binary_java,
    binary_windows,
    config_general,
    config_xml,
    data_json,
    doc_general,
    doc_readme,
    font,
    manifest_npm,
    media_audio,
    media_image,
    media_video,
    script_bash,
    script_build,
    script_data,
    script_perl,
    source_c,
    source_cpp,
    source_csharp,
    source_go,
    source_haskell,
    source_java,
    source_javascript,
    source_javaserverpage,
    source_kotlin,
    source_objectivec,
    source_php,
    source_python,
    source_ruby,
    source_rust,
    source_scala,
    source_swift,
    source_typescript,
    web_css,
    web_html
]


def category_key(category):
    return category.order


def categorize_resource(resource):
    """
    Return a Categorizer for this ``resource`` Resource object, or None.
    """
    for category in sorted(categories, key=category_key):
        if category.categorize(resource):
            return category
