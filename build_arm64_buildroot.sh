#!/bin/bash
BUILDROOT=/home/np/zicBox-build/os/zero2w64/output
CC=$BUILDROOT/host/bin/aarch64-linux-g++
SYSROOT=$BUILDROOT/host/aarch64-buildroot-linux-gnu/sysroot

cd /mnt/e/PiDev/zicBox/plugins/audio
mkdir -p ../../build/obj/pixel_arm64/libs/audio
mkdir -p ../../build/pixel_arm64/libs/audio

echo "Compiling with: $CC"
echo "Sysroot: $SYSROOT"

$CC -c -o ../../build/obj/pixel_arm64/libs/audio/SynthMultiEngine.o audioPlugin.cpp \
    -I../.. -fPIC \
    -DPLUGIN_NAME=SynthMultiEngine \
    -DPLUGIN_INCLUDE='"SynthMultiEngine.h"' \
    --sysroot=$SYSROOT \
    -I$SYSROOT/usr/include \
    --std=c++17 -DIS_RPI=1

if [ $? -ne 0 ]; then
    echo "Compilation failed!"
    exit 1
fi

$CC -shared -o ../../build/pixel_arm64/libs/audio/libzic_SynthMultiEngine.so \
    -I../.. \
    ../../build/obj/pixel_arm64/libs/audio/SynthMultiEngine.o \
    --sysroot=$SYSROOT \
    -L$SYSROOT/usr/lib \
    --std=c++17 \
    -lsndfile

if [ $? -ne 0 ]; then
    echo "Linking failed!"
    exit 1
fi

echo "Build complete!"
file ../../build/pixel_arm64/libs/audio/libzic_SynthMultiEngine.so
