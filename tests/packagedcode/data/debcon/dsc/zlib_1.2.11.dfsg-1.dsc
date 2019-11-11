-----BEGIN PGP SIGNED MESSAGE-----
Hash: SHA512

Format: 3.0 (quilt)
Source: zlib
Binary: zlib1g, zlib1g-dev, zlib1g-dbg, zlib1g-udeb, lib64z1, lib64z1-dev, lib32z1, lib32z1-dev, libn32z1, libn32z1-dev
Architecture: any
Version: 1:1.2.11.dfsg-1
Maintainer: Mark Brown <broonie@debian.org>
Homepage: http://zlib.net/
Standards-Version: 3.9.8
Build-Depends: debhelper (>= 8.1.3~), binutils (>= 2.18.1~cvs20080103-2) [mips mipsel], gcc-multilib [amd64 i386 kfreebsd-amd64 mips mipsel powerpc ppc64 s390 sparc s390x] <!stage1>, dpkg-dev (>= 1.16.1)
Package-List:
 lib32z1 deb libs optional arch=amd64,ppc64,kfreebsd-amd64,s390x profile=!stage1
 lib32z1-dev deb libdevel optional arch=amd64,ppc64,kfreebsd-amd64,s390x profile=!stage1
 lib64z1 deb libs optional arch=sparc,s390,i386,powerpc,mips,mipsel profile=!stage1
 lib64z1-dev deb libdevel optional arch=sparc,s390,i386,powerpc,mips,mipsel profile=!stage1
 libn32z1 deb libs optional arch=mips,mipsel profile=!stage1
 libn32z1-dev deb libdevel optional arch=mips,mipsel profile=!stage1
 zlib1g deb libs required arch=any
 zlib1g-dbg deb debug extra arch=any
 zlib1g-dev deb libdevel optional arch=any
 zlib1g-udeb udeb debian-installer optional arch=any
Checksums-Sha1:
 1b7f6963ccfb7262a6c9d88894d3a30ff2bf2e23 370248 zlib_1.2.11.dfsg.orig.tar.gz
 c3b2bac9b1927fde66b72d4f98e4063ce0b51f34 18956 zlib_1.2.11.dfsg-1.debian.tar.xz
Checksums-Sha256:
 80c481411a4fe8463aeb8270149a0e80bb9eaf7da44132b6e16f2b5af01bc899 370248 zlib_1.2.11.dfsg.orig.tar.gz
 00b95b629fbe9a5181f8ba1ceddedf627aba1ab42e47f5916be8a41deb54098a 18956 zlib_1.2.11.dfsg-1.debian.tar.xz
Files:
 2950b229ed4a5e556ad6581580e4ab2c 370248 zlib_1.2.11.dfsg.orig.tar.gz
 fd4b8f37a845569734dfa2e0fe8a08dc 18956 zlib_1.2.11.dfsg-1.debian.tar.xz

-----BEGIN PGP SIGNATURE-----

iQFHBAEBCgAxFiEEreZoqmdXGLWf4p/qJNaLcl1Uh9AFAlrjaY8THGJyb29uaWVA
ZGViaWFuLm9yZwAKCRAk1otyXVSH0J2YB/wMNRqxrwDU5ZJAfnp5gEK1Dq0qT79v
FEEQ6ZfXHnxhQhIQvI/KIPLUIrqkoyvp1DhCxKi+b0LM29JMOpgK8l40EAE52gGk
2vH/NSrcgSXK8yXYJYG0h9fobAihK+eUa6cyp0NR049s8OI00BGSBiHJn3ONH6G4
zNE2vmG2iLVP9bdF/w+0WbyfwccnsjJprrCefJ2/HR+5ckX+PIGklHpI3WVoL1a8
qwfP8hx7pnR4CV1rFfmmDmtwORv4edwfgS6mmbdpKClWS2k4ft7AFEjmBPL+vqKc
6DzauiRhm79p2HZPGWyLvZ0rMUaVvIGYeNjO2n4Lpkc+snZAEX/3LFVQ
=BVVn
-----END PGP SIGNATURE-----
