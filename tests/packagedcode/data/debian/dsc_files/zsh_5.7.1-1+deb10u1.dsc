-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

Format: 3.0 (quilt)
Source: zsh
Binary: zsh-common, zsh, zsh-doc, zsh-static, zsh-dev
Architecture: any all
Version: 5.7.1-1+deb10u1
Maintainer: Debian Zsh Maintainers <pkg-zsh-devel@lists.alioth.debian.org>
Uploaders: Michael Prokop <mika@debian.org>, Axel Beckert <abe@debian.org>, Frank Terbeck <ft@bewatermyfriend.org>, Richard Hartmann <richih@debian.org>
Homepage: https://www.zsh.org/
Standards-Version: 4.3.0
Vcs-Browser: https://salsa.debian.org/debian/zsh
Vcs-Git: https://salsa.debian.org/debian/zsh.git -b debian
Testsuite: autopkgtest
Testsuite-Triggers: adequate
Build-Depends: bsdmainutils, cm-super-minimal, debhelper-compat (= 12), dpkg-dev (>= 1.16.2~), ghostscript, groff, groff-base, libcap-dev [linux-any], libncursesw5-dev, libpcre3-dev, texinfo (>= 5~), texlive-fonts-recommended, texlive-latex-base, texlive-latex-recommended, yodl (>= 3.08.01) | yodl (<< 3.08.00)
Package-List:
 zsh deb shells optional arch=any
 zsh-common deb shells optional arch=all
 zsh-dev deb libdevel optional arch=any
 zsh-doc deb doc optional arch=all
 zsh-static deb shells optional arch=any
Checksums-Sha1:
 b2fd47fdb878aa681edc974864e37baae9b0d6b7 2776796 zsh_5.7.1.orig.tar.xz
 14a8d38d3fae5b8eec0b124be5c943a60c4e8fec 87028 zsh_5.7.1-1+deb10u1.debian.tar.xz
Checksums-Sha256:
 439aafb4341522c307a67a2680e95fadb1b35a5c7f332089b9cc5154496570ca 2776796 zsh_5.7.1.orig.tar.xz
 ecbe22ed6a2b8dcaf10eff02b6b66583ce8d108a936624fc424c72188dea1ddd 87028 zsh_5.7.1-1+deb10u1.debian.tar.xz
Files:
 acc1a32ef5b3120ead5c6f0d011ceb76 2776796 zsh_5.7.1.orig.tar.xz
 d0f5fe26d9548331d9757e26b95c7aaf 87028 zsh_5.7.1-1+deb10u1.debian.tar.xz

-----BEGIN PGP SIGNATURE-----

iQIzBAEBCgAdFiEERoyJeTtCmBnp12Ema+Zjx1o1yXUFAmIMYK4ACgkQa+Zjx1o1
yXWTgw//SzaiMwbl8gSiQ/mB7+KPCeqL0o44q8oVAbj0WWhlh6yVUdjIcoHk6Zr3
Om4b3C5pU1l64jQ/JH5GP4i/7NnHAttobDL5zh9yvXAjUkUSfhBB6mJPeKT2QlHY
3SsvWiwtZOU8hPdwW48ATFiSSiYka+hKEM5nr5f/kI++yg2Rg7d1b5svaD3BMytI
Hl25comMwLgPeL4aIB7j8UL0sQT2zb/O5CK4aZr3CPUxy9OzBAwpQuukNNsJJ3Zg
g+a6Y6ADLAdhkav1JeZIF6LQ4Q9sk4Cqkp+CFenvRtDv2BDdosOXwOnBUBlm1A2j
yPuOcPdgSDqctMohSWVehDqGZK8dPjIOVq/sX3yKzwtNWdil9aErjGWxQVRSMyfg
fqEaCHYdpRpfrE8QWk+7TqovRqv3PaAmY6wahEAd5buniRScDF2yobT95qDOMnfj
fR1YDDH0cRkePHt+VHQUzM1mO4c/5Obhxfd8uExR+8KpO4SnsT8z7wa1J1O+jWGg
88zuhJ2HUCDGHdVlpgksagnNkmbT1Oohml6YfTAtDO4eXXJeTPmSpOYNzRCMsN0D
V1tY+awJuR0VSNjo+3X7DKyC/pKJiCzk+MBVogmFvzfBwJhYiLbVnVElNic/2J2J
Rz6VMPKIYqKUTyIgsQML0IkK8D9Lpp1LHqLNbUVt2aWcYlqgPBU=
=cPZC
-----END PGP SIGNATURE-----