# -*- coding: utf-8 -*-

"""
Python Frontmatter: Parse and manage posts with YAML frontmatter

Based on and heavily modified/simplified from ``python-frontmatter``
version 1.0.0, to only support nexB/saneyaml instead of pure YAML.

license: mit. See frontmatter.ABOUT file for details.
"""

import codecs
import saneyaml
import re

DEFAULT_POST_TEMPLATE = """\
{start_delimiter}
{metadata}
{end_delimiter}

{content}
"""


class SaneYAMLHandler:
    """
    Load and export YAML metadata. .

    This is similar to the original frontmatter.default_handlers.YAMLHandler
    but is using nexB/saneyaml instead of pyyaml.
    """
    FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "---"

    def __init__(self):
        self.FM_BOUNDARY = self.FM_BOUNDARY
        self.START_DELIMITER = self.START_DELIMITER
        self.END_DELIMITER = self.END_DELIMITER

    def detect(self, text):
        """
        Decide whether this handler can parse the given ``text``,
        and return True or False.
        """
        if self.FM_BOUNDARY.match(text):
            return True
        return False

    def split(self, text):
        """
        Split text into frontmatter and content.
        """
        _, fm, content = self.FM_BOUNDARY.split(text, 2)
        return fm, content

    def format(self, content, metadata, **kwargs):
        """
        Return string with `content` and `metadata` as YAML frontmatter,
        used in ``frontmatter.dumps``.
        """
        start_delimiter = kwargs.pop("start_delimiter", self.START_DELIMITER)
        end_delimiter = kwargs.pop("end_delimiter", self.END_DELIMITER)

        metadata = self.export(metadata, **kwargs)

        return DEFAULT_POST_TEMPLATE.format(
            metadata=metadata,
            content=content,
            start_delimiter=start_delimiter,
            end_delimiter=end_delimiter,
        ).strip()

    def load(self, fm, **kwargs):
        """
        Parse YAML front matter.
        """
        return saneyaml.load(fm, allow_duplicate_keys=False, **kwargs)

    def export(self, metadata, **kwargs):
        """
        Export metadata as YAML.
        """
        metadata = saneyaml.dump(metadata, indent=4, encoding='utf-8', **kwargs).strip()
        return return_unicode(metadata)  # ensure unicode


def return_unicode(text, encoding="utf-8"):
    """
    Return unicode text, no matter what.
    """

    if isinstance(text, bytes):
        text = text.decode(encoding)

    # it's already unicode
    text = text.replace("\r\n", "\n")
    return text


def parse_frontmatter(text, encoding="utf-8", handler=SaneYAMLHandler(), **defaults):
    """
    Parse text with frontmatter, return `content` and `metadata`.
    Pass in optional metadata defaults as keyword args.

    If frontmatter is not found, returns an empty metadata dictionary
    (or defaults) and original text content.
    """
    # ensure unicode first
    text = return_unicode(text, encoding)

    # metadata starts with defaults
    metadata = defaults.copy()

    # split on the delimiters
    try:
        fm, content = handler.split(text)
    except ValueError:
        # if we can't split, bail
        return metadata, text

    # parse, now that we have frontmatter
    fm = handler.load(fm)
    if isinstance(fm, dict):
        metadata.update(fm)

    return content, metadata


def load_frontmatter(fd, encoding="utf-8", **defaults):
    """
    Load and parse a file-like object or filename `fd`, and return
    `content` and `metadata` with the text and the frontmatter metadata.
    """
    if hasattr(fd, "read"):
        text = fd.read()

    else:
        with codecs.open(fd, "r", encoding) as f:
            text = f.read()

    text = return_unicode(text, encoding)
    return parse_frontmatter(text, encoding, **defaults)


def dumps_frontmatter(content, metadata, handler=SaneYAMLHandler(), **kwargs):
    """
    Create a string and return the text from `content` and `metadata`.
    """
    return handler.format(content, metadata, **kwargs)
