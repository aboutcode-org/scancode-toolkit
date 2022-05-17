#
# Copyright (c) nexB Inc. and others. All rights reserved.
# ScanCode is a trademark of nexB Inc.
# SPDX-License-Identifier: Apache-2.0
# See http://www.apache.org/licenses/LICENSE-2.0 for the license text.
# See https://github.com/nexB/scancode-toolkit for support or download.
# See https://aboutcode.org for more information about nexB OSS projects.
#

import logging
import os
import posixpath
import sys

import xmltodict
from commoncode import command

from packagedcode import models
from textcode.analysis import as_unicode

TRACE = False
TRACE_DEEP = False


def logger_debug(*args):
    pass


logger = logging.getLogger(__name__)

if TRACE:
    logging.basicConfig(stream=sys.stdout)
    logger.setLevel(logging.DEBUG)

    def logger_debug(*args):
        return logger.debug(' '.join(isinstance(a, str) and a or repr(a) for a in args))


def parse_rpm_xmlish(location, datasource_id, package_type):
    """
    Yield PackageData built from an RPM XML'ish file at ``location``. This is a file
    created with the rpm CLI with the xml query option.
    """
    if not location or not os.path.exists(location):
        return

    # there are smetimes weird encodings. We avoid issues there
    with open(location, 'rb') as f:
        rpms = as_unicode(f.read())

    # The XML'ish format is in fact multiple XML documents, one for each package
    # wrapped in an <rpmHeader> root element. So we add a global root element
    # to make this a valid XML document.

    for rpm_raw_tags in collect_rpms(rpms):
        tags = collect_tags(rpm_raw_tags)
        yield build_package(
            rpm_tags=tags,
            datasource_id=datasource_id,
            package_type=package_type,
        )


def collect_rpms(text):
    """
    Yield lists of RPM raw tags, one list for each RPM from an XML'ish ``text``.

    The XML'ish format is in fact multiple XML documents, one for each package
    wrapped in an <rpmHeader> root element. Therefore, we add a global root
    element to make this a valid XML document before parsing it.

    Each XML document represents one RPM package and has this overall shape:
        <rpmHeader>
        ....
          <rpmTag name="Name"><string>perl-Errno</string></rpmTag>
          <rpmTag name="Version"><string>1.30</string></rpmTag>
        ......
          <rpmTag name="License"><string>GPL+ or Artistic</string></rpmTag>
        ....
          <rpmTag name="Filesizes">
            <integer>6863</integer>
            <integer>2629</integer>
          </rpmTag>
          <rpmTag name="Filemodes">
            <integer>33188</integer>
            <integer>33188</integer>
          </rpmTag>
        ...
        </rpmHeader>

    After wrapping in a top level element we get this shape:
    <rpms>
        <rpmHeader/>
        <rpmHeader/>
    </rpms>

    When parsed with xmltodict we end up with this structure:
    {'rpms':  {'rpmHeader': [
        {'rpmTag': [
            {'@name': 'Name', 'string': 'boost-license1_71_0'},
            {'@name': 'Version', 'string': '1.71.0'},
            {'@name': 'Filesizes', 'integer': ['0', '1338']},
            {'@name': 'Filestates', 'integer': ['0', '0']},
        ]},
        {'rpmTag': [
            {'@name': 'Name', 'string': 'foobar'},
            {'@name': 'Version', 'string': '1.0'},
            ...
        ]},
    }}

    Some of these structures are peculiar as there are parallel lists (for
    instance for files) and each name comes with a type.
    """
    text = f'<rpms>{text}</rpms>'
    parsed = xmltodict.parse(text, dict_constructor=dict)
    rpms = parsed['rpms']['rpmHeader']
    for rpm in rpms:
        yield rpm['rpmTag']


def collect_tags(raw_tags):
    """
    Yield tags as (name, value_type, value) tubles from a ``raw_tags`` list of
    raw RPM tag data.

    """
    for rtag in raw_tags:
        # The format of a raw tag is: ('@name', 'sample'), ('string', 'sample context')
        name = rtag.pop('@name')
        assert len(rtag) == 1
        value_type, value = list(rtag.items())[0]
        yield name, value_type, value


def build_package(rpm_tags, datasource_id, package_type, package_namespace=None):
    """
    Return a PackageData object from an ``rpm_tags`` iterable of (name,
    value_type, value) tuples.
    """

    # mapping of real Package field name -> value converted to expected format
    converted = {
        'datasource_id': datasource_id,
        'type': package_type,
        'namespace': package_namespace
    }

    for name, value_type, value in rpm_tags:
        handler = RPM_TAG_HANDLER_BY_NAME.get(name)
        # FIXME: we need to handle EVRA correctly
        # TODO: add more fields
        # TODO: merge with tag handling in rpm.py
        if handler:
            try:
                handled = handler(value, **converted)
            except Exception as e:
                raise Exception(value, converted) from e
            converted.update(handled)

    package_data = models.PackageData.from_dict(converted)

    if not package_data.license_expression and package_data.declared_license:
        package_data.license_expression = models.compute_normalized_license(package_data.declared_license)

    return package_data

################################################################################
# Each handler function accepts a value and returns a {name: value} mapping
# and handlers MUST accept **kwargs as they also receive the whole current data
# being processed so far as kwargs.

# TODO: process lists in a more explict way
# Most handler do not use it, but parallel list handlers (such as for files) use
# this to process such lists by accumulating data passed around


def name_value_str_handler(name):
    """
    Return a generic handler for plain string fields.
    """

    def handler(value, **kwargs):
        return {name: value}

    return handler


def size_handler(value, **kwargs):
    return {'size': int(value)}


def arch_handler(value, **kwargs):
    """
    Return a Package URL qualifiers for the arch.
    """
    # TODO: should arch={value} be rather a mapping of {arch: value} ?
    return {'qualifiers': f'arch={value}'}


def checksum_handler(value, **kwargs):
    """
    Return a list which contains the a checksum hash.
    """
    return {'current_filerefs': value}


def dir_index_handler(value, **kwargs):
    """
    Return a list of tuples with (dirindexes, md5).
    """
    current_filerefs = kwargs.get('current_filerefs')
    return {'current_filerefs': list(zip(value, current_filerefs))}


def basename_handler(value, **kwargs):
    """
    Return a list of tuples with (dirindexes, md5, basename).
    """
    data = []

    current_filerefs = kwargs.get('current_filerefs') or []
    for index, file in enumerate(current_filerefs):
        basename = (value[index],)
        data.append(file + basename)
    return {'current_filerefs': data}


ALGO_BY_HEX_LEN = {
    32: 'md5',
    40: 'sha1',
    64: 'sha256',
    96: 'sha384',
    128: 'sha512',
}


def infer_digest_algo(digest):
    """
    Given a ``digest`` string, return an inferred digest algorightm.

    We assume hex encoding for now (base64 with or without padding is common these days)

    For example:
    >>> assert infer_digest_algo('acd15e34cce4a29542d98007c7eff6ee') == 'md5'
    """
    return digest and ALGO_BY_HEX_LEN.get(len(digest))


def dirname_handler(value, **kwargs):
    """
    Return a mapping of {'file_references': <list of FileReference dicts>}.
    Update the ``current_filerefs`` found in `kwargs` by adding the correct dir,
    basename and checksum value.
    """
    file_references = []
    current_filerefs = kwargs.get('current_filerefs') or []
    for dirindexes, checksum, basename in current_filerefs:
        dirname = value[int(dirindexes)]
        # TODO: review this. Empty filename does not make sense, unless these
        # are directories that we might ignore OK.

        # There is case where entry of basename is "</string>" which will
        # cause error as None type cannot be used for join.
        # Therefore, we need to convert the None type to empty string
        # in order to make the join works.
        if basename == None:
            basename = ''

        file_reference = models.FileReference(
            path=posixpath.join(dirname, basename),
            # TODO: add size and fileclass as extra data
        )

        # TODO: we could/should use instead the filedigestalgo RPM tag
        algo = infer_digest_algo(checksum)
        if algo:
            setattr(file_reference, algo, checksum)
        file_references.append(file_reference)

    return {'file_references': [fr.to_dict() for fr in file_references]}

#
# Mapping of:
# - the package field name in the installed db XMLis dump,
# - an handler function/callable for this field that implies also a target
#   PackageData field name


RPM_TAG_HANDLER_BY_NAME = {

    ############################################################################
    # per-package fields
    ############################################################################

    'Name': name_value_str_handler('name'),
    # TODO: add these
    #  'Epoch'
    #  'Release' 11.3.2
    'Version': name_value_str_handler('version'),
    'Description': name_value_str_handler('description'),
    'Sha1header': name_value_str_handler('sha1'),
    'Url': name_value_str_handler('homepage_url'),
    'License': name_value_str_handler('declared_license'),
    'Arch':  arch_handler,
    'Size': size_handler,

    # TODO:
    #  'Summary' to combine with description!

    #  'Distribution'
    #     SUSE Linux Enterprise 15
    #     Mariner
    #     (not on Centos 5/6/7)
    #     CentOS (in CentOS 8)
    #     Fedora Project

    #  'Vendor'
    #     SUSE LLC &lt;https://www.suse.com/&gt;
    #     CentOS

    #  'Packager'
    #     https://www.suse.com/
    #     CentOS BuildSystem &lt;http://bugs.centos.org&gt;

    #  'Group' System/Fhs --> keywords
    #  'Os' linux
    #  'Platform' noarch-suse-linux
    #  'Sourcerpm' system-user-root-20190513-3.3.1.src.rpm
    #  'Disturl' in Suse: obs://build.suse.de/SUSE:Maintenance:11304/
    #     SUSE_SLE-15_Update/04b28aa8ff6101d2615ad6d102b6f09b-system-user-root.SUSE_SLE-15_Update

    ############################################################################
    # dependency fields
    ############################################################################
    #  'Requirename' <string>rpmlib(BuiltinLuaScripts)</string>
    #                <string>rpmlib(CompressedFileNames)</string>
    #  'Requireversion' <string>4.2.2-1</string>
    #                   <string>3.0.4-1</string>
    #  'Requireflags'

    #  'Providename' <string>group(root)</string>
    #                <string>group(shadow)</string>
    #  'Provideversion' <string/>
    #                   <string>20190513-3.3.1</string>
    #  'Provideflags'

    #  'Conflictflags'
    #  'Conflictname'
    #  'Conflictversion'

    #  'Obsoleteflags'
    #  'Obsoletename'
    #  'Obsoleteversion'

    ############################################################################
    # per-file fields
    ############################################################################
    # TODO: these two are needed:
    #  'Filesizes' -> useful info
    #  'Filelinktos' -> links!

    #  'Fileflags' -> contains if a file is doc or license
    # <rpmTag name="Fileflags">     <rpmTag name="Basenames">
    #       <integer>0</integer>          <string>libpopt.so.0</string>
    #       <integer>0</integer>          <string>libpopt.so.0.0.0</string>
    #       <integer>0</integer>          <string>popt</string>
    #       <integer>128</integer>        <string>COPYING</string>
    # values:
    #     128: license
    #     2: documentation
    #     0: regular file

    #  'Classdict' -> filetype from "file" libmagic for each file. The position is an index
    #  'Fileclass' -> the position is a fileindex and the value is a classdict index
    # <rpmTag name="Classdict">               <rpmTag name="Basenames">
    #     <string/>                                 <string>libpopt.so.0</string>
    #     <string>ELF 64-bit LSB ..</string>        <string>libpopt.so.0.0.0</string>
    #     <string>directory</string>                <string>popt</string>
    #     <string>ASCII text</string>               <string>COPYING</string>

    'Dirindexes': dir_index_handler,
    'Basenames': basename_handler,
    'Dirnames': dirname_handler,

    'Filedigests': checksum_handler,

    ############################################################################

    ############################################################################
    # TODO: ignored per-package fields. From here on, these fields are not used yet
    ############################################################################
    #  '(unknown)'
    #  'Archivesize'
    #  'Buildhost'
    #  'Buildtime'
    #  'Changelogname' <string>fvogt@suse.com</string> <string>kukuk@suse.de</string>
    #  'Changelogtext' <string>- Add some BuildIgnores for bootstrapping</string> <string>- Add group trusted [bsc#1044014]</string>
    #  'Changelogtime' <integer>1557748800</integer> <integer>1498046400</integer>
    #  'Cookie'
    #  'Dependsdict'
    #  'Dsaheader'
    #  'Filecolors'
    #  'Filecontexts'
    #  'Filedependsn'
    #  'Filedependsx'
    #  'Filedevices'
    #  'Filegroupname'
    #  'Fileinodes'
    #  'Filelangs'
    #  'Filelinktos'
    #  'Filemodes'
    #  'Filemtimes'
    #  'Filerdevs'
    #  'Filestates'
    #  'Fileusername'
    #  'Fileverifyflags'
    #  'Installcolor'
    #  'Installtid'
    #  'Installtime'
    #  'Instprefixes'
    #  'Optflags'
    #  'Payloadcompressor'
    #  'Payloadflags'
    #  'Payloadformat'
    #  'Postin'
    #  'Postinprog'
    #  'Postun'
    #  'Postunprog'
    #  'Prefixes'
    #  'Prein'
    #  'Preinprog']
    #  'Preun'
    #  'Preunprog'
    #  'Rpmversion' 4.14.1
    #  'Sigmd5'
    #  'Sigsize'
    #  'Triggerflags'
    #  'Triggerindex'
    #  'Triggername'
    #  'Triggerscriptprog'
    #  'Triggerscripts'
    #  'Triggerversion'
    #  'Headeri18ntable'
    ############################################################################

}

RPM_BIN_DIR = 'rpm_inspector_rpm.rpm.bindir'


def get_rpm_bin_location():
    """
    Return the binary location for an RPM exe loaded from a plugin-provided path.
    """
    from plugincode.location_provider import get_location
    rpm_bin_dir = get_location(RPM_BIN_DIR)
    if not rpm_bin_dir:
        raise Exception(
            'CRITICAL: RPM executable is not provided. '
            'Unable to continue: you need to install a valid rpm-inspector-rpm '
            'plugin with a valid RPM executable and shared libraries available.'
    )

    return rpm_bin_dir


class InstalledRpmError(Exception):
    pass


def collect_installed_rpmdb_xmlish_from_rootfs(root_dir):
    """
    Return the location of an RPM "XML'ish" inventory file collected from the
    ``root_dir`` rootfs directory or None.

    Raise an InstalledRpmError exception on errors.

    The typical locations of the rpmdb are:

    /var/lib/rpm/
        centos all versions and rpmdb formats
        fedora all versions and rpmdb formats
        openmanidriva all versions and rpmdb formats
        suse/opensuse all versions using bdb rpmdb format

    /usr/lib/sysimage/rpm/ (/var/lib/rpm/ links to /usr/lib/sysimage/rpm)
        suse/opensuse versions that use ndb rpmdb format
    """
    root_dir = os.path.abspath(os.path.expanduser(root_dir))

    rpmdb_loc = os.path.join(root_dir, 'var/lib/rpm')
    if not os.path.exists(rpmdb_loc):
        rpmdb_loc = os.path.join(root_dir, 'usr/lib/sysimage/rpm')
        if not os.path.exists(rpmdb_loc):
            return
    return collect_installed_rpmdb_xmlish_from_rpmdb_loc(rpmdb_loc)


def collect_installed_rpmdb_xmlish_from_rpmdb_loc(rpmdb_loc):
    """
    Return the location of an RPM "XML'ish" inventory file collected from the
    ``rpmdb_loc`` rpmdb directory or None.

    Raise an InstalledRpmError exception on errors.
    """
    rpmdb_loc = os.path.abspath(os.path.expanduser(rpmdb_loc))
    if not os.path.exists(rpmdb_loc):
        return
    rpm_bin_dir = get_rpm_bin_location()

    env = dict(os.environ)
    env['RPM_CONFIGDIR'] = rpm_bin_dir
    env['LD_LIBRARY_PATH'] = rpm_bin_dir

    args = [
        '--query',
        '--all',
        '--qf', '[%{*:xml}\n]',
        '--dbpath', rpmdb_loc,
    ]

    cmd_loc = os.path.join(rpm_bin_dir, 'rpm')
    if TRACE:
        full_cmd = ' '.join([cmd_loc] + args)
        logger_debug(
            f'collect_installed_rpmdb_xmlish_from_rpmdb_loc:\n'
            f'cmd: {full_cmd}')

    rc, stdout_loc, stderr_loc = command.execute(
        cmd_loc=cmd_loc,
        args=args,
        env=env,
        to_files=True,
        log=TRACE,
    )

    if TRACE:
        full_cmd = ' '.join([cmd_loc] + args)
        logger_debug(
            f'collect_installed_rpmdb_xmlish_from_rpmdb_loc:\n'
            f'cmd: {full_cmd}\n'
            f'rc: {rc}\n'
            f'stderr: file://{stderr_loc}\n'
            f'stdout: file://{stdout_loc}\n')

    if rc != 0:
        with open(stderr_loc) as st:
            stde = st.read()
        full_cmd = ' '.join([cmd_loc] + args)
        msg = (
            f'collect_installed_rpmdb_xmlish_from_rpmdb_loc: '
            f'Failed to execute RPM command: {full_cmd}\n{stde}'
        )
        raise Exception(msg)

    return stdout_loc
