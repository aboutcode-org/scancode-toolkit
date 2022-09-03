SUMMARY = "Live image install script with a second rootfs/kernel"
LICENSE = "MIT"
LIC_FILES_CHKSUM = "file://${COREBASE}/meta/COPYING.MIT;md5=3da9cfbcb788c80a0384361b4de20420"
SRC_URI = "file://init-install-testfs.sh"

RDEPENDS_${PN} = "grub parted e2fsprogs-mke2fs"

S = "${WORKDIR}"

do_install() {
        install -m 0755 ${WORKDIR}/init-install-testfs.sh ${D}/install.sh
}

INHIBIT_DEFAULT_DEPS = "1"
FILES_${PN} = " /install.sh "
COMPATIBLE_HOST = "(i.86|x86_64).*-linux"