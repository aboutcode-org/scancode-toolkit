What is this?
=============

Physics is a physical world simulator and playground.  You can add
squares, circles, triangles, or draw your own shapes, and see them
come to life with forces, friction, and inertia.

How to use?
===========

Physics is not part of the Sugar desktop, but can be added.  Please refer to;

* [How to Get Sugar on sugarlabs.org](https://sugarlabs.org/),
* [How to use Sugar](https://help.sugarlabs.org/),
* [How to use Physics](https://help.sugarlabs.org/physics.html).

How to upgrade?
===============

On Sugar desktop systems;
* use [My Settings](https://help.sugarlabs.org/my_settings.html), [Software Update](https://help.sugarlabs.org/my_settings.html#software-update).

How to integrate?
=================

On Debian and Ubuntu systems;

```
apt install sugar-physics-activity
```

On Fedora systems;

```
dnf install sugar-physics
```

Physics depends on Python, [Sugar
Toolkit](https://github.com/sugarlabs/sugar-toolkit-gtk3), Cairo,
Telepathy, GTK+ 3, Pango, Box2d and Pygame.

Physics is started by [Sugar](https://github.com/sugarlabs/sugar).

Physics is packaged by Linux distributions;
* [Fedora package sugar-physics](https://src.fedoraproject.org/).

How to develop?
===============

* setup a development environment for Sugar desktop,
* install the dependencies, see below,
* clone this repository,
* edit source files,
* test in Terminal by typing `sugar-activity3`

How to install dependencies for development
===========================================

For development, install the Box2D library.

* Install `swig`,
   - On Ubuntu/Debian, run
    ```sudo apt install swig```
   - On Fedora/RHEL systems, run
    ```sudo dnf install swig```
* Install setuptools and pip,
   - On Ubuntu/Debian, run
   ```sudo apt install python3 python3-setuptools python3-pip python3-all-dev ```
   - On Fedora/RHEL, run
   ```sudo dnf install python3-pip python3-setuptools```
* Clone pybox2d and build, run
```
git clone https://github.com/pybox2d/pybox2d
cd pybox2d
# Make sure you have installed swig
python3 setup.py build
pip3 install . --system

```
