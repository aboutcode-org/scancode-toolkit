

import logging
import os
import re

from packagedcode import models
from commoncode import fileutils
from commoncode import text

logger = logging.getLogger(__name__)

class BazelPackage(models.Package):
    """
    A `BazelPackage` object represents a package defined by the Bazel build system.
    """
    default_type = 'bazel'
    default_primary_language = 'Python'
    default_web_baseurl = None
    default_download_baseurl = None
    default_api_baseurl = None

    @classmethod
    def recognize(cls, location):
        """
        Recognize if the given file is a Bazel BUILD or WORKSPACE file and yield a BazelPackage.
        """
        logger.debug('BazelPackage.recognize: Processing file at %s', location)
        filename = os.path.basename(location)
        if filename in ('BUILD', 'BUILD.bazel', 'WORKSPACE', 'WORKSPACE.bazel'):
            package = parse_bazel_file(location)
            if package:
                yield package


def parse_bazel_file(location):
    """
    Parse a Bazel BUILD or WORKSPACE file to extract package information.
    """
    logger.debug('parse_bazel_file: Parsing file at %s', location)
    if not fileutils.file_exists(location):
        logger.error('parse_bazel_file: File does not exist at %s', location)
        return None
    with open(location, 'r', encoding='utf-8') as bazel_file:
        content = bazel_file.read()
    name = extract_name(content)
    version = extract_version(content)
    dependencies = extract_dependencies(content)

    if name:
        package = BazelPackage(
            name=name,
            version=version,
            declared_license=None,
            dependencies=dependencies,
            homepage_url=None,
        )
        return package
    else:
        logger.debug('parse_bazel_file: No package name found in %s', location)
        return None


def extract_name(content):
    """
    Extract the name of the Bazel package from the content.
    """
    pattern = r'(?:^|\n)\s*(package|workspace)\s*\(\s*[^)]*?name\s*=\s*"([^"]+)"'
    match = re.search(pattern, content, flags=re.DOTALL)
    if match:
        name = match.group(2)
        logger.debug('extract_name: Found package name %s', name)
        return name
    else:
        logger.debug('extract_name: No package name found')
    return None


def extract_version(content):
    """
    Extract the version of the Bazel package from the content.
    """
    # Bazel files typically don't include version info. Placeholder for future use
    return None


def extract_dependencies(content):
    """
    Extract dependencies from the Bazel BUILD or WORKSPACE file.
    Return a list of DependentPackage objects.
    """
    dependencies = []
    repo_rules = [
        'http_archive',
        'git_repository',
        'new_git_repository',
        'new_http_archive',
        'maven_jar',
    ]

    repo_pattern = r'(?:^|\n)\s*({})\s*\(\s*(.*?)\)'.format('|'.join(repo_rules))

    for repo_match in re.finditer(repo_pattern, content, flags=re.DOTALL):
        rule_type, rule_content = repo_match.groups()
        dep = parse_repository_rule(rule_type, rule_content)
        if dep:
            dependencies.append(dep)

    logger.debug('extract_dependencies: Found %d dependencies', len(dependencies))
    return dependencies


def parse_repository_rule(rule_type, rule_content):
    """
    Parse a Bazel repository rule and return a DependentPackage object.
    """
    attributes = parse_rule_attributes(rule_content)
    name = attributes.get('name')
    urls = attributes.get('url') or attributes.get('urls')
    if not name or not urls:
        logger.debug('parse_repository_rule: Missing name or url in rule: %s', rule_type)
        return None

    if urls.startswith('['):
        urls_list = re.findall(r'"([^"]+)"', urls)
        url = urls_list[0] if urls_list else None
    else:
        url = urls.strip('"')

    if not url:
        logger.debug('parse_repository_rule: No valid URL found for dependency %s', name)
        return None

    purl = models.PackageURL(type='generic', name=name, download_url=url)

    dependency = models.DependentPackage(
        purl=str(purl),
        scope='dependency',
        is_runtime=True,
        is_optional=False,
        extracted_requirement=rule_type,
    )

    logger.debug('parse_repository_rule: Parsed dependency %s', dependency)
    return dependency


def parse_rule_attributes(rule_content):
    """
    Parse the attributes of a Bazel rule and return a dictionary.
    """
    attributes = {}
    tokens = tokenize_rule_content(rule_content)
    for token in tokens:
        key_value = token.split('=',1)
        if len(key_value) == 2:
            key = key_value[0].strip()
            value = key_value[1].strip()
            attributes[key] = value
    return attributes


def tokenize_rule_content(content):
    """
    Tokenize the content of a Bazel rule into key-value pairs, handling nested structures.
    """
    tokens = []
    current_token = []
    bracket_level = 0
    i = 0
    length = len(content)
    while i < length:
        char = content[i]
        if char == '#':
            while i < length and content[i] != '\n':
                i +=1
            continue
        if char == '/' and i + 1 < length and content[i + 1] == '*':
            i += 2
            while i + 1 < length and not (content[i] == '*' and content[i + 1] == '/'):
                i += 1
            i += 2
            continue
        if char in ('(', '[', '{'):
            bracket_level += 1
        elif char in (')', ']', '}'):
            bracket_level -= 1
        elif char == ',' and bracket_level == 0:
            token = ''.join(current_token).strip()
            if token:
                tokens.append(token)
            current_token = []
            i += 1
            continue
        current_token.append(char)
        i += 1
    if current_token:
        token = ''.join(current_token).strip()
        if token:
            tokens.append(token)
    return tokens
