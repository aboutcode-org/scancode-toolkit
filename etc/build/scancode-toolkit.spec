Name:           scancode-toolkit
Version:        v1.3.2
Release:        0
Url:            https://github.com/nexB/scancode-toolkit
Summary:        ScanCode is a tool to scan code and detect licenses, copyrights and more.
License:        Apache-2.0 with ScanCode acknowledgment and CC0-1.0 and others
#Source:         https://github.com/nexB/scancode-toolkit/archive/master.tar.gz
#Source:         https://github.com/nexB/scancode-toolkit/archive/v%{version}.tar.gz
Source:         https://github.com/pombredanne/scancode-toolkit/archive/%{version}.tar.gz
BuildRoot:      %{_tmppath}/%{name}-%{version}-build
BuildRequires:  python-devel
BuildRequires:  zlib
BuildRequires:  bzip2
BuildRequires:  liblzma5
BuildRequires:  libarchive13
BuildRequires:  git

# http://openbuildservice.org/2013/11/22/Source-Update-Via_Token/
# http://openbuildservice.org/help/manuals/obs-reference-guide/cha.obs.authorization.token.html#idm139741989418240

%description
ScanCode is a tool to scan code and detect licenses, copyrights and more.

%prep
%setup -q -n %{name}-%{version}

%build
#cd %{buildroot}
ls -al
pwd
./configure
cd `pwd` && bin/py.test -n 2 -vvs src tests/commoncode

#py.test -n 2 -vvs src tests/commoncode tests/extractcode tests/textcode tests/typecode tests/cluecode tests/scancode tests/licensedcode/test_detect.py tests/licensedcode/test_index.py tests/licensedcode/test_legal.py tests/licensedcode/test_models.py

#%install
#python setup.py install --prefix=%{_prefix} --root=%{buildroot}

#%check
#source configure && py.test -n 2 -vs src tests/commoncode
