# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import json
import re

from debian_inspector.debcon import get_paragraphs_data_from_file
from packageurl import PackageURL

from packagedcode import models
from packagedcode.utils import build_description
from packagedcode.utils import parse_maintainer_name_email

VERSION_FIELDS = (
    "version",
    "version-semver",
    "version-date",
    "version-string",
)

SOURCE_MACROS = {
    "vcpkg_download_distfile",
    "vcpkg_download_sourceforge",
    "vcpkg_from_bitbucket",
    "vcpkg_from_git",
    "vcpkg_from_github",
    "vcpkg_from_gitlab",
    "vcpkg_from_sourceforge",
}

CMAKE_KEYWORDS = {
    "ALWAYS_REDOWNLOAD",
    "AUTHORIZATION_TOKEN",
    "FETCH_REF",
    "FILE_DISAMBIGUATOR",
    "FILENAME",
    "GITHUB_HOST",
    "GITLAB_URL",
    "HEADERS",
    "HEAD_REF",
    "LFS",
    "NO_REMOVE_ONE_LEVEL",
    "OUT_SOURCE_PATH",
    "PATCHES",
    "QUIET",
    "REF",
    "REPO",
    "SHA512",
    "SKIP_SHA512",
    "URL",
    "URLS",
    "USE_TARBALL_API",
    "WORKING_DIRECTORY",
}


class BaseVcpkgHandler(models.DatafileHandler):
    default_package_type = "vcpkg"
    default_primary_language = "C++"

    @classmethod
    def assemble(
        cls,
        package_data,
        resource,
        codebase,
        package_adder=models.add_to_package,
    ):
        """
        Assemble one vcpkg package from a manifest and its sibling portfile.
        """
        if resource.has_parent():
            directory = resource.parent(codebase)
        else:
            directory = resource

        if codebase.has_single_resource:
            siblings = [resource]
        else:
            siblings = list(directory.children(codebase))

        package_data_by_name = {}
        resource_by_name = {}
        for sibling in siblings:
            if sibling.name not in ("vcpkg.json", "CONTROL", "portfile.cmake"):
                continue

            resource_by_name[sibling.name] = sibling
            if sibling.package_data:
                package_data_by_name[sibling.name] = models.PackageData.from_dict(
                    sibling.package_data[0]
                )
            elif sibling.path == resource.path:
                package_data_by_name[sibling.name] = package_data

        identity_name = None
        if "vcpkg.json" in package_data_by_name:
            identity_name = "vcpkg.json"
        elif "CONTROL" in package_data_by_name:
            identity_name = "CONTROL"

        identity = package_data_by_name.get(identity_name)
        identity_resource = resource_by_name.get(identity_name)
        portfile = package_data_by_name.get("portfile.cmake")
        portfile_resource = resource_by_name.get("portfile.cmake")

        package = None
        package_uid = None
        if identity:
            assembled = models.PackageData.from_dict(identity.to_dict())
            if portfile:
                enrich_package_data(assembled, portfile)

            if assembled.purl:
                package = models.Package.from_package_data(
                    package_data=assembled,
                    datafile_path=identity_resource.path,
                )
                if portfile_resource:
                    package.datafile_paths.append(portfile_resource.path)
                    package.datasource_ids.append(portfile.datasource_id)

                package.populate_license_fields()
                package_uid = package.package_uid
                yield package

                cls.assign_package_to_parent_tree(
                    package=package,
                    resource=identity_resource,
                    codebase=codebase,
                    package_adder=package_adder,
                )

            if assembled.dependencies:
                yield from models.Dependency.from_dependent_packages(
                    dependent_packages=assembled.dependencies,
                    datafile_path=identity_resource.path,
                    datasource_id=identity.datasource_id,
                    package_uid=package_uid,
                )

        for sibling in resource_by_name.values():
            yield sibling


class VcpkgJsonHandler(BaseVcpkgHandler):
    datasource_id = "vcpkg_json"
    path_patterns = ("*/vcpkg.json",)
    description = "vcpkg JSON manifest"
    documentation_url = "https://learn.microsoft.com/vcpkg/reference/vcpkg-json"

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as manifest_file:
            manifest = json.load(manifest_file)

        if not isinstance(manifest, dict):
            return

        version, version_data = get_version_data(manifest)
        qualifiers, port_version_data = get_port_version_data(manifest)
        extra_data = dict(version_data)
        extra_data.update(port_version_data)

        for field_name in (
            "$schema",
            "builtin-baseline",
            "configuration",
            "default-features",
            "documentation",
            "overrides",
            "supports",
            "vcpkg-configuration",
        ):
            if field_name in manifest:
                extra_data[field_name] = manifest[field_name]

        dependencies = get_json_dependencies(manifest.get("dependencies"))
        features_data = {}
        features = manifest.get("features") or {}
        if not isinstance(features, dict):
            features = {}
        for feature_name, feature in features.items():
            if not isinstance(feature, dict):
                continue

            feature_data = {
                key: feature[key]
                for key in ("description", "supports")
                if key in feature
            }
            if feature_data:
                features_data[feature_name] = feature_data

            dependencies.extend(
                get_json_dependencies(
                    dependencies=feature.get("dependencies"),
                    scope=f"feature:{feature_name}",
                    is_optional=True,
                )
            )

        if features_data:
            extra_data["features"] = features_data

        description = manifest.get("description")
        if isinstance(description, list):
            description = "\n".join(str(line) for line in description if line)
        elif not isinstance(description, str):
            description = None

        name = manifest.get("name")
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            name=name,
            version=version,
            qualifiers=qualifiers,
            description=build_description(summary=None, description=description),
            parties=get_maintainers(manifest.get("maintainers")),
            homepage_url=manifest.get("homepage"),
            extracted_license_statement=manifest.get("license"),
            is_private=not bool(name),
            dependencies=dependencies,
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(package_data, package_only)


class VcpkgControlHandler(BaseVcpkgHandler):
    """
    Parse a classic vcpkg CONTROL file, including optional feature paragraphs.
    """

    datasource_id = "vcpkg_control"
    path_patterns = ("*/CONTROL",)
    description = "vcpkg CONTROL manifest"
    documentation_url = "https://learn.microsoft.com/vcpkg/maintainers/control-files"

    @classmethod
    def is_datafile(cls, location, filetypes=tuple(), _bare_filename=False):
        if not super().is_datafile(
            location,
            filetypes=filetypes,
            _bare_filename=_bare_filename,
        ):
            return False

        if _bare_filename:
            return True

        with io.open(location, encoding="utf-8", errors="replace") as control_file:
            content = control_file.read(65536)

        # Source, Version, and Description are required by the legacy vcpkg format.
        return all(
            re.search(rf"(?m)^{field}:[ \t]*\S", content)
            for field in ("Source", "Version", "Description")
        )

    @classmethod
    def parse(cls, location, package_only=False):
        paragraphs = list(get_paragraphs_data_from_file(location=location))
        if not paragraphs:
            return

        control = paragraphs[0]
        qualifiers, port_version_data = get_port_version_data(control)
        extra_data = dict(port_version_data)
        for field_name in ("default-features", "supports"):
            if field_name in control:
                extra_data[field_name] = control[field_name]

        dependencies = get_control_dependencies(control.get("build-depends"))
        features_data = {}
        for feature in paragraphs[1:]:
            feature_name = feature.get("feature")
            if not feature_name:
                continue

            feature_data = {
                key: feature[key]
                for key in ("description", "supports")
                if key in feature
            }
            if feature_data:
                features_data[feature_name] = feature_data

            dependencies.extend(
                get_control_dependencies(
                    build_depends=feature.get("build-depends"),
                    scope=f"feature:{feature_name}",
                    is_optional=True,
                )
            )

        if features_data:
            extra_data["features"] = features_data

        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            name=control.get("source"),
            version=control.get("version"),
            qualifiers=qualifiers,
            homepage_url=control.get("homepage"),
            description=build_description(
                summary=None,
                description=control.get("description"),
            ),
            extracted_license_statement=control.get("license"),
            dependencies=dependencies,
            extra_data=extra_data,
        )
        yield models.PackageData.from_data(package_data, package_only)


class VcpkgPortfileHandler(BaseVcpkgHandler):
    datasource_id = "vcpkg_portfile"
    path_patterns = ("*/portfile.cmake",)
    description = "vcpkg CMake portfile"
    documentation_url = "https://learn.microsoft.com/vcpkg/concepts/ports"

    @classmethod
    def parse(cls, location, package_only=False):
        with io.open(location, encoding="utf-8") as portfile:
            content = portfile.read()

        source_data = get_source_data(content)
        package_data = dict(
            datasource_id=cls.datasource_id,
            type=cls.default_package_type,
            primary_language=cls.default_primary_language,
            namespace=None,
            download_url=source_data.get("download_url"),
            vcs_url=source_data.get("vcs_url"),
            sha512=source_data.get("sha512"),
            extra_data={"sources": source_data.get("sources", [])},
        )
        yield models.PackageData.from_data(package_data, package_only)


def get_version_data(manifest):
    versions = {
        field_name: manifest[field_name]
        for field_name in VERSION_FIELDS
        if manifest.get(field_name) is not None
    }
    if not versions:
        return None, {}

    version_scheme = next(
        field_name for field_name in VERSION_FIELDS if field_name in versions
    )
    extra_data = {"version_scheme": version_scheme}
    if len(versions) > 1:
        extra_data["version_fields"] = versions
    return str(versions[version_scheme]), extra_data


def get_port_version_data(data):
    if "port-version" not in data:
        return {}, {}

    port_version = data.get("port-version")
    extra_data = {"port_version": port_version}
    try:
        is_revision = not isinstance(port_version, bool) and int(port_version) > 0
    except (TypeError, ValueError):
        is_revision = False

    qualifiers = {"port_version": str(port_version)} if is_revision else {}
    return qualifiers, extra_data


def get_maintainers(maintainers):
    if isinstance(maintainers, str):
        maintainers = [maintainers]
    elif not isinstance(maintainers, (list, tuple)):
        maintainers = []

    parties = []
    for maintainer in maintainers or []:
        if not isinstance(maintainer, str) or not maintainer.strip():
            continue

        name, email = parse_maintainer_name_email(maintainer.strip())
        parties.append(
            models.Party(
                type=models.party_person,
                role="maintainer",
                name=name,
                email=email,
            )
        )
    return parties


def get_json_dependencies(dependencies, scope="dependencies", is_optional=False):
    if not isinstance(dependencies, (list, tuple)):
        return []

    dependent_packages = []
    for dependency in dependencies or []:
        if isinstance(dependency, str):
            name = dependency
            dependency_data = {}
        elif isinstance(dependency, dict):
            name = dependency.get("name")
            dependency_data = {
                field_name: dependency[field_name]
                for field_name in ("features", "default-features", "platform", "host")
                if field_name in dependency
            }
        else:
            continue

        if not isinstance(name, str) or not name.strip():
            continue

        name = name.strip()
        minimum_version = (
            dependency.get("version>=") if isinstance(dependency, dict) else None
        )
        extracted_requirement = f">= {minimum_version}" if minimum_version else None
        is_host = dependency_data.get("host") is True
        dependency_scope = scope
        if is_host and scope == "dependencies":
            dependency_scope = "host"

        purl = PackageURL(type="vcpkg", name=name)
        dependent_packages.append(
            models.DependentPackage(
                purl=purl.to_string(),
                extracted_requirement=extracted_requirement,
                scope=dependency_scope,
                is_runtime=not is_host,
                is_optional=is_optional,
                is_pinned=False,
                extra_data=dependency_data,
            )
        )
    return dependent_packages


def split_control_dependencies(build_depends):
    """
    Return comma-separated dependency entries without splitting nested syntax.
    """
    entries = []
    start = 0
    square_depth = 0
    parenthesis_depth = 0
    for index, character in enumerate(build_depends or ""):
        if character == "[":
            square_depth += 1
        elif character == "]" and square_depth:
            square_depth -= 1
        elif character == "(":
            parenthesis_depth += 1
        elif character == ")" and parenthesis_depth:
            parenthesis_depth -= 1
        elif character == "," and not square_depth and not parenthesis_depth:
            entry = build_depends[start:index].strip()
            if entry:
                entries.append(entry)
            start = index + 1

    entry = (build_depends or "")[start:].strip()
    if entry:
        entries.append(entry)
    return entries


CONTROL_DEPENDENCY_PATTERN = re.compile(
    r"^(?P<name>[a-z0-9][a-z0-9-]*)"
    r"(?:\[(?P<features>[^]]*)\])?"
    r"(?:\s*\((?P<platform>.*)\))?$",
    re.IGNORECASE,
)


def get_control_dependencies(build_depends, scope="dependencies", is_optional=False):
    dependencies = []
    for entry in split_control_dependencies(build_depends):
        match = CONTROL_DEPENDENCY_PATTERN.match(entry)
        if not match:
            continue

        name = match.group("name")
        extra_data = {}
        features = match.group("features")
        if features is not None:
            extra_data["features"] = [
                feature.strip() for feature in features.split(",") if feature.strip()
            ]
        platform = match.group("platform")
        if platform is not None:
            extra_data["platform"] = platform.strip()

        purl = PackageURL(type="vcpkg", name=name)
        dependencies.append(
            models.DependentPackage(
                purl=purl.to_string(),
                scope=scope,
                is_runtime=True,
                is_optional=is_optional,
                extra_data=extra_data,
            )
        )
    return dependencies


def get_source_data(content):
    """
    Return safe literal source data from supported vcpkg CMake calls.
    """
    sources = []
    for macro, body in get_cmake_calls(content):
        arguments = get_cmake_arguments(body)
        source = build_source(macro, arguments)
        if source:
            sources.append(source)

    source_data = {"sources": sources}
    primary = next(
        (
            source
            for source in sources
            if source.get("download_url") or source.get("vcs_url")
        ),
        None,
    )
    if primary:
        for field_name in ("download_url", "vcs_url", "sha512"):
            if primary.get(field_name):
                source_data[field_name] = primary[field_name]
    return source_data


def get_cmake_calls(content):
    """
    Yield supported CMake macro names and their balanced argument bodies.
    """
    index = 0
    length = len(content)
    while index < length:
        character = content[index]
        if character == "#":
            index = skip_line_comment(content, index)
            continue
        if character == '"':
            index = skip_quoted(content, index)
            continue

        bracket_end = get_bracket_end(content, index)
        if bracket_end is not None:
            index = bracket_end
            continue

        if not (character.isalpha() or character == "_"):
            index += 1
            continue

        identifier_start = index
        index += 1
        while index < length and (content[index].isalnum() or content[index] == "_"):
            index += 1

        macro = content[identifier_start:index].lower()
        if macro not in SOURCE_MACROS:
            continue

        call_start = skip_cmake_space(content, index)
        if call_start >= length or content[call_start] != "(":
            continue

        body, index = read_cmake_call(content, call_start)
        if body is not None:
            yield macro, body


def read_cmake_call(content, opening_parenthesis):
    depth = 1
    index = opening_parenthesis + 1
    body_start = index
    while index < len(content):
        character = content[index]
        if character == "#":
            index = skip_line_comment(content, index)
            continue
        if character == '"':
            index = skip_quoted(content, index)
            continue

        bracket_end = get_bracket_end(content, index)
        if bracket_end is not None:
            index = bracket_end
            continue

        if character == "(":
            depth += 1
        elif character == ")":
            depth -= 1
            if not depth:
                return content[body_start:index], index + 1
        index += 1
    return None, len(content)


def skip_line_comment(content, index):
    bracket_end = get_bracket_end(content, index + 1)
    if bracket_end is not None:
        return bracket_end

    newline = content.find("\n", index)
    return len(content) if newline == -1 else newline + 1


def skip_quoted(content, index):
    index += 1
    while index < len(content):
        if content[index] == "\\":
            index += 2
        elif content[index] == '"':
            return index + 1
        else:
            index += 1
    return len(content)


BRACKET_OPENING_PATTERN = re.compile(r"\[(?P<equals>=*)\[")


def get_bracket_end(content, index):
    match = BRACKET_OPENING_PATTERN.match(content, index)
    if not match:
        return

    closing = f"]{match.group('equals')}]"
    end = content.find(closing, match.end())
    return len(content) if end == -1 else end + len(closing)


def skip_cmake_space(content, index):
    while index < len(content):
        if content[index].isspace():
            index += 1
        elif content[index] == "#":
            index = skip_line_comment(content, index)
        else:
            break
    return index


def tokenize_cmake_arguments(body):
    tokens = []
    index = 0
    while index < len(body):
        index = skip_cmake_space(body, index)
        if index >= len(body):
            break

        if body[index] == '"':
            value = []
            index += 1
            while index < len(body):
                if body[index] == "\\" and index + 1 < len(body):
                    value.append(body[index + 1])
                    index += 2
                elif body[index] == '"':
                    index += 1
                    break
                else:
                    value.append(body[index])
                    index += 1
            tokens.append("".join(value))
            continue

        bracket_match = BRACKET_OPENING_PATTERN.match(body, index)
        if bracket_match:
            closing = f"]{bracket_match.group('equals')}]"
            end = body.find(closing, bracket_match.end())
            if end == -1:
                tokens.append(body[bracket_match.end() :])
                break
            tokens.append(body[bracket_match.end() : end])
            index = end + len(closing)
            continue

        start = index
        while index < len(body) and not body[index].isspace() and body[index] != "#":
            index += 1
        if start != index:
            tokens.append(body[start:index])
        if index < len(body) and body[index] == "#":
            index = skip_line_comment(body, index)
    return tokens


def get_cmake_arguments(body):
    arguments = {}
    current_keyword = None
    for token in tokenize_cmake_arguments(body):
        if token in CMAKE_KEYWORDS:
            current_keyword = token
            arguments.setdefault(token, [])
        elif current_keyword:
            arguments[current_keyword].append(token)
    return arguments


def get_literal_values(arguments, name):
    values = []
    for value in arguments.get(name, []):
        for item in value.split(";"):
            item = item.strip()
            if item and "$" not in item:
                values.append(item)
    return values


def get_literal_value(arguments, name):
    values = get_literal_values(arguments, name)
    return values[0] if values else None


def build_source(macro, arguments):
    repository = get_literal_value(arguments, "REPO")
    reference = get_literal_value(arguments, "REF")
    sha512 = get_literal_value(arguments, "SHA512")
    filename = get_literal_value(arguments, "FILENAME")
    urls = get_literal_values(arguments, "URLS")

    source = {"macro": macro}
    if repository:
        source["repository"] = repository
    if reference:
        source["reference"] = reference
    if sha512:
        source["sha512"] = sha512
    if filename:
        source["filename"] = filename
    if macro == "vcpkg_download_distfile" and urls:
        source["urls"] = urls
        source["download_url"] = urls[0]

    if macro == "vcpkg_from_github" and repository:
        host = get_literal_value(arguments, "GITHUB_HOST") or "https://github.com"
        repository_url = f"{host.rstrip('/')}/{repository.lstrip('/')}"
        source["vcs_url"] = get_versioned_vcs_url(repository_url, reference)
        if reference:
            source["download_url"] = f"{repository_url}/archive/{reference}.tar.gz"

    elif macro == "vcpkg_from_gitlab" and repository:
        host = get_literal_value(arguments, "GITLAB_URL") or "https://gitlab.com"
        repository_url = f"{host.rstrip('/')}/{repository.lstrip('/')}"
        source["vcs_url"] = get_versioned_vcs_url(repository_url, reference)
        if reference:
            project = repository.rstrip("/").rsplit("/", 1)[-1]
            source["download_url"] = (
                f"{repository_url}/-/archive/{reference}/{project}-{reference}.tar.gz"
            )

    elif macro == "vcpkg_from_bitbucket" and repository:
        repository_url = f"https://bitbucket.org/{repository.lstrip('/')}"
        source["vcs_url"] = get_versioned_vcs_url(repository_url, reference)
        if reference:
            source["download_url"] = f"{repository_url}/get/{reference}.tar.gz"

    elif macro == "vcpkg_from_git":
        url = get_literal_value(arguments, "URL")
        if url:
            source["url"] = url
            source["vcs_url"] = get_versioned_vcs_url(url, reference)

    elif macro in ("vcpkg_from_sourceforge", "vcpkg_download_sourceforge"):
        sourceforge_url = get_sourceforge_url(repository, reference, filename)
        if sourceforge_url:
            source["download_url"] = sourceforge_url

    if len(source) == 1:
        return
    return source


def get_versioned_vcs_url(url, reference):
    url = url.rstrip("/")
    if not url.endswith(".git"):
        url = f"{url}.git"
    return f"{url}@{reference}" if reference else url


def get_sourceforge_url(repository, reference, filename):
    if not repository or not filename:
        return

    project, _, path = repository.partition("/")
    parts = [path, reference, filename]
    source_path = "/".join(part.strip("/") for part in parts if part)
    return f"https://sourceforge.net/projects/{project}/files/{source_path}/download"


def enrich_package_data(package_data, portfile_data):
    for field_name in ("download_url", "vcs_url", "sha512"):
        if not getattr(package_data, field_name) and getattr(portfile_data, field_name):
            setattr(package_data, field_name, getattr(portfile_data, field_name))

    sources = portfile_data.extra_data.get("sources")
    if sources:
        package_data.extra_data.setdefault("sources", []).extend(sources)
