# Contributor: Oliver Smith <ollieparanoid@postmarketos.org>
# Maintainer: Natanael Copa <ncopa@alpinelinux.org>
pkgname=linux-firmware
pkgver=20210511
pkgrel=0
pkgdesc="firmware files for linux"
url="https://git.kernel.org/?p=linux/kernel/git/firmware/linux-firmware.git;a=summary"
arch="all"
license="custom:multiple"
makedepends="libarchive-tools"
provides="linux-firmware-any"
provider_priority=1
options="!strip !check !archcheck !tracedeps !spdx"

_rpi_bt=e7fd166981ab4bb9a36c2d1500205a078a35714d

source="https://git.kernel.org/pub/scm/linux/kernel/git/firmware/linux-firmware.git/snapshot/linux-firmware-$pkgver.tar.gz
	BCM43430A1.hcd.${_rpi_bt::8}::https://github.com/RPi-Distro/bluez-firmware/raw/$_rpi_bt/broadcom/BCM43430A1.hcd
	BCM4345C0.hcd.${_rpi_bt::8}::https://github.com/RPi-Distro/bluez-firmware/raw/$_rpi_bt/broadcom/BCM4345C0.hcd
	BCM43430B0.hcd.${_rpi_bt::8}::https://github.com/RPi-Distro/bluez-firmware/raw/$_rpi_bt/broadcom/BCM43430B0.hcd
	BCM4345C5.hcd.${_rpi_bt::8}::https://github.com/RPi-Distro/bluez-firmware/raw/$_rpi_bt/broadcom/BCM4345C5.hcd"

_builddir="$srcdir"/$pkgname-$pkgver

# Put /lib/firmware/* folders in subpackages
_folders="3com acenic adaptec advansys amd amd-ucode amdgpu ar3k ath10k ath11k
	ath6k ath9k_htc atmel atusb av7110 bnx2 bnx2x brcm cadence cavium cis cpia2
	cxgb3 cxgb4 cypress dabusb dpaa2 dsp56k e100 edgeport emi26 emi62 ene-ub6250
	ess go7007 i915 imx inside-secure intel isci kaweth keyspan keyspan_pda korg
	libertas liquidio matrox mediatek mellanox meson microchip moxa mrvl mwl8k
	mwlwifi myricom netronome nvidia ositech qca qcom qed qlogic r128 radeon
	rockchip rsi rtl8192e rtl_bt rtl_nic rtlwifi rtw88 rtw89 sb16 silabs slicoss
	sun sxg tehuti ti ti-connectivity ti-keystone tigon ttusb-budget ueagle-atm
	vicam vxge yam yamaha"

subpackages="$pkgname-other::noarch $pkgname-none::noarch"
depends="linux-firmware-other=$pkgver-r$pkgrel"
for i in $_folders; do
	subpackages="$pkgname-$i:_folder:noarch $subpackages"
	depends="$pkgname-$i=$pkgver-r$pkgrel $depends"
done
subpackages="amd-ucode::noarch $subpackages"

package() {
	cd "${_builddir}"
	make DESTDIR="${pkgdir}" FIRMWAREDIR="/lib/firmware" install

	# add compat links for pre-5.0 kernel
	ln -s brcmfmac43455-sdio.raspberrypi,3-model-b-plus.txt "$pkgdir"/lib/firmware/brcm/brcmfmac43455-sdio.txt
	ln -s brcmfmac43430-sdio.raspberrypi,3-model-b.txt      "$pkgdir"/lib/firmware/brcm/brcmfmac43430-sdio.txt

	local fw; for fw in $source; do
		local _f=${fw%::*}
		case $_f in
		*.hcd*)
			install -Dm 644 $srcdir/$_f \
				"$pkgdir"/lib/firmware/brcm/"${_f%.*}"
			;;
		esac
	done

	rm -f "${pkgdir}/usr/lib/firmware/{Makefile,README,configure,GPL-3}"

	find "${pkgdir}" \( -name '*.S' -or -name '*.asm' -or \
		-name '*.c' -or -name '*.h' -or -name '*.pl' -or \
                -name 'Makefile' \) -exec rm -- {} \;
}

_folder() {
	local folder=${subpkgname##linux-firmware-}
	pkgdesc="firmware files for linux ($folder folder)"
	depends=""
	provides="linux-firmware-any"
	provider_priority=

	# Move /lib/firmware/$folder (case insensitive)
	mkdir -p "$subpkgdir/lib/firmware"
	mv "$(find "$pkgdir/lib/firmware" -iname "$folder" -type d)" \
		"$subpkgdir/lib/firmware"
}

other() {
	# Requires subfolders to be split in subpackages
	local leftover=""
	local i
	for i in "$pkgdir"/lib/firmware/*; do
		[ -d "$i" ] && leftover="$leftover $(basename $i)"
	done
	if [ "$leftover" != "" ]; then
		local fixed
		error "Not all subfolders have been moved to subpackages!"
		error "Fix this by adjusting _folders as follows:"
		fixed="$(echo $_folders$leftover | tr " " "\n" | tr '[A-Z]' '[a-z]' | sort)"
		echo "_folders=\"$(printf "$fixed" | tr "\n" " ")\"" | fold -s
		return 1
	fi

	# Move /lib/firmware (which doesn't have subfolders now)
	pkgdesc="firmware files for linux (uncategorized)"
	depends=""
	provides="linux-firmware-any"
	provider_priority=
	mkdir -p "$subpkgdir"/
	mv "$pkgdir"/lib "$subpkgdir"/
}

none() {
	# dummy package with no firmware
	pkgdesc="Empty linux firwmare package for those who does not need any firmware"
	provider_priority=
	provides="linux-firmware-any"
	depends=
	mkdir -p "$subpkgdir"
}

ucode() {
	pkgdesc="Microcode update files for AMD CPUs"
	provider_priority=
	provides=
	depends=

	# build ported from Arch Linux's PKGBUILD
	mkdir -p "$subpkgdir"/boot
	mkdir -p "$builddir"/kernel/x86/microcode
	cat "$pkgdir"/lib/firmware/amd-ucode/microcode_amd*.bin > "$builddir"/kernel/x86/microcode/AuthenticAMD.bin
	[ -n "$SOURCE_DATE_EPOCH" ] && touch -d @$SOURCE_DATE_EPOCH "$builddir"/kernel/x86/microcode/AuthenticAMD.bin
	cd "$builddir" && echo kernel/x86/microcode/AuthenticAMD.bin |
	  bsdtar --uid 0 --gid 0 -cnf - -T - |
	  bsdtar --null -cf - --format=newc @- > "$subpkgdir"/boot/amd-ucode.img
}

sha512sums="f282bdcd0e62f446a3c859876319ae2fb4b2e129022a4b2b1ced45f38c8b192ccb07a4480ff4d41ed8fc13c0a38bf0c0d5a5d98515a1750d655db5d919c6af8c  linux-firmware-20210511.tar.gz
355c940b4fd597101c332207678fd28154d7e7a90cb374b1fdf230d2061bf979af0209c5a423fca8d23ddb3d95abec741e7dd651da7f0aaa97459ed4fe4d2355  BCM43430A1.hcd.e7fd1669
1707c2955ceac3e6fc4b1edb8965c871dcfab21ce85cc617de67d7e6f3d6f9b93ee5a8a202de6b20f7b43d1462668287a8569786146cadf5e0268058d2524a9c  BCM4345C0.hcd.e7fd1669
c8b943bfeffa54ce1687ca69884e9d56efd28d5ea1dbef660915a80c3e036a8675e7d4299102c32006193e4895367654bb67e2d08e66d7803f396eee7e3dfbd6  BCM43430B0.hcd.e7fd1669
eac7428befa36952542e19d3c4a5fa96e1cb3a56c3b00770534909fb0d8caf503a42368175e715e1de58e50cfbd2b4c8ea5a26af3bd546cbbaf8d2c12457a628  BCM4345C5.hcd.e7fd1669"
