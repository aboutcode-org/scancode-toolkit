%define nspr_name	    nspr
%define nss_name	    nss
%define mozldap_name	mozldap

Summary: LDAP Perl module that wraps the Mozilla C SDK
Name: perl-Mozilla-LDAP
Version: 1.5.2
Release: 4%{?dist}
License: MPL/GPL/LGPL
Group: Development/Libraries
URL: http://www.mozilla.org/directory/perldap.html
BuildRoot: %{_tmppath}/%{name}-%{version}-%{release}-root
BuildRequires: perl >= 2:5.8.0
Requires: %(perl -MConfig -le 'if (defined $Config{useithreads}) { print "perl(:WITH_ITHREADS)" } else { print "perl(:WITHOUT_ITHREADS)" }')
Requires: %(perl -MConfig -le 'if (defined $Config{usethreads}) { print "perl(:WITH_THREADS)" } else { print "perl(:WITHOUT_THREADS)" }')
Requires: %(perl -MConfig -le 'if (defined $Config{uselargefiles}) { print "perl(:WITH_LARGEFILES)" } else { print "perl(:WITHOUT_LARGEFILES)" }')
Requires: %{nspr_name} >= 4.6
Requires: %{nss_name} >= 3.11
Requires: %{mozldap_name} >= 6.0
BuildRequires: %{nspr_name}-devel >= 4.6
BuildRequires: %{nss_name}-devel >= 3.11
BuildRequires: %{mozldap_name}-devel >= 6.0
Source0: ftp://ftp.mozilla.org/pub/mozilla.org/directory/perldap/releases/1.5/perl-mozldap-%{version}.tar.gz
Source1: ftp://ftp.mozilla.org/pub/mozilla.org/directory/perldap/releases/1.5/Makefile.PL.rpm

%description
%{summary}.

%prep
%setup -q -n perl-mozldap-%{version}

%build

LDAPPKGNAME=%{mozldap_name} CFLAGS="$RPM_OPT_FLAGS" perl %{SOURCE1} PREFIX=$RPM_BUILD_ROOT%{_prefix} INSTALLDIRS=vendor < /dev/null
make OPTIMIZE="$RPM_OPT_FLAGS" CFLAGS="$RPM_OPT_FLAGS" 
make test

%install
rm -rf $RPM_BUILD_ROOT
eval `perl '-V:installarchlib'`

%makeinstall
# remove files we don't want to package
rm -f `find $RPM_BUILD_ROOT -type f -name perllocal.pod -o -name .packlist`
find $RPM_BUILD_ROOT -name API.bs -a -size 0 -exec rm -f {} \;

# make sure shared lib is correct mode
find $RPM_BUILD_ROOT -name API.so -exec chmod 755 {} \;

if [ -x /usr/lib/rpm/brp-compress ] ; then
    /usr/lib/rpm/brp-compress
elif [ -x %{_libdir}/rpm/brp-compress ] ; then
    %{_libdir}/rpm/brp-compress
fi

# make sure files refer to %{_prefix} instead of buildroot/%prefix
find $RPM_BUILD_ROOT%{_prefix} -type f -print | \
	sed "s@^$RPM_BUILD_ROOT@@g" > %{name}-%{version}-%{release}-filelist
if [ "$(cat %{name}-%{version}-%{release}-filelist)X" = "X" ] ; then
    echo "ERROR: EMPTY FILE LIST"
    exit 1
fi

%clean
rm -rf $RPM_BUILD_ROOT

%files -f %{name}-%{version}-%{release}-filelist
%defattr(-,root,root,-)
%doc CREDITS ChangeLog README MPL-1.1.txt

%changelog
* Mon Aug 27 2007 Rich Megginson <rmeggins@redhat.com> - 1.5.2-4%{dist}
- remove exclusive arch

* Mon Aug 27 2007 Rich Megginson <rmeggins@redhat.com> - 1.5.2-3%{dist}
- change license to MPL/GPL/LGPL tri-license

* Fri Jul 27 2007 Rich Megginson <rmeggins@redhat.com> - 1.5.2-2lel5idm
- added Makefile.PL.rpm

* Fri Jul 27 2007 Rich Megginson <rmeggins@redhat.com> - 1.5.2-1lel5idm
- bump version to 1.5.2 - fixes mozilla bugzilla 389731

* Sat Jul 22 2007 Margaret Lum <mlum@redhat.com> - 1.5-11lel5idm
- Reverting back to mozldap-devel

* Sat Jul 22 2007 Margaret Lum <mlum@redhat.com> - 1.5-10lel5idm
- Use mozldap package, not mozldap-devel package

* Sat Jul 21 2007 Margaret Lum <mlum@redhat.com> - 1.5-9el5idm
- Use mozldap for RHEL-5

* Thu Jun 14 2007 Margaret Lum <mlum@redhat.com> - 1.5-8el5idm
- Branch for IDMCOMMON, update disttag to el5idm

* Thu Jun 14 2007 Margaret Lum <mlum@redhat.com> - 1.5-7el4idm
- Branch for IDMCOMMON, update disttag to el4idm

* Thu Jan 11 2007 Rich Megginson <rmeggins@redhat.com> - 1.5-7
- import sources from Fedora
- Change license to MPL - add MPL-1.1.txt to DOCs

* Tue Oct 17 2006 Rich Megginson <rmeggins@redhat.com> - 1.5-6
- look for brp-compress first in /usr/lib then _libdir

* Tue Oct 17 2006 Rich Megginson <rmeggins@redhat.com> - 1.5-5
- there is no TODO file; use custom Makefile.PL

* Mon Oct 16 2006 Rich Megginson <rmeggins@redhat.com> - 1.5-4
- use pkg-config --variable=xxx instead of --cflags e.g.

* Mon Oct 16 2006 Rich Megginson <rmeggins@redhat.com> - 1.5-3
- this is not a noarch package

* Mon Oct 16 2006 Rich Megginson <rmeggins@redhat.com> - 1.5-2
- Use new mozldap6, dirsec versions of nspr, nss

* Tue Feb  7 2006 Rich Megginson <richm@stanfordalumni.org> - 1.5-1
- Based on the perl-LDAP.spec file

