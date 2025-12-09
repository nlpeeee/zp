#include "plugins/audio/MultiEngine/ChordEngine.h"
#include "audio/lookupTable.h"
#include <iostream>

int main()
{
    LookupTable lookupTable;
    AudioPlugin::Props props = {
        .sampleRate = 44100,
        .channels = 2,
        .audioPluginHandler = nullptr,
        .maxTracks = 16,
        .lookupTable = &lookupTable,
    };

    nlohmann::json synthJson = nlohmann::json::object();
    AudioPlugin::Config cfg = { std::string("chordEngineTest"), synthJson, 0 };
    ChordEngine synth(props, cfg);

    float buffer[16] = {0.0f};

    const int totalSamples = props.sampleRate * 2; // 2 seconds
    const int retrigInterval = 200; // samples (~4.5ms)

    int nextTrigger = 0;
    float prev = 0.0f;
    float maxDelta = 0.0f;

    for (int i = 0; i < totalSamples; ++i) {
        if (i >= nextTrigger) {
            synth.noteOn(60, 1.0f);
            nextTrigger = i + retrigInterval;
        }
        ((Engine&)synth).sample(buffer);
        float out = buffer[0];
        float d = fabs(out - prev);
        if (d > maxDelta) maxDelta = d;
        prev = out;
    }

    std::cout << "Max per-sample delta (ChordEngine): " << maxDelta << std::endl;
    return 0;
}
