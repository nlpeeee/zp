#!/bin/bash
cd /mnt/e/PiDev/zicBox/plugins/audio
mkdir -p ../../build/obj/pixel_arm64/libs/audio
mkdir -p ../../build/pixel_arm64/libs/audio

aarch64-linux-gnu-g++ -c -o ../../build/obj/pixel_arm64/libs/audio/SynthMultiEngine.o audioPlugin.cpp \
    -I../.. -fPIC \
    -DPLUGIN_NAME=SynthMultiEngine \
    '-DPLUGIN_INCLUDE="SynthMultiEngine.h"' \
    -I/usr/include \
    --std=c++17 -DIS_RPI=1

aarch64-linux-gnu-g++ -shared -o ../../build/pixel_arm64/libs/audio/libzic_SynthMultiEngine.so \
    -I../.. \
    ../../build/obj/pixel_arm64/libs/audio/SynthMultiEngine.o \
    --std=c++17 \
    -lsndfile

echo "Build complete: build/pixel_arm64/libs/audio/libzic_SynthMultiEngine.so"
