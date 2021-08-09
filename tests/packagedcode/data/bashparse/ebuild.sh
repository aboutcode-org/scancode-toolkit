# Copyright 1999-2021 Gentoo Authors
# Distributed under the terms of the GNU General Public License v2

EAPI=7

inherit desktop libtool qmake-utils systemd

MY_PV=${PV/_beta/-b}
MY_P=${PN}-${MY_PV}

DESCRIPTION="Featureful client/server network backup suite"
HOMEPAGE="https://www.bacula.org/"
SRC_URI="mirror://sourceforge/bacula/${MY_P}.tar.gz"

LICENSE="AGPL-3"
SLOT="0"
KEYWORDS="amd64 ppc ~sparc x86"
IUSE="acl bacula-clientonly bacula-nodir bacula-nosd +batch-insert examples ipv6 logwatch mysql postgres qt5 readline +sqlite ssl static tcpd vim-syntax X"

DEPEND="
	!bacula-clientonly? (
		!bacula-nodir? ( virtual/mta )
		postgres? ( dev-db/postgresql:=[threads] )
		mysql? ( || ( dev-db/mysql-connector-c dev-db/mariadb-connector-c ) )
		sqlite? ( dev-db/sqlite:3 )
	)
	dev-libs/gmp:0
	qt5? (
		dev-qt/qtcore:5
		dev-qt/qtgui:5
		dev-qt/qtwidgets:5
		dev-qt/qtsvg:5
		x11-libs/qwt:6
	)
	logwatch? ( sys-apps/logwatch )
	readline? ( sys-libs/readline:0 )
	static? (
		dev-libs/lzo[static-libs]
		sys-libs/ncurses:=[static-libs]
		sys-libs/zlib[static-libs]
		acl? ( virtual/acl[static-libs(+)] )
		ssl? ( dev-libs/openssl:0=[static-libs] )
	)
	!static? (
		dev-libs/lzo
		sys-libs/ncurses:=
		sys-libs/zlib
		acl? ( virtual/acl )
		ssl? ( dev-libs/openssl:0= )
	)
	tcpd? ( >=sys-apps/tcp-wrappers-7.6 )
"
RDEPEND="${DEPEND}
	acct-user/bacula
	acct-group/bacula
	!bacula-clientonly? (
		!bacula-nosd? (
			app-arch/mt-st
			sys-block/mtx
		)
	)
	vim-syntax? ( || ( app-editors/vim app-editors/gvim ) )
"

REQUIRED_USE="
	!bacula-clientonly? ( ^^ ( mysql postgres sqlite ) )
	static? ( bacula-clientonly )
"

S=${WORKDIR}/${MY_P}

pkg_setup() {
	#XOR and !bacula-clientonly controlled by REQUIRED_USE
	use mysql && export mydbtype="mysql"
	use postgres && export mydbtype="postgresql"
	use sqlite && export mydbtype="sqlite3"

	if use bacula-clientonly && use static && use qt5; then
		ewarn
		ewarn "Building statically linked 'bat' is not supported. Ignorig 'qt5' useflag."
		ewarn
	fi
}

src_prepare() {
	# adjusts default configuration files for several binaries
	# to /etc/bacula/<config> instead of ./<config>
	pushd src >&/dev/null || die
	for f in console/console.c dird/dird.c filed/filed.c \
		stored/bcopy.c stored/bextract.c stored/bls.c \
		stored/bscan.c stored/btape.c stored/stored.c \
		qt-console/main.cpp; do
		sed -i -e 's|^\(#define CONFIG_FILE "\)|\1/etc/bacula/|g' "${f}" \
			|| die "sed on ${f} failed"
	done
	popd >&/dev/null || die

	# bug 466688 drop deprecated categories from Desktop file
	sed -i -e 's/Application;//' scripts/bat.desktop.in || die

	# bug 466690 Use CXXFLAGS instead of CFLAGS
	sed -i -e 's/@CFLAGS@/@CXXFLAGS@/' autoconf/Make.common.in || die

	# drop automatic install of unneeded documentation (for bug 356499)
	eapply -p0 "${FILESDIR}"/7.2.0/${PN}-7.2.0-doc.patch

	# bug #310087
	eapply "${FILESDIR}"/5.2.3/${PN}-5.2.3-as-needed.patch

	# bug #311161
	eapply -p0 "${FILESDIR}"/9.0.2/${PN}-9.0.2-lib-search-path.patch

	# bat needs to respect LDFLAGS and CFLAGS
	eapply -p0 "${FILESDIR}"/9.0.6/${PN}-9.0.6-bat-pro.patch

	# bug #328701
	eapply -p0 "${FILESDIR}"/5.2.3/${PN}-5.2.3-openssl-1.patch

	eapply -p0 "${FILESDIR}"/9.6.3/${PN}-9.6.3-fix-static.patch

	# fix soname in libbaccat.so bug #602952
	eapply -p0 "${FILESDIR}/bacula-fix-sonames.patch"

	# do not strip binaries
	sed -i -e "s/strip /# strip /" src/filed/Makefile.in || die
	sed -i -e "s/strip /# strip /" src/console/Makefile.in || die

	# fix file not found error during make depend
	eapply -p0 "${FILESDIR}"/7.0.2/${PN}-7.0.2-depend.patch

	eapply_user

	# Fix systemd unit files:
	# bug 497748
	sed -i -e '/Requires/d' platforms/systemd/*.service.in || die
	sed -i -e '/StandardOutput/d' platforms/systemd/*.service.in || die
	# bug 504370
	sed -i -e '/Alias=bacula-dir/d' platforms/systemd/bacula-dir.service.in || die
	# bug 584442 and 504368
	sed -i -e 's/@dir_user@/root/g' platforms/systemd/bacula-dir.service.in || die

	# build 'bat' for Qt5
	export QMAKE="$(qt5_get_bindir)"/qmake

	# adapt to >=Qt-5.9 (see bug #644566)
	# qmake needs an existing target file to generate install instructions
	sed -i -e 's#bins.files = bat#bins.files = .libs/bat#g' \
		src/qt-console/bat.pro.in || die
	mkdir src/qt-console/.libs || die
	touch src/qt-console/.libs/bat || die
	chmod 755 src/qt-console/.libs/bat || die

	# fix handling of libressl version
	# needs separate handling for <libressl-2.7 and >=libressl2.7
	# (see bug #655520)
	if has_version "<dev-libs/libressl-2.7"; then
		eapply -p0 "${FILESDIR}"/9.4.0/${PN}-9.4.0-libressl26.patch
	else
		eapply -p0 "${FILESDIR}"/9.4.0/${PN}-9.4.0-libressl27.patch
	fi

	# Don't let program install man pages directly
	sed -i -e 's/ manpages//' Makefile.in || die

	# correct installation for plugins to mode 0755 (bug #725946)
	sed -i -e "s/(INSTALL_PROGRAM) /(INSTALL_LIB) /" src/plugins/fd/Makefile.in ||die

	# fix bundled libtool (bug 466696)
	# But first move directory with M4 macros out of the way.
	# It is only needed by autoconf and gives errors during elibtoolize.
	mv autoconf/libtool autoconf/libtool1 || die
	elibtoolize
}

src_configure() {
	local myconf=''

	if use bacula-clientonly; then
		myconf="${myconf} \
			$(use_enable bacula-clientonly client-only) \
			$(use_enable !static libtool) \
			$(use_enable static static-cons) \
			$(use_enable static static-fd)"
	else
		myconf="${myconf} \
			$(use_enable !bacula-nodir build-dird) \
			$(use_enable !bacula-nosd build-stored)"
		# bug #311099
		# database support needed by dir-only *and* sd-only
		# build as well (for building bscan, btape, etc.)
		myconf="${myconf}
			--with-${mydbtype}"
	fi

	# do not build bat if 'static' clientonly
	if ! use bacula-clientonly || ! use static; then
		myconf="${myconf} \
			$(use_enable qt5 bat)"
	fi

	myconf="${myconf} \
		$(use_with X x) \
		$(use_enable batch-insert) \
		$(use_enable !readline conio) \
		$(use_enable readline) \
		$(use_with readline readline /usr) \
		$(use_with ssl openssl) \
		$(use_enable ipv6) \
		$(use_enable acl) \
		$(use_with tcpd tcp-wrappers)"

	econf \
		--with-pid-dir=/var/run \
		--sysconfdir=/etc/bacula \
		--with-archivedir=/var/lib/bacula/tmp \
		--with-subsys-dir=/var/lock/subsys \
		--with-working-dir=/var/lib/bacula \
		--with-logdir=/var/lib/bacula \
		--with-scriptdir=/usr/libexec/bacula \
		--with-systemd=$(systemd_get_systemunitdir) \
		--with-dir-user=bacula \
		--with-dir-group=bacula \
		--with-sd-user=root \
		--with-sd-group=bacula \
		--with-fd-user=root \
		--with-fd-group=bacula \
		--enable-smartalloc \
		--disable-afs \
		--without-s3 \
		--host=${CHOST} \
		${myconf}
}

src_compile() {
	# Make build log verbose (bug #447806)
	emake NO_ECHO=""
}

src_install() {
	emake DESTDIR="${D}" install
	doicon scripts/bacula.png

	# install bat icon and desktop file when enabled
	# (for some reason ./configure doesn't pick this up)
	if use qt5 && ! use static ; then
		doicon src/qt-console/images/bat_icon.png
		domenu scripts/bat.desktop
	fi

	# remove some scripts we don't need at all
	rm -f "${D}"/usr/libexec/bacula/{bacula,bacula-ctl-dir,bacula-ctl-fd,bacula-ctl-sd,startmysql,stopmysql}

	# rename statically linked apps
	if use bacula-clientonly && use static ; then
		pushd "${D}"/usr/sbin || die
		mv static-bacula-fd bacula-fd || die
		mv static-bconsole bconsole || die
		popd || die
	fi

	# extra files which 'make install' doesn't cover
	if ! use bacula-clientonly; then
	    # the database update scripts
		diropts -m0750
		insinto /usr/libexec/bacula/updatedb
		insopts -m0754
		doins "${S}"/updatedb/*
		fperms 0640 /usr/libexec/bacula/updatedb/README

		# the logrotate configuration
		# (now unconditional wrt bug #258187)
		diropts -m0755
		insinto /etc/logrotate.d
		insopts -m0644
		newins "${S}"/scripts/logrotate bacula

		# the logwatch scripts
		if use logwatch; then
			diropts -m0750
			dodir /usr/share/logwatch/scripts/services
			dodir /usr/share/logwatch/scripts/shared
			dodir /etc/logwatch/conf/logfiles
			dodir /etc/logwatch/conf/services
			pushd "${S}"/scripts/logwatch >&/dev/null || die
			emake DESTDIR="${D}" install
			popd >&/dev/null || die
		fi
	fi

	# Install all man pages
	doman "${S}"/manpages/*.[18]

	if ! use qt5; then
		rm -vf "${D}"/usr/share/man/man1/bat.1*
	fi
	rm -vf "${D}"/usr/share/man/man1/bacula-tray-monitor.1*

	if use bacula-clientonly || use bacula-nodir ; then
		rm -vf "${D}"/usr/libexec/bacula/create_*_database
		rm -vf "${D}"/usr/libexec/bacula/drop_*_database
		rm -vf "${D}"/usr/libexec/bacula/make_*_tables
		rm -vf "${D}"/usr/libexec/bacula/update_*_tables
		rm -vf "${D}"/usr/libexec/bacula/drop_*_tables
		rm -vf "${D}"/usr/libexec/bacula/grant_*_privileges
		rm -vf "${D}"/usr/libexec/bacula/*_catalog_backup
	fi
	if use bacula-clientonly || use bacula-nosd; then
		rm -vf "${D}"/usr/libexec/bacula/disk-changer
		rm -vf "${D}"/usr/libexec/bacula/mtx-changer
		rm -vf "${D}"/usr/libexec/bacula/dvd-handler
	fi

	# documentation
	dodoc ChangeLog ReleaseNotes SUPPORT

	# install examples (bug #457504)
	if use examples; then
		docinto examples/
		dodoc -r examples/*
	fi

	# vim-files
	if use vim-syntax; then
		insinto /usr/share/vim/vimfiles/syntax
		doins scripts/bacula.vim
		insinto /usr/share/vim/vimfiles/ftdetect
		newins scripts/filetype.vim bacula_ft.vim
	fi

	# setup init scripts
	myscripts="bacula-fd"
	if ! use bacula-clientonly; then
		if ! use bacula-nodir; then
			myscripts="${myscripts} bacula-dir"
		fi
		if ! use bacula-nosd; then
			myscripts="${myscripts} bacula-sd"
		fi
	fi
	for script in ${myscripts}; do
		# copy over init script and config to a temporary location
		# so we can modify them as needed
		cp "${FILESDIR}/${script}".confd "${T}/${script}".confd || die "failed to copy ${script}.confd"
		cp "${FILESDIR}/newscripts/${script}".initd "${T}/${script}".initd || die "failed to copy ${script}.initd"

		# now set the database dependancy for the director init script
		case "${script}" in
			bacula-dir)
				case "${mydbtype}" in
					sqlite3)
						# sqlite databases don't have a daemon
						sed -i -e 's/need "%database%"/:/g' "${T}/${script}".initd || die
						;;
					*)
						# all other databases have daemons
						sed -i -e "s:%database%:${mydbtype}:" "${T}/${script}".initd || die
						;;
				esac
				;;
			*)
				;;
		esac

		# install init script and config
		newinitd "${T}/${script}".initd "${script}"
		newconfd "${T}/${script}".confd "${script}"
	done

	systemd_dounit "${S}"/platforms/systemd/bacula-{dir,fd,sd}.service

	# make sure the working directory exists
	diropts -m0750
	keepdir /var/lib/bacula

	# make sure bacula group can execute bacula libexec scripts
	fowners -R root:bacula /usr/libexec/bacula
}

pkg_postinst() {
	if use bacula-clientonly; then
		fowners root:bacula /var/lib/bacula
	else
		fowners bacula:bacula /var/lib/bacula
	fi

	einfo
	einfo "A group 'bacula' has been created. Any users you add to this"
	einfo "group have access to files created by the daemons."
	einfo
	einfo "A user 'bacula' has been created.  Please see the bacula manual"
	einfo "for information about running bacula as a non-root user."
	einfo

	if ! use bacula-clientonly && ! use bacula-nodir; then
		einfo
		einfo "If this is a new install, you must create the ${mydbtype} databases with:"
		einfo "  /usr/libexec/bacula/create_${mydbtype}_database"
		einfo "  /usr/libexec/bacula/make_${mydbtype}_tables"
		einfo "  /usr/libexec/bacula/grant_${mydbtype}_privileges"
		einfo

		ewarn "ATTENTION!"
		ewarn "The format of the database may have changed."
		ewarn "If you just upgraded from a version below 9.0.0 you must run"
		ewarn "'update_bacula_tables' now."
		ewarn "Make sure to have a backup of your catalog before."
		ewarn
	fi

	if use sqlite; then
		einfo
		einfo "Be aware that Bacula does not officially support SQLite database anymore."
		einfo "Best use it only for a client-only installation. See Bug #445540."
		einfo
	fi

	einfo "Please note that 'bconsole' will always be installed. To compile 'bat'"
	einfo "you have to enable 'USE=qt5'."
	einfo
	einfo "/var/lib/bacula/tmp was configured for archivedir. This dir will be used during"
	einfo "restores, so be sure to set it to an appropriate in dir in the bacula config."
}
