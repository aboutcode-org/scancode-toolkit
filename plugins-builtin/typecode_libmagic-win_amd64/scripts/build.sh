# a build script for libmagic on Windows 64

set -e
set -x

pkgprefix=mingw-w64
pkgname=file
pkgver=5.37
pkgrel=1
arch=x86_64
lib_target=../src/typecode_libmagic/lib
lic_target=../src/typecode_libmagic/licenses
data_target=../src/typecode_libmagic/data

today=$(date +%Y-%m-%d)

# fetch the upstream sources
wget -O ${pkgname}-${pkgver}.tar.gz ftp://ftp.astron.com/pub/file/${pkgname}-${pkgver}.tar.gz


fetch_msys_build_files() {
    # fetch the MSYS2 build file for reference
    pkgn=$1
    rm -rf $pkgn-msys2-$today
    svn export https://github.com/msys2/MINGW-packages/trunk/$pkgn $pkgn-msys2-$today
    tar -czf $pkgn-msys2-$today.tar.gz $pkgn-msys2-$today
    # rm -rf $pkgn-msys2-$today
}


get_dependencies() {
    pkginfo_file=$1
    egrep -o "^depend = (.*)$" $pkginfo_file | cut -d" " -f3
}


fetch_and_extract_binary() {
    package_arch=$1
    arch_name=$package_arch.pkg.tar.xz
    rm -rf $package_arch $arch_name
    
    # fetch    
    wget http://repo.msys2.org/mingw/$arch/$arch_name

    # extract
    mkdir $package_arch
    tar -xf $arch_name -C $package_arch
}

install_dlls_and_docs() {
    package_arch=$1
    mv $package_arch/mingw64/bin/*.dll $lib_target/
    if [ -d "$package_arch/mingw64/share/licenses" ]; then
        mv -f $package_arch/mingw64/share/licenses/* $lic_target
    fi

}


package_archive=$pkgprefix-$arch-$pkgname-$pkgver-$pkgrel-any

########################################33
fetch_msys_build_files $pkgprefix-$pkgname
fetch_and_extract_binary $package_archive

########################################33
# dispatch the built files
mv $package_archive/mingw64/bin/libmagic-1.dll $lib_target/libmagic.dll
mv $package_archive/mingw64/share/misc/magic.mgc $data_target

########################################33
# fetch dependencies
depends=$(get_dependencies $package_archive/.PKGINFO)

# no dlls: mingw-w64-x86_64-mpc-1.1.0-1-any
# no dlls: mingw-w64-x86_64-mpfr-4.0.2-2-any

depends="mingw-w64-x86_64-libsystre-1.0.1-4-any
    mingw-w64-x86_64-libtre-git-r128.6fb7206-2-any
    mingw-w64-x86_64-gettext-0.19.8.1-8-any
    mingw-w64-x86_64-gcc-libs-9.3.0-2-any
    mingw-w64-x86_64-expat-2.2.9-1-any
    mingw-w64-x86_64-libiconv-1.16-1-any
    mingw-w64-x86_64-gmp-6.2.0-1-any
    mingw-w64-x86_64-libwinpthread-git-8.0.0.5814.9dbf4cc1-1-any"

for dep_nevra in $depends
do
    fetch_and_extract_binary $dep_nevra
    install_dlls_and_docs $dep_nevra
    rm -rf $dep_nevra
done
