%define _bindir /bin

Summary: A GNU archiving program
Name: cpio
Version: 2.9
Release: 4%{?dist}
License: GPLv3+
Group: Applications/Archiving
URL: http://www.gnu.org/software/cpio/
Source: ftp://ftp.gnu.org/gnu/cpio/cpio-%{version}.tar.gz
Source1: cpio.1
Patch1: cpio-2.6-setLocale.patch
Patch2: cpio-2.9-rh.patch
Patch3: cpio-2.9-chmodRaceC.patch
Patch4: cpio-2.9-exitCode.patch
Requires(post): /sbin/install-info
Requires(preun): /sbin/install-info
BuildRequires: texinfo, autoconf, gettext
Buildroot: %{_tmppath}/%{name}-%{version}-%{release}-root-%(%{__id_u} -n)

%description
GNU cpio copies files into or out of a cpio or tar archive.  Archives
are files which contain a collection of other files plus information
about them, such as their file name, owner, timestamps, and access
permissions.  The archive can be another file on the disk, a magnetic
tape, or a pipe.  GNU cpio supports the following archive formats:  binary,
old ASCII, new ASCII, crc, HPUX binary, HPUX old ASCII, old tar and POSIX.1
tar.  By default, cpio creates binary format archives, so that they are
compatible with older cpio programs.  When it is extracting files from
archives, cpio automatically recognizes which kind of archive it is reading
and can read archives created on machines with a different byte-order.

Install cpio if you need a program to manage file archives.

%prep
%setup -q
%patch1  -p1 -b .setLocale
%patch2  -p1 -b .rh
%patch3  -p1 -b .chmodRaceC
%patch4  -p1 -b .exitCode

autoheader

%build

CFLAGS="$RPM_OPT_FLAGS -D_GNU_SOURCE -D_FILE_OFFSET_BITS=64 -D_LARGEFILE64_SOURCE -pedantic -Wall" %configure
make %{?_smp_mflags}

%install
rm -rf ${RPM_BUILD_ROOT}

make DESTDIR=$RPM_BUILD_ROOT INSTALL="install -p" install


rm -f $RPM_BUILD_ROOT%{_libexecdir}/rmt
rm -f $RPM_BUILD_ROOT%{_infodir}/dir
rm -f $RPM_BUILD_ROOT%{_mandir}/man1/*.1*
install -c -p -m 0644 %{SOURCE1} ${RPM_BUILD_ROOT}%{_mandir}/man1

%find_lang %{name}

%clean
rm -rf ${RPM_BUILD_ROOT}

%post
/sbin/install-info %{_infodir}/cpio.info.gz %{_infodir}/dir || :

%preun
if [ $1 = 0 ]; then
	/sbin/install-info --delete %{_infodir}/cpio.info.gz %{_infodir}/dir || :
fi

%files -f %{name}.lang
%defattr(-,root,root,0755)
%doc AUTHORS ChangeLog NEWS README THANKS TODO COPYING
%{_bindir}/*
%{_mandir}/man*/*
%{_infodir}/*.info*

%changelog
* Tue Sep 04 2007 Radek Brich <rbrich@redhat.com> 2.9-4
- Updated license tag

* Wed Aug 29 2007 Fedora Release Engineering <rel-eng at fedoraproject dot org> - 2.9-3
- Rebuild for selinux ppc32 issue.

* Thu Jul 19 2007 Radek Brich <rbrich@redhat.com> 2.9-1.1
- fix spec, rebuild

* Thu Jul 19 2007 Radek Brich <rbrich@redhat.com> 2.9-1
- update to 2.9, GPLv3

* Tue Feb 20 2007 Peter Vrabec <pvrabec@redhat.com> 2.6-27
- fix typo in changelog

* Thu Feb 08 2007 Ruben Kerkhof <ruben@rubenkerkhof.com> 2.6-26
- Preserve timestamps when installing files

* Thu Feb 08 2007 Peter Vrabec <pvrabec@redhat.com> 2.6-25
- set cpio bindir properly

* Wed Feb 07 2007 Peter Vrabec <pvrabec@redhat.com> 2.6-24
- fix spec file to meet Fedora standards (#225656) 

* Mon Jan 22 2007 Peter Vrabec <pvrabec@redhat.com> 2.6-23
- fix non-failsafe install-info use in scriptlets (#223682)

* Sun Dec 10 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-22
- fix rpmlint issue in spec file

* Tue Dec 05 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-21
- fix setlocale (#200478)

* Sat Nov 25 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-20
- cpio man page provided by RedHat

* Tue Jul 18 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-19
- fix cpio --help output (#197597)

* Wed Jul 12 2006 Jesse Keating <jkeating@redhat.com> - 2.6-18.1
- rebuild

* Sat Jun 10 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-18
- autoconf was added to BuildRequires, because autoheader is 
  used in prep phase (#194737)

* Tue Mar 28 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-17
- rebuild

* Sat Mar 25 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-15
- fix (#186339) on ppc and s390

* Thu Mar 23 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-14
- init struct  file_hdr (#186339)

* Wed Mar 15 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-13
- merge toAsciiError.patch with writeOutHeaderBufferOverflow.patch
- merge largeFileGrew.patch with lfs.patch
- fix large file support, cpio is able to store files<8GB 
  in 'old ascii' format (-H odc option)
- adjust warnings.patch

* Tue Mar 14 2006 Peter Vrabec <pvrabec@redhat.com> 2.6-12
- fix warn_if_file_changed() and set exit code to #1 when 
  cpio fails to store file > 4GB (#183224)

* Fri Feb 10 2006 Jesse Keating <jkeating@redhat.com> - 2.6-11.2.1
- bump again for double-long bug on ppc(64)

* Tue Feb 07 2006 Jesse Keating <jkeating@redhat.com> - 2.6-11.2
- rebuilt for new gcc4.1 snapshot and glibc changes

* Fri Dec 09 2005 Jesse Keating <jkeating@redhat.com>
- rebuilt

* Wed Nov 23 2005 Peter Vrabec <pvrabec@redhat.com> 2.6-11
- fix previous patch(writeOutHeaderBufferOverflow)

* Wed Nov 23 2005 Peter Vrabec <pvrabec@redhat.com> 2.6-10
- write_out_header rewritten to fix buffer overflow(#172669)

* Mon Oct 31 2005 Peter Vrabec <pvrabec@redhat.com> 2.6-9
- fix checksum error on 64-bit machines (#171649)

* Fri Jul 01 2005 Peter Vrabec <pvrabec@redhat.com> 2.6-8
- fix large file support, archive >4GiB, archive members <4GiB (#160056)
- fix race condition holes, use mode 0700 for dir creation

* Tue May 17 2005 Peter Vrabec <pvrabec@redhat.com> 2.6-7
- fix #156314 (CAN-2005-1229) cpio directory traversal issue
- fix some gcc warnings

* Mon Apr 25 2005 Peter Vrabec <pvrabec@redhat.com> 2.6-6
- fix race condition (#155749)
- use find_lang macro

* Thu Mar 17 2005 Peter Vrabec <pvrabec@redhat.com>
- rebuild 2.6-5

* Mon Jan 24 2005 Peter Vrabec <pvrabec@redhat.com>
- insecure file creation (#145721)

* Mon Jan 17 2005 Peter Vrabec <pvrabec@redhat.com>
- fix symlinks pack (#145225)

* Fri Jan 14 2005 Peter Vrabec <pvrabec@redhat.com>
- new fixed version of lfs patch (#144688)

* Thu Jan 13 2005 Peter Vrabec <pvrabec@redhat.com>
- upgrade to cpio-2.6

* Tue Nov 09 2004 Peter Vrabec <pvrabec@redhat.com>
- fixed "cpio -oH ustar (or tar) saves bad mtime date after Jan 10 2004" (#114580)

* Mon Nov 01 2004 Peter Vrabec <pvrabec@redhat.com>
- support large files > 2GB (#105617)

* Thu Oct 21 2004 Peter Vrabec <pvrabec@redhat.com>
- fix dependencies in spec

* Tue Jun 15 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 13 2004 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Tue Sep 23 2003 Florian La Roche <Florian.LaRoche@redhat.de>
- do not link against -lnsl

* Wed Jun 04 2003 Elliot Lee <sopwith@redhat.com>
- rebuilt

* Fri Feb 14 2003 Jeff Johnson <jbj@redhat.com> 2.5-3
- setlocale for i18n compliance (#79136).

* Wed Jan 22 2003 Tim Powers <timp@redhat.com>
- rebuilt

* Mon Nov 18 2002 Jeff Johnson <jbj@redhat.com> 2.5-1
- update 2.5, restack and consolidate patches.
- don't apply (but include for now) freebsd and #56346 patches.
- add url (#54598).

* Thu Nov  7 2002 Jeff Johnson <jbj@redhat.com> 2.4.2-30
- rebuild from CVS.

* Fri Jun 21 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu May 23 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Wed Jan 09 2002 Tim Powers <timp@redhat.com>
- automated rebuild

* Thu Nov 22 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.4.2-25
- Fix up extraction of multiply linked files when the first link is
  excluded (Bug #56346)

* Mon Oct  1 2001 Bernhard Rosenkraenzer <bero@redhat.com> 2.4.2-24
- Merge and adapt patches from FreeBSD, this should fix FIFO handling

* Tue Jun 26 2001 Bernhard Rosenkraenzer <bero@redhat.com>
- Add and adapt Debian patch (pl36), fixes #45285 and a couple of other issues

* Sun Jun 24 2001 Elliot Lee <sopwith@redhat.com>
- Bump release + rebuild.

* Tue Aug  8 2000 Jeff Johnson <jbj@redhat.com>
- update man page with decription of -c behavior (#10581).

* Wed Jul 12 2000 Prospector <bugzilla@redhat.com>
- automatic rebuild

* Thu Jun 29 2000 Preston Brown <pbrown@redhat.com>
- patch from HJ Lu for better error codes upon exit

* Mon Jun  5 2000 Jeff Johnson <jbj@redhat.com>
- FHS packaging.

* Wed Feb  9 2000 Jeff Johnson <jbj@redhat.com>
- missing defattr.

* Mon Feb  7 2000 Bill Nottingham <notting@redhat.com>
- handle compressed manpages

* Fri Dec 17 1999 Jeff Johnson <jbj@redhat.com>
- revert the stdout patch (#3358), restoring original GNU cpio behavior
  (#6376, #7538), the patch was dumb.

* Tue Aug 31 1999 Jeff Johnson <jbj@redhat.com>
- fix infinite loop unpacking empty files with hard links (#4208).
- stdout should contain progress information (#3358).

* Sun Mar 21 1999 Crstian Gafton <gafton@redhat.com> 
- auto rebuild in the new build environment (release 12)

* Sat Dec  5 1998 Jeff Johnson <jbj@redhat.com>
- longlong dev wrong with "-o -H odc" headers (formerly "-oc").

* Thu Dec 03 1998 Cristian Gafton <gafton@redhat.com>
- patch to compile on glibc 2.1, where strdup is a macro

* Tue Jul 14 1998 Jeff Johnson <jbj@redhat.com>
- Fiddle bindir/libexecdir to get RH install correct.
- Don't include /sbin/rmt -- use the rmt from dump package.
- Don't include /bin/mt -- use the mt from mt-st package.
- Add prereq's

* Tue Jun 30 1998 Jeff Johnson <jbj@redhat.com>
- fix '-c' to duplicate svr4 behavior (problem #438)
- install support programs & info pages

* Mon Apr 27 1998 Prospector System <bugs@redhat.com>
- translations modified for de, fr, tr

* Fri Oct 17 1997 Donnie Barnes <djb@redhat.com>
- added BuildRoot
- removed "(used by RPM)" comment in Summary

* Thu Jun 19 1997 Erik Troan <ewt@redhat.com>
- built against glibc
- no longer statically linked as RPM doesn't use cpio for unpacking packages
