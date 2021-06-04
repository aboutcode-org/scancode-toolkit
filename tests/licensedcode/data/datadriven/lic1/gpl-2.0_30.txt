#
# spec file for package btrace (Version 1.0)
#
# Copyright (c) 2005 SUSE LINUX Products GmbH, Nuernberg, Germany.
# This file and all modifications and additions to the pristine
# package are under the same license as the package itself.
#
# Please submit bugfixes or comments via http://www.suse.de/feedback/
#

# norootforbuild
# neededforbuild tetex te_latex gcc

Name:         btrace
License:      GPL
Group:        foo
Version:      1.0
Release:      1
URL:          http://brick.kernel.dk/snaps
Summary:      Block IO tracer
Source0:      %name-%version.tar.bz2
BuildRoot:    %{_tmppath}/%{name}-%{version}-build

%description
btrace can show detailed info about what is happening on a block
device io queue. This is valuable for diagnosing and fixing
performance or application problems relating to block layer io.


Authors:
--------
    Jens Axboe <axboe@kernel.dk>

%prep
%setup -q

%build
make CFLAGS="$RPM_OPT_FLAGS" all docs

%install
rm -rf $RPM_BUILD_ROOT
make dest=$RPM_BUILD_ROOT prefix=$RPM_BUILD_ROOT/%{_prefix} install

%clean
rm -rf $RPM_BUILD_ROOT

%files
%defattr(-,root,root)
%doc README doc/blktrace.pdf
/usr/bin/*
/usr/man/*

%changelog -n btrace
* Mon Oct 10 2005 - axboe@suse.de
- Initial version
