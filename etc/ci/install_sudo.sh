#!/bin/bash
set -e


if [[ "$1" == "apt-get" ]]; then
    apt-get update -y
    apt-get -o DPkg::Options::="--force-confold" install -y sudo

elif [[ "$1" == "yum" ]]; then
    yum install -y sudo

elif [[ "$1" == "dnf" ]]; then
    dnf install -y sudo

fi
