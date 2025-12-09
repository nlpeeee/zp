#!/bin/bash
set -e

# Root and output directories
ROOT="/mnt/e/PiDev/zicBox"
OUT="$ROOT/build/pixel_arm64"
OBJ="$ROOT/build/obj/pixel_arm64"

mkdir -p "$OUT/libs/audio" "$OUT/libs/components" "$OBJ/libs/audio" "$OBJ/libs/components"

# List of concrete plugin headers to build
PLUGINS=(SynthMultiEngine EffectGainVolume SynthFM2 SynthKick23 SynthBass SynthMetalic SynthMonoSample SynthMulti SynthMultiDrum SynthMultiSample SynthSample SynthWavetable)

for name in "${PLUGINS[@]}"; do
    hdr="$ROOT/plugins/audio/$name.h"
    if [ -f "$hdr" ]; then
        echo "Building audio plugin: $name"
        aarch64-linux-gnu-g++ -c -o "$OBJ/libs/audio/$name.o" "$ROOT/plugins/audio/audioPlugin.cpp" \
            -I"$ROOT" -fPIC \
            -DPLUGIN_NAME="$name" \
            "-DPLUGIN_INCLUDE=\"$name.h\"" \
            -I/usr/include --std=c++17 -DIS_RPI=1
        aarch64-linux-gnu-g++ -shared -o "$OUT/libs/audio/libzic_$name.so" \
            -I"$ROOT" "$OBJ/libs/audio/$name.o" --std=c++17 -lsndfile
    fi
done

# Build Pixel UI components (example, adjust as needed)
# if [ -d "$ROOT/plugins/components" ]; then
#     for hdr in $ROOT/plugins/components/*.h; do
#         name=$(basename "$hdr" .h)
#         if grep -q "class $name" "$hdr"; then
#             echo "Building component: $name"
#             aarch64-linux-gnu-g++ -c -o "$OBJ/libs/components/$name.o" "$ROOT/plugins/components/componentPlugin.cpp" \
#                 -I"$ROOT" -fPIC \
#                 -DPLUGIN_NAME="$name" \
#                 "-DPLUGIN_INCLUDE=\"$name.h\"" \
#                 -I/usr/include --std=c++17 -DIS_RPI=1
#             aarch64-linux-gnu-g++ -shared -o "$OUT/libs/components/libzic_$name.so" \
#                 -I"$ROOT" "$OBJ/libs/components/$name.o" --std=c++17
#         fi
#     done
# fi

# Build main executable (if needed)
# aarch64-linux-gnu-g++ -o "$OUT/zic" ...main sources...

echo "Full ARM64 build complete: $OUT"
