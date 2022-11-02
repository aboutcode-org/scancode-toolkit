# -*- coding: utf-8 -*-

"""
Python Frontmatter: Parse and manage posts with YAML frontmatter

Based on and modified from ``python-frontmatter`` version 1.0.0.

license: mit. See frontmatter.ABOUT file for details.
"""


import codecs
import saneyaml
import re

from frontmatter import detect_format
from frontmatter import handlers
from frontmatter import Post as FrontmatterPost
from frontmatter.default_handlers import BaseHandler
from frontmatter.util import u

from licensedcode.tokenize import query_lines



class SaneYAMLHandler(BaseHandler):
    """
    Load and export YAML metadata. .

    This is similar to the frontmatter.default_handlers.YAMLHandler but
    is using nexB/saneyaml instead of pyyaml.
    """
    FM_BOUNDARY = re.compile(r"^-{3,}\s*$", re.MULTILINE)
    START_DELIMITER = END_DELIMITER = "---"

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
        return u(metadata)  # ensure unicode


def get_rule_text(location=None, text=None):
    """
    Return the rule ``text`` prepared for indexing.
    ###############
    # IMPORTANT: we use the same process as used to load query text for symmetry
    ###############
    """
    numbered_lines = query_lines(location=location, query_string=text, plain_text=True)
    return '\n'.join(l.strip() for _, l in numbered_lines)


def parse_frontmatter(text, encoding="utf-8", handler=None, **defaults):
    """
    Parse text with frontmatter, return metadata and content.
    Pass in optional metadata defaults as keyword args.

    If frontmatter is not found, returns an empty metadata dictionary
    (or defaults) and original text content.

    This is similar to the frontmatter.parse but is using `get_rule_text`
    to use the same process as loading quary text for symmetry.
    """
    # ensure unicode first
    text = u(text, encoding).strip()

    # metadata starts with defaults
    metadata = defaults.copy()

    # this will only run if a handler hasn't been set higher up
    handler = handler or detect_format(text, handlers)
    if handler is None:
        return metadata, text

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

    text = get_rule_text(text=content)

    return metadata, text


def loads_frontmatter(text, encoding="utf-8", handler=None, **defaults):
    """
    Parse text (binary or unicode) and return a :py:class:`post <frontmatter.Post>`.

    This is similar to the frontmatter.loads but is using the `parse`
    function defined above.
    """
    text = u(text, encoding)
    handler = handler or detect_format(text, handlers)
    metadata, content = parse_frontmatter(text, encoding, handler, **defaults)
    return FrontmatterPost(content, handler, **metadata)


def load_frontmatter(fd, encoding="utf-8", handler=None, **defaults):
    """
    Load and parse a file-like object or filename,
    return a :py:class:`post <frontmatter.Post>`.

    This is similar to the frontmatter.load but is using the `loads`
    function defined above.
    """
    if hasattr(fd, "read"):
        text = fd.read()

    else:
        with codecs.open(fd, "r", encoding) as f:
            text = f.read()

    handler = handler or detect_format(text, handlers)
    return loads_frontmatter(text, encoding, handler, **defaults)


def dumps_frontmatter(post, handler=None, **kwargs):
    """
    Serialize a :py:class:`post <frontmatter.Post>` to a string and return text.
    This always returns unicode text, which can then be encoded.

    Passing ``handler`` will change how metadata is turned into text. A handler
    passed as an argument will override ``post.handler``, with
    :py:class:`SaneYAMLHandler <frontmatter.SaneYAMLHandler>` used as
    a default.

    This is similar to the frontmatter.dumps but is using the `SaneYAMLHandler`
    defined above as default instead of frontmatter.default_handlers.YAMLHandler.
    """
    if handler is None:
        handler = getattr(post, "handler", None) or SaneYAMLHandler()

    return handler.format(post, **kwargs)
