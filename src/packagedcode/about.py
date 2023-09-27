#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import io
import os
from pathlib import Path

import saneyaml

from packagedcode import models
from packageurl import PackageURL

# TODO: Override get_package_resource so it returns the Resource that the ABOUT file is describing

TRACE = os.environ.get('SCANCODE_DEBUG_PACKAGE', False)


def logger_debug(*args):
    pass


if TRACE:
    import logging
    import sys

    logger = logging.getLogger(__name__)
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(
            ' '.join(isinstance(a, str) and a or repr(a) for a in args)
        )


class AboutFileHandler(models.DatafileHandler):
    datasource_id = 'about_file'
    default_package_type = 'about'
    path_patterns = ('*.ABOUT',)
    description = 'AboutCode ABOUT file'
    documentation_url = 'https://aboutcode-toolkit.readthedocs.io/en/latest/specification.html'

    @classmethod
    def parse(cls, location, purl_only=False):
        """
        Yield one or more Package manifest objects given a file ``location`` pointing to a
        package archive, manifest or similar.
        """
        with io.open(location, encoding='utf-8') as loc:
            package_data = saneyaml.load(loc.read())

        # About files can contain any purl and also have a namespace
        about_type = package_data.get('type')
        about_ns = package_data.get('namespace')
        purl_type = None
        purl_ns = None
        purl = package_data.get('purl')
        if purl:
            purl = PackageURL.from_string(purl)
            if purl:
                purl_type = purl.type

        package_type = about_type or purl_type or cls.default_package_type
        package_ns = about_ns or purl_ns

        name = package_data.get('name')
        version = package_data.get('version')
        if purl_only:
            yield models.PackageData(
                datasource_id=cls.datasource_id,
                type=package_type,
                namespace=package_ns,
                name=name,
                version=version,
            )
            return

        homepage_url = package_data.get('home_url') or package_data.get('homepage_url')
        download_url = package_data.get('download_url')
        copyright_statement = package_data.get('copyright')

        declared_license_expression = package_data.get('license_expression')

        owner = package_data.get('owner')
        if not isinstance(owner, str):
            owner = repr(owner)
        parties = [models.Party(type=models.party_person, name=owner, role='owner')]

        # FIXME: also include notice_file and license_file(s) as file_references
        file_references = []
        about_resource = package_data.get('about_resource')
        if about_resource:
            file_references.append(models.FileReference(path=about_resource))

        # FIXME: we should put the unprocessed attributes in extra data
        yield models.PackageData(
            datasource_id=cls.datasource_id,
            type=package_type,
            namespace=package_ns,
            name=name,
            version=version,
            extracted_license_statement=declared_license_expression,
            copyright=copyright_statement,
            parties=parties,
            homepage_url=homepage_url,
            download_url=download_url,
            file_references=file_references,
        )

    @classmethod
    def assemble(cls, package_data, resource, codebase, package_adder):
        """
        Yield a Package. Note that ABOUT files do not carry dependencies.
        """
        datafile_path = resource.path
        # do we have enough to create a package?
        if package_data.purl:
            package = models.Package.from_package_data(
                package_data=package_data,
                datafile_path=datafile_path,
            )

            package.populate_license_fields()

            yield package

            package_uid = package.package_uid
            # NOTE: we do not attach files to the Package level. Instead we
            # update `for_package` in the file
            package_adder(package_uid, resource, codebase)

            if resource.has_parent() and package_data.file_references:
                parent_resource = resource.parent(codebase)
                if parent_resource and package_data.file_references:
                    root_path = Path(parent_resource.path)

                    # FIXME: we should be able to get the path relatively to the
                    # ABOUT file resource a file ref extends from the root of
                    # the filesystem
                    file_references_by_path = {
                        str(root_path / ref.path): ref
                        for ref in package.file_references
                    }

                    for res in parent_resource.walk(codebase):
                        ref = file_references_by_path.get(res.path)
                        if not ref:
                            continue

                        # path is found and processed: remove it, so we can
                        # check if we found all of them
                        del file_references_by_path[res.path]
                        package_adder(package_uid, res, codebase)

                        yield res

                # if we have left over file references, add these to extra data
                if file_references_by_path:
                    missing = sorted(file_references_by_path.values(), key=lambda r: r.path)
                    package.extra_data['missing_file_references'] = missing
            else:
                package.extra_data['missing_file_references'] = package_data.file_references[:]

        # we yield this as we do not want this further processed
        yield resource
