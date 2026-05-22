# Welcome to the /etc/os-release zoo!

This project collects `/etc/os-release` files from various distributions.
If you see one missing, please open an issue with the text or send me a pull
request.

`/etc/os-release` contains operating system identification and was originally 
[introduced](http://0pointer.de/blog/projects/os-release) with systemd.
For more information please refer to the os-release
[man page](http://0pointer.de/public/systemd-man/os-release.html).

Not all distributions and/or versions include an os-release file. Distributions
known _not_ to support it are included in this collection as files with a
`not-supported` file extension, e.g. `centos/centos-6.not-supported`.
