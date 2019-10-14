# Copyright 1999-2019 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

KDE_HANDBOOK="forceoptional"
KDE_TEST="optional"
VIRTUALX_REQUIRED="test"
inherit kde5

DESCRIPTION="KDE Archiving tool"
HOMEPAGE="https://kde.org/applications/utilities/ark
https://utils.kde.org/projects/ark/"
KEYWORDS=""
IUSE="bzip2 lzma zip"

BDEPEND="
	sys-devel/gettext
"
RDEPEND="
	$(add_frameworks_dep karchive)
	$(add_frameworks_dep kcompletion)
	$(add_frameworks_dep kconfig)
	$(add_frameworks_dep kconfigwidgets)
	$(add_frameworks_dep kcoreaddons)
	$(add_frameworks_dep kcrash)
	$(add_frameworks_dep kdbusaddons)
	$(add_frameworks_dep ki18n)
	$(add_frameworks_dep kiconthemes)
	$(add_frameworks_dep kio)
	$(add_frameworks_dep kitemmodels)
	$(add_frameworks_dep kjobwidgets)
	$(add_frameworks_dep kparts)
	$(add_frameworks_dep kpty)
	$(add_frameworks_dep kservice)
	$(add_frameworks_dep kwidgetsaddons)
	$(add_frameworks_dep kxmlgui)
	$(add_qt_dep qtdbus)
	$(add_qt_dep qtgui)
	$(add_qt_dep qtwidgets)
	app-arch/libarchive:=[bzip2?,lzma?,zlib]
	sys-libs/zlib
	zip? ( >=dev-libs/libzip-1.2.0:= )
"
DEPEND="${RDEPEND}
	$(add_qt_dep qtconcurrent)
"

# bug #560548, last checked with 16.04.1
RESTRICT+=" test"

src_configure() {
	local mycmakeargs=(
		$(cmake-utils_use_find_package bzip2 BZip2)
		$(cmake-utils_use_find_package lzma LibLZMA)
		$(cmake-utils_use_find_package zip LibZip)
	)

	kde5_src_configure
}

pkg_postinst() {
	kde5_pkg_postinst

	if [[ -z "${REPLACING_VERSIONS}" ]]; then
		if ! has_version app-arch/rar; then
			elog "For creating/extracting rar archives, installing app-arch/rar is required."
			if ! has_version app-arch/unar && ! has_version app-arch/unrar; then
				elog "Alternatively, for only extracting rar archives, install app-arch/unar (free) or app-arch/unrar (non-free)."
			fi
		fi

		has_version app-arch/p7zip || \
			elog "For handling 7-Zip archives, install app-arch/p7zip."

		has_version app-arch/lrzip || \
			elog "For handling lrz archives, install app-arch/lrzip."
	fi
}
