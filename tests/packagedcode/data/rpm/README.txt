All the tests RPMs have been truncated to 10KB or less using dd to have
smaller tests files.

Their file type is correct and header is intact but are otherwise
incorrect/invalid rpms (incorrect checksum, corrupted archive, etc), 
they are not extractible with a regular rpm or cpio tool.

The dd command to create a file of 10000 bytes is:
$ dd if=mvlutils-2.8.4-7.0.2.0801061.src.rpm  of=mvlutils-2.8.4-7.0.2.0801061.src.rpm.1 bs=1 count=10000

And to verify the rpm headers are still readable:
$ dd if=mdv-rpm-summary-0.9.3-1mdv2010.0.noarch.rpm  of=mdv-rpm-summary-0.9.3-1mdv2010.0.noarch.rpm.1 bs=1 count=21000
$ rpm -qpi --nodigest --nosignature mdv-rp
m-summary-0.9.3-1mdv2010.0.noarch.rpm.1
21000+0 records in
21000+0 records out
21000 bytes (21 kB) copied, 0.179 s, 117 kB/s
Name        : mdv-rpm-summary              Relocations: (not relocateable)
Version     : 0.9.3                             Vendor: Mandriva
Release     : 1mdv2010.0                    Build Date: Thu Oct 29 11:31:32 2009
Install date: (not installed)               Build Host: klodia.mandriva.com
Group       : System/Internationalization   Source RPM: mdv-rpm-summary-0.9.3-1mdv2010.0.src.rpm
Size        : 6490616                          License: GPL
Signature   : DSA/SHA1, Thu Oct 29 22:14:02 2009, Key ID e7898ae070771ff3
Packager    : Anne Nicolas <anne.nicolas@mandriva.com>
Summary     : Localization files for packages summaries
Description :
This package includes translations of summaries the Mandriva Linux packages.
They are used by rpmdrake.
