"""
originally from
https://raw.githubusercontent.com/rory/camarabuntu/60ed5982bbdf7d342e4f3888a8d59e9169036bea/bin/apt.py
license: cc0-1.0

notes: Rory McCann https://github.com/rory made this available under Public Domain CC0-1.0
 per https://github.com/rory/camarabuntu/issues/1#issuecomment-552501895
 On Mon, Nov 11, 2019 at 4:56 PM Rory McCann wrote this
 > wow this is old! Consider that file under Public Domain (aka CC-zero)
"""

import os, re, commands, copy, urllib, gzip, tempfile, operator

class Dependency():
    def __init__(self, string=None, package_name=None, version=None, relation=None):
        if string is not None:
            depends_re = re.compile( r"(?P<name>\S*) \((?P<relation><<|<=|=|>=|>>) (?P<version>\S*)\)" )
            result = depends_re.search( string )
            if result is None:
                self.name = string
                self.version = None
                self.relation = None
            else:
                self.name = result.group('name')
                self.version = result.group('version')
                self.relation = result.group('relation')
        else:
            self.name = name
            self.version = version
            self.relation = relation

    def __str__(self):
        if self.relation is None and self.version is None:
            return self.name
        else:
            return "%s (%s %s)" % (self.name, self.relation, self.version)

    def __repr__(self):
        return "Dependency( name=%r, version=%r, relation=%r )" % (self.name, self.version, self.relation )

    def __eq__(self, other):
        return self.name == other.name and self.version == other.version and self.relation == other.version

    def __hash__(self):
        return hash((self.name, self.version, self.relation))

class Package():
    def __init__(self, filename=None):
        self.name = None
        self.version = None
        self.depends_line = None
        self.filename = None

        if filename is not None:
            self.__init_from_deb_file(os.path.abspath(filename))

    def __init_from_deb_file(self, filename):
        assert os.path.isfile(filename)

        status, output = commands.getstatusoutput("dpkg-deb --info \"%s\"" % filename)
        if status != 0:
            print output
            return

        for line in output.split("\n"):
            # remove the leading space
            line = line[1:]
            line = line.rstrip()
            if line[0] == " ":
                continue
            bits = line.split(": ", 1)
            if len(bits) != 2:
                continue
            key, value = bits
            if key == "Depends":
                self.parse_dependencies( value )
            if key == "Version":
                self.version_string = value
            if key == "Package":
                self.name = value



    def __str__(self):
        return self.name

    def __repr__(self):
        return str(self)

    def parse_dependencies(self, depends_line):
        depends = []

        # Assuming that "," is more important than "|"
        # and that we ca only nest them 2 deep at most
        packages = depends_line.split( "," )
        for package in packages:
            package = package.strip()
            alts = [ s.strip() for s in package.split("|") ]
            if len(alts) == 1:
                # just a normal package line
                depends.append( Dependency( string = package ) )
            else:
                depends.append( OrDependencyList( *[ Dependency(string=alt) for alt in alts ] ) )

        self.depends = AndDependencyList( *depends )

    def fulfils(self, dep):
        """Returns true iff this package can satify the dependency dep"""
        if dep.name != self.name:
            # Obviously
            return False

        if dep.version is None:
            # for this dependency the version is unimportant
            return True

        # version code from here:
        # http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version
        # TODO debian group is including the 'ubuntu' string
        version_re = re.compile("""
            ((?P<epoch>\d+):)?
            (
                    ( (?P<upstream1>[-0-9.+:]+) - (?P<debian1>[a-zA-Z0-9+.]+) )
                |   ( (?P<upstream2>[0-9.+:]+) ( - (?P<debian2>[a-zA-Z0-9+.]+) )? )
            )
            """, re.VERBOSE )

        match = version_re.match( self.version_string )
        assert match is not None, "The version string for %s (%s) does not match the version regular expression %s" % (self.name, self.version, version_re)

        dep_match = version_re.match( dep.version )
        assert dep_match is not None, "The version string for depenency %s (%s) does not match the version regular expression %r" % (dep, dep.version, version_re )

        relation_to_func = {
            '<<': operator.lt,
            '<=': operator.le,
            '=' : operator.eq,
            '>=': operator.ge,
            '>>': operator.gt
        }

        assert dep.relation in relation_to_func.keys(), "The depenency %s has a relation of %s, which is not in the known relations" % (dep, dep.relation)
        op = relation_to_func[dep.relation]

        assert (match.group('epoch') is None and dep_match.group('epoch') is None) or (match.group('epoch') is not None or dep_match.group('epoch') ), "Exactly one of the version strings %s and %s contain an epoch. Either none or both should include one" % (self.version_string, dep.version )
        if match.group('epoch') is not None:
            # if we provide an epoch we should check it. If not skip it.
            if int(match.group('epoch')) != int(dep_match.group('epoch')):
                return op(int(match.group('epoch')), int(dep_match.group('epoch')))

        pkg_version_dict = match.groupdict()
        if pkg_version_dict['upstream1'] is not None:
            pkg_version_dict['upstream'] = pkg_version_dict['upstream1']
            pkg_version_dict['debian'] = pkg_version_dict['debian1']
        else:
            pkg_version_dict['upstream'] = pkg_version_dict['upstream2']
            pkg_version_dict['debian'] = pkg_version_dict['debian2']
        del pkg_version_dict['upstream1'], pkg_version_dict['upstream2']
        del pkg_version_dict['debian1'], pkg_version_dict['debian2']

        dep_version_dict = dep_match.groupdict()
        if dep_version_dict['upstream1'] is not None:
            dep_version_dict['upstream'] = dep_version_dict['upstream1']
            dep_version_dict['debian'] = dep_version_dict['debian1']
        else:
            dep_version_dict['upstream'] = dep_version_dict['upstream2']
            dep_version_dict['debian'] = dep_version_dict['debian2']
        del dep_version_dict['upstream1'], dep_version_dict['upstream2']
        del dep_version_dict['debian1'], dep_version_dict['debian2']


        # From: http://www.debian.org/doc/debian-policy/ch-controlfields.html#s-f-Version
        # The upstream_version and debian_revision parts are compared by the
        # package management system using the same algorithm:
        
        # The strings are compared from left to right.
        #
        # First the initial part of each string consisting entirely of
        # non-digit characters is determined. These two parts (one of which may
        # be empty) are compared lexically. If a difference is found it is
        # returned. The lexical comparison is a comparison of ASCII values
        # modified so that all the letters sort earlier than all the
        # non-letters.
        #
        # Then the initial part of the remainder of each string which consists
        # entirely of digit characters is determined. The numerical values of
        # these two parts are compared, and any difference found is returned as
        # the result of the comparison. For these purposes an empty string
        # (which can only occur at the end of one or both version strings being
        # compared) counts as zero.
        #
        # These two steps (comparing and removing initial non-digit strings and
        # initial digit strings) are repeated until a difference is found or
        # both strings are exhausted. 



        # Check the upstream version
        pkg_str = pkg_version_dict['upstream']
        dep_str = dep_version_dict['upstream']
        assert pkg_str is not None and dep_str is not None

        digits_non_digits_pkg = [s for s in re.split("(\D*)(\d*)", pkg_str) if s != ""]
        digits_non_digits_dep = [s for s in re.split("(\D*)(\d*)", dep_str) if s != ""]

        smaller_len = min(len(digits_non_digits_dep), len(digits_non_digits_pkg))

        last_check = None
        for index in range(smaller_len):
            try:
                last_check = op( int(digits_non_digits_pkg[index]), int(digits_non_digits_dep[index]) )
            except ValueError:
                last_check = op( digits_non_digits_pkg[index], digits_non_digits_dep[index] )
            if digits_non_digits_pkg[index] != digits_non_digits_dep[index]:
                return last_check

        if pkg_version_dict['debian'] is None or dep_version_dict['debian'] is None:
            return last_check

        # Clean up the debian/ubuntu version numbering
        if re.match( "\d*ubuntu\d*", pkg_version_dict['debian'] ):
            pkg_version_dict['debian'], pkg_version_dict['ubuntu'] = re.split("ubuntu", pkg_version_dict['debian'])
            #print repr(pkg_version_dict)
        if re.match("\d*ubuntu\d*", dep_version_dict['debian'] ):
            dep_version_dict['debian'], dep_version_dict['ubuntu'] = re.split("ubuntu", dep_version_dict['debian'])
            #print repr(dep_version_dict)

        if pkg_version_dict['debian'] != dep_version_dict['debian']:
            # we need to do the same splitting based on digits and non digits for the debian version.
            digits_non_digits_pkg = [s for s in re.split("(\D*)(\d*)", pkg_version_dict['debian']) if s != ""]
            digits_non_digits_dep = [s for s in re.split("(\D*)(\d*)", dep_version_dict['debian']) if s != ""]

            smaller_len = min(len(digits_non_digits_dep), len(digits_non_digits_pkg))

            last_check = None
            for index in range(smaller_len):
                # check if they are different
                try:
                    last_check = op( int(digits_non_digits_pkg[index]), int(digits_non_digits_dep[index]) )
                except ValueError:
                    last_check = op( digits_non_digits_pkg[index], digits_non_digits_dep[index] )
                if digits_non_digits_pkg[index] != digits_non_digits_dep[index]:
                    return last_check

        # if we've gotten to here, then the debian versions are the same, so look at the ubuntu version
        assert pkg_version_dict['debian'] == dep_version_dict['debian'], "When checking debian versions %s and %s, the code got to the 'check ubuntu' version part. This should only happen if the debian versions are the same" % (pkg_version_dict['debian'], dep_version_dict['debian'])

        # check the ubuntu version
        if 'ubuntu' not in dep_version_dict.keys() or dep_version_dict['ubuntu'] is None:
            return last_check
        else:
            return op(int(pkg_version_dict['ubuntu']), int(dep_version_dict['ubuntu']))

        raise NotImplementedError, "The code for comparing versions has finished without returning. This means the author did not fully understand the debian method of comparing versions or this is a funny deb. The deb: %r. The depenency: %r" % (self, dep)


    def save(self, directory=None):
        if directory == None:
            directory = os.getcwd()
        
        assert self.filename is not None, "Attempted to save a package with filename = None"
        assert self.filename[0:7], "Attempted to save a package with a non-http filename. You can't save local packages"
    
        print "Downloading "+str(self)
        urllib.urlretrieve( self.filename, os.path.join( directory, os.path.basename( self.filename ) ) )


class DependencyList():
    def __init__(self, *dependencies):
        self.dependencies = dependencies

    def __iter__(self):
        return self.dependencies.__iter__()
                


class AndDependencyList(DependencyList):
    def __str__(self):
        return ", ".join( [ str(dep) for dep in self.dependencies ] )

    def __repr__(self):
        return "AndDependencyList( %s )" % ", ".join( [ repr(dep) for dep in self.dependencies ] )

class OrDependencyList(DependencyList):
    def __str__(self):
        return " | ".join( [ str(dep) for dep in self.dependencies ] )

    def __repr__(self):
        return "OrDependencyList( %s )" % ", ".join( [ repr(dep) for dep in self.dependencies ] )


class Repository():
    REMOTE_REPOSITORY, LOCAL_REPOSITORY = range(2)
    def __init__(self, uri, download_callback_func=None):
        self.packages = []
        self.type = None
        if os.path.isdir( os.path.abspath( uri ) ):
            self.type = Repository.LOCAL_REPOSITORY
            self.path = os.path.abspath( uri )
            self.__scan_local_packages()
        elif uri[0:7] == "http://":
            self.type = Repository.REMOTE_REPOSITORY
            self.url = uri
            self.url, self.dist, self.component = uri.split( " " )
            self.__scan_remote_packages(download_callback_func=download_callback_func)

    def __scan_remote_packages(self, download_callback_func=None):
        # check for the repo file
        tmpfile_fp, tmpfile = tempfile.mkstemp(suffix=".gz", prefix="web-repo-")
        urllib.urlretrieve( self.url+ "/dists/" + self.dist + "/" +self.component + "/binary-i386/Packages.gz", filename=tmpfile, reporthook=download_callback_func )
        self.__scan_packages( gzip.open( tmpfile ) )
        
    
    def __scan_packages(self, releases_fp):
        package = Package()
        self.packages = []
        for line in releases_fp:
            line = line.rstrip("\n")
            if line == "":
                self.packages.append(package)
                package = Package()
                continue
            if line[0] == " ":
                continue
            bits = line.split(": ", 1)
            if len(bits) != 2:
                continue
            key, value = bits
            maps = [ [ 'Package', 'name' ],
                     [ 'Version', 'version_string' ],
                     [ 'Filename', 'filename' ],
                     ]
            for key_name, attr in maps:
                if key == key_name:
                    setattr( package, attr, value )
            if key == 'Depends':
                package.parse_dependencies( value )
            if key == 'Filename':
                if self.type == Repository.LOCAL_REPOSITORY:
                    package.filename = os.path.abspath( self.path + "/" + value )
                elif self.type == Repository.REMOTE_REPOSITORY:
                    package.filename = self.url + "/" + value



    def __scan_local_packages(self):
        package = Package()
        self.packages = []
        self.__scan_packages( open( self.path + "/binary-i386/Packages" ) )

    def __contains__(self, package):
        if isinstance(package, str):
            # looking for package name
            pass
        elif isinstance(package, Package):
            # looking for an actual package
            return package in self.dependencies
        elif isinstance( package, Dependency ):
            # looking for a version
            possibilities = [ dep for dep in self.dependencies if deb.name == package.name ]
            print repr( possibilities )

    def __getitem__(self, package_name):
        assert self.packages is not None and len(self.packages) > 0, "The repository %s has no packages, and attempted to get a package from it" % self
        for pkg in self.packages:
            if pkg.name == package_name:
                return pkg
        return None

    def __str__(self):
        print "self.type = " + self.type
        if self.type == Repository.LOCAL_REPOSITORY:
            return "\"file://" + os.abspath( self.path ) + "\""
        elif self.type == Repository.REMOTE_REPOSITORY:
            return "%s %s %s" % (self.url, self.dist, self.component)
        


def dl_depenencies(packages, local_repos, remote_repos, directory):
    debs_to_download = set()
    unmet_dependencies = set()

    for package in packages:

        if isinstance(package, str):
            # deb is a package name
            options = [r for r in local_repos if r[package] is not None]
            assert len(options) <= 1, "More than one local repository has the packages %s, don't know what to do" % packages
            if len(options) == 0:
                # not found locally, try looking remotely

                remote_options = [r for r in remote_repos if r[package] is not None]
                
                assert len(remote_options) != 0, "package %s is not available in local or remote repositories" % package
                assert len(remote_options) == 1, "more than one option to download from, there should be only one"
                
                package = remote_options[0][package]
                debs_to_download.add(package)
            else:
                package = options[0][package]


        assert isinstance(package, Package)

        # Start off with all our depends. We have to keep going until we this
        # is empty.
        unfulfiled = set(package.depends)
        fulfiled_deps = set()


        while len(unfulfiled) > 0:
            dependency = unfulfiled.pop()
            #print "Looking at dependency %s" % dependency

            fulfiled_locally = False

            for repo in local_repos:
                if fulfiled_locally:
                    break
                for package in repo.packages:
                    if fulfiled_locally:
                        break
                    if isinstance( dependency, OrDependencyList ):
                        if any([package.fulfils(dep) for dep in dependency] ):
                            #print "package %s fulfils the dependency %s, which is part of %s" % (package, dep, dependency)
                            fulfiled_locally = True
                            break
                    else:
                        if package.fulfils(dependency):
                            #print "package %s fulfils the dependency %s" % (package, dependency)
                            fulfiled_locally = True
                            break

            if fulfiled_locally:
                # Don't bother looking at the remote repositories if we can already fulfill locally
                #print "The dependency %s can be fulfilled locally" % dependency
                continue # to the next package

            # check if one of the debs we're going to download will fulfil this repository. Can help with cycles
            if any([deb.fulfils(dependency) for deb in debs_to_download]):
                #print "The dependency %s will be fulfilled by one of the debs we are going to download" % dependency
                continue # to next dependency

            # we know we need to look on the web for this dependency

            fulfiled_remotely = False
            remote_repo = None
            for repo in remote_repos:
                if fulfiled_remotely:
                    break
                for package in repo.packages:
                    if fulfiled_remotely:
                        break
                    if isinstance( dependency, OrDependencyList ):
                        if any([package.fulfils(dep) for dep in dependency] ):
                            debs_to_download.add(package)
                            fulfiled_remotely = True
                            remote_repo = repo
                            break
                    else:
                        if package.fulfils(dependency):
                            debs_to_download.add(package)
                            fulfiled_remotely = True
                            remote_repo = repo
                            break
            
            #if fulfiled_remotely:
                #print "The dependency %s can be fulfilled from the %s repository" % (dependency, remote_repo)

            if not fulfiled_remotely and not fulfiled_locally:
                print "Warning the dependency %s cannot be fulfilled remotely or locally. Try adding extra repositories" % dependency
                unmet_dependencies.add(dependency)


    print "The following packages need to be downloaded: "+", ".join([str(x) for x in debs_to_download])

    # now download our debs
    for deb in debs_to_download:
        deb.save(directory)

    if len(unmet_dependencies) > 0:
        print "Warning: the following dependencies could not be met:"
        print ", ".join([str(x) for x in unmet_dependencies])
        print "Please add extra repositories"
