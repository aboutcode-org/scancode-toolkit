# Maintainer: Natanael Copa <ncopa@alpinelinux.org>
pkgname=cairo
pkgver=1.16.0
pkgrel=2
pkgdesc="A vector graphics library"
url="https://cairographics.org/"
arch="all"
options="!check"  # Recursive dependency on gtk+2.0 for check.
license="LGPL-2.0-or-later MPL-1.1"
depends=
depends_dev="fontconfig-dev freetype-dev libxrender-dev pixman-dev
	xcb-util-dev libxext-dev $pkgname-tools"
makedepends="$depends_dev zlib-dev expat-dev glib-dev libpng-dev autoconf automake libtool"
subpackages="$pkgname-dev $pkgname-doc $pkgname-gobject $pkgname-tools $pkgname-dbg"
source="https://cairographics.org/releases/cairo-$pkgver.tar.xz
	musl-stacksize.patch
	CVE-2018-19876.patch
	pdf-flush.patch
	85.patch
	"
builddir="$srcdir/$pkgname-$pkgver"

# secfixes:
#   1.16.0-r2:
#     - CVE-2020-35492
#   1.16.0-r1:
#     - CVE-2018-19876

build() {
	cd "$builddir"
	./configure \
		--build=$CBUILD \
		--host=$CHOST \
		--prefix=/usr \
		--sysconfdir=/etc \
		--localstatedir=/var \
		--enable-ft \
		--enable-gobject \
		--enable-pdf \
		--enable-png \
		--enable-ps \
		--enable-svg \
		--enable-tee \
		--enable-x \
		--enable-xcb \
		--enable-xcb-shm \
		--enable-xlib \
		--enable-xlib-xrender \
		--disable-xlib-xcb \
		--disable-static
	make
}

package() {
	cd "$builddir"
	make DESTDIR="$pkgdir" install
}

gobject() {
	pkgdesc="$pkgdesc (gobject bindings)"
	mkdir -p "$subpkgdir"/usr/lib
	mv "$pkgdir"/usr/lib/libcairo-gobject.so.* "$subpkgdir"/usr/lib/
}

tools() {
	pkgdesc="$pkgdesc (development tools)"
	mkdir -p "$subpkgdir"/usr/lib/cairo
	mv "$pkgdir"/usr/bin "$subpkgdir"/usr/
	mv "$pkgdir"/usr/lib/cairo/libcairo-trace.* \
		"$subpkgdir"/usr/lib/cairo/
}

sha512sums="9eb27c4cf01c0b8b56f2e15e651f6d4e52c99d0005875546405b64f1132aed12fbf84727273f493d84056a13105e065009d89e94a8bfaf2be2649e232b82377f  cairo-1.16.0.tar.xz
86f26fe41deb5e14f553c999090d1ec1d92a534fa7984112c9a7f1d6c6a8f1b7bb735947e8ec3f26e817f56410efe8cc46c5e682f6a278d49b40a683513740e0  musl-stacksize.patch
8f13cdcae0f134e04778cf5915f858fb8d5357a7e0a454791c93d1566935b985ec66dfe1683cd0b74a1cb44a130923d7a27cf006f3fc70b9bee93abd58a55aa3  CVE-2018-19876.patch
533ea878dc7f917af92e2694bd3f535a09cde77f0ecd0cc00881fbc9ec1ea86f60026eacc76129705f525f6672929ad8d15d8cfe1bfa61e9962e805a7fbded81  pdf-flush.patch
20699d2dd10531f99587cdcd187a23e23bca5a9f031255c95aade4dadb79bbb62118c7ddff677c2fd20e4ba7694eee4debcd79a4d0736d62951a4fcee56ccae0  85.patch"
