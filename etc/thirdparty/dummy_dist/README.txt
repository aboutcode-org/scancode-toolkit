Dummy Wheel Distributions for Apple Silicon (macOS ARM64)
=========================================================

Overview
--------
This directory provides **empty wheel distributions** designed as a workaround to
allow the installation of `scancode-toolkit` on **Apple Silicon (macOS ARM64)** platforms.

The issue arises because certain required packages, such as `extractcode-7z`, do not
offer pre-built wheels compatible with Apple Silicon.
Consequently, `pip` encounters dependency resolution errors during installation.

Purpose
-------
The dummy wheels in this project serve as placeholders. These wheels:
- **Contain no functionality** and are completely empty.
- Allow `pip` to resolve dependencies correctly by tricking it into treating the
  required package as already installed.

Caution
-------
These dummy wheels **do not provide any actual functionality**.
They only exist to bypass `pip` dependency resolution issues and allow
`scancode-toolkit` to be installed on Apple Silicon.
