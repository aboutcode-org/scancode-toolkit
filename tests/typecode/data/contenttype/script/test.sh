#!/bin/sh

if [ "$1" == "-h" ]; then
    echo Hello
    exit
else
    echo Goodbye
    exit -1
fi