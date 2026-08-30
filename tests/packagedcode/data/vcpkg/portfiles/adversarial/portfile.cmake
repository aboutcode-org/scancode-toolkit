# vcpkg_from_github(REPO ignored/comment REF bad SHA512 bad)
#[=[
vcpkg_from_gitlab(REPO ignored/bracket-comment REF bad SHA512 bad)
]=]
set(IGNORED "vcpkg_from_git(REPO ignored/string REF bad)")

vcpkg_download_distfile(
    ARCHIVE
    URLS
        "${DYNAMIC_URL}"
        "https://downloads.example.com/source.tar.gz"
        [=[https://mirror.example.com/source.tar.gz]=]
    FILENAME source.tar.gz
    SHA512 distfile-sha512
)

vcpkg_from_github(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO example/dynamic-ref
    REF "${VERSION}"
    SHA512 github-sha512
    PATCHES nested(name).patch
)

vcpkg_from_bitbucket(
    OUT_SOURCE_PATH SOURCE_PATH
    REPO example/project
    REF v2.0.0
    SHA512 bitbucket-sha512
)
