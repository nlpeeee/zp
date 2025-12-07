/** Description:
This C++ header defines the blueprint for a specialized digital audio generator called "Wavetable2Engine." This engine is designed to create sound, typically used within a synthesizer or audio plugin.

**Core Functionality:**
The engine operates by combining several key components to produce and shape its sound:

1.  **Wavetable Synthesis:** The primary sound source is a **Wavetable**, which is a collection of pre-defined waveforms (sonic textures). The engine cycles through or "morphs" between these waves to create its unique tone.
2.  **Modulation (LFO):** A dedicated Low-Frequency Oscillator (LFO) is used to automatically vary the wave selection or shape over time, adding subtle or extreme movement to the sound. Users control the LFO’s speed and type.
3.  **Filtering:** The output sound then passes through an audio **Filter**, which controls the brightness (cutoff) and emphasis (resonance) of the tone, allowing the user to create sounds ranging from muffled bass to crisp leads.
4.  **Multi-Effects:** Finally, a dedicated **Multi-Effects** unit applies post-processing, such as reverb or delay, before the sound is outputted.

**User Interaction:**
The engine exposes a set of detailed parameters, giving the user control over every critical aspect, including the fundamental pitch, the speed of the internal LFO, the current wave selection, and all filter and effect settings.

The engine handles the lifecycle of a note, from when it is initially pressed (`noteOn`) to generating the continuous audio signal in real-time by processing samples through these modules.

sha: ded030a608401d33ff47080ae858f2a046e5ac4d54559a60d483dd3175c4349c 
*/
#pragma once

#include "helpers/math.h"
#include "plugins/audio/MultiEngine/Engine.h"
#include "audio/FastWaveform.h"
#include "audio/MMfilter.h"
#include "audio/MultiFx.h"
#include "audio/Wavetable.h"
#include "audio/EnvelopDrumAmp.h"
#include "plugins/audio/utils/valMMfilterCutoff.h"

class Wavetable2Engine : public Engine {
protected:
    MultiFx multiFx;
    Wavetable wavetable;
    MMfilter filter;
    MMfilter antiAliasFilter;  // Pitch-tracking anti-alias filter
    FastWaveform lfo;
    EnvelopDrumAmp envPitch; // For pitch punch at note start

    float velocity = 1.0f;
    float sampleIndexLfo = 0.0f;
    float baseCutoff = 0.5f; // Store base cutoff for envelope modulation
    float antiAliasCutoff = 1.0f;  // Calculated based on pitch
    
    // Wavetable frequency calculation
    // sampleInc = targetFreq * sampleCount / sampleRate
    // Middle C (261.63 Hz) at note 60 is the reference
    static constexpr uint8_t baseNote = 60;
    static constexpr float middleCFreq = 261.63f;
    float freq = 1.0f;  // This becomes sampleInc for the wavetable
    uint8_t freqNote = 60;
    void setFreq(uint8_t note = 0) {
        if (note == 0) note = freqNote;
        freqNote = note;
        // Calculate target frequency in Hz
        float targetFreq = middleCFreq * pow(2.0f, ((note - baseNote + picth.get()) / 12.0f));
        // Convert to sample increment based on actual wavetable size
        freq = targetFreq * wavetable.sampleCount / props.sampleRate;
        
        // Anti-aliasing: reduce high frequencies for higher notes
        // At note 60 (middle C): full bandwidth
        // At note 96 (C7): heavily filtered
        // This prevents harsh aliasing on high notes
        float noteRatio = (float)(note - 36) / 60.0f;  // 0 at C2, 1 at C7
        antiAliasCutoff = 1.0f - noteRatio * 0.7f;  // 1.0 at low notes, 0.3 at high notes
        antiAliasCutoff = CLAMP(antiAliasCutoff, 0.15f, 1.0f);
        antiAliasFilter.setCutoff(antiAliasCutoff);
    }

public:
    // --- 10 parameters ---
    Val& picth = val(0.0f, "PITCH", { .label = "Pitch", .type = VALUE_CENTERED, .min = -32, .max = 32 }, [&](auto p) {
        p.val.setFloat(p.value);
        setFreq(); // Update freq ratio when pitch changes
    });

    Val& lfoRate = val(1.0f, "LFO_RATE", { .label = "LFO Rate", .min = 0.1f, .max = 100.0f, .step = 0.1f, .floatingPoint = 1, .unit = "Hz" }, [&](auto p) {
        p.val.setFloat(p.value);
        lfo.setRate(p.val.get());
        if (p.val.get() < 10.0f && p.val.props().step > 0.1f) {
            p.val.props().step = 0.1f;
            p.val.props().floatingPoint = 1;
        } else if (p.val.get() >= 10.0f && p.val.props().step < 1.0f) {
            p.val.props().step = 1.0f;
            p.val.props().floatingPoint = 0;
        }
    });

    Val& lfoWaveform = val(0, "LFO_WAVEFORM", { .label = "LFO", .type = VALUE_STRING, .max = FastWaveform::TYPE_COUNT - 1 }, [&](auto p) {
        p.val.setFloat(p.value);
        lfo.setType((int)p.val.get());
        p.val.setString(lfo.toString());
    });

    Val& lfoWave = val(0.0f, "LFO_WAVE_MOD", { .label = "Wave. Mod.", .unit = "%" });

    Val& envFilterMod = val(50.0f, "ENV_FILTER_MOD", { .label = "Env>Filter", .unit = "%" });

    Val& wave = val(0, "WAVE", { .label = "Wave", VALUE_STRING }, [&](auto p) {
        p.val.setFloat(p.value);
        int position = p.val.get();
        wavetable.open(position, false);
        p.val.setString(wavetable.fileBrowser.getFileWithoutExtension(position));
        setVal("WAVE_EDIT", 0.0f);
    });

    GraphPointFn graphWave = [&](auto index) { return *wavetable.sample(&index); };
    Val& waveEdit = val(0, "WAVE_EDIT", { .label = "Wave Edit", .type = VALUE_STRING, .min = 1.0, .max = ZIC_WAVETABLE_WAVEFORMS_COUNT, .graph = graphWave }, [&](auto p) {
        p.val.setFloat(p.value);
        wavetable.morph((int)p.val.get() - 1);
        p.val.setString(std::to_string((int)p.val.get()) + "/" + std::to_string(ZIC_WAVETABLE_WAVEFORMS_COUNT));
    });

    Val& cutoff = val(50.0f, "CUTOFF", { .label = "LPF | HPF", .type = VALUE_CENTERED | VALUE_STRING, .min = -100.0, .max = 100.0 }, [&](auto p) {
        valMMfilterCutoff(p, filter);
        // Store base cutoff for envelope modulation
        baseCutoff = (p.value + 100.0f) / 200.0f;
    });

    Val& resonance = val(0.0f, "RESONANCE", { .label = "Resonance", .unit = "%" }, [&](auto p) {
        p.val.setFloat(p.value);
        filter.setResonance(p.val.pct());
    });

    Val& fxType = val(0, "FX_TYPE", { .label = "FX type", .type = VALUE_STRING, .max = MultiFx::FXType::FX_COUNT - 1 }, multiFx.setFxType);

    Val& fxAmount = val(0, "FX_AMOUNT", { .label = "FX edit", .unit = "%" });

    // --- constructor ---
    Wavetable2Engine(AudioPlugin::Props& p, AudioPlugin::Config& c)
        : Engine(p, c, "Wavtabl2")
        , multiFx(props.sampleRate, props.lookupTable)
        , lfo(props.sampleRate)
    {
        initValues();
    }

    void sample(float* buf, float envAmpVal) override
    {
        if (envAmpVal == 0.0f) {
            float out = buf[track];
            out = multiFx.apply(out, fxAmount.pct());
            buf[track] = out;
            return;
        }

        // Pitch envelope for punch (subtle pitch bend at note start)
        float pitchEnv = envPitch.next();
        float pitchMod = 1.0f + pitchEnv * 0.02f; // Max 2% pitch bend

        float modulatedFreq = freq * pitchMod;  // Use ratio-based freq, not Hz

        // LFO for wave modulation (gentler range: max ~8 waveforms sweep)
        float lfoVal = lfo.process();
        // Scale to ±0.125 max (8/64 waveforms), controlled by Wave Mod amount
        float waveMod = lfoWave.pct() > 0.0f ? lfoVal * lfoWave.pct() * 0.125f : 0.0f;

        float out = waveMod != 0.0f 
            ? wavetable.sample(&wavetable.sampleIndex, modulatedFreq, waveMod)
            : wavetable.sample(&wavetable.sampleIndex, modulatedFreq);

        // Apply pitch-tracking anti-alias filter first (always on, reduces harshness)
        out = antiAliasFilter.process(out);

        // Envelope-to-filter modulation: filter tracks envelope
        float envFilterAmount = envFilterMod.pct();
        if (envFilterAmount > 0.01f && cutoff.get() != 0.0f) {
            float envMod = envAmpVal * envFilterAmount;
            float modCutoff;
            if (cutoff.get() > 0.0f) {
                // LPF mode: increase cutoff with envelope
                modCutoff = baseCutoff + (1.0f - baseCutoff) * envMod;
            } else {
                // HPF mode: decrease cutoff intensity with envelope
                modCutoff = baseCutoff * (1.0f - envMod * 0.5f);
            }
            filter.setCutoff(modCutoff);
        }

        out = filter.process(out);
        out = out * envAmpVal * velocity;
        out = multiFx.apply(out, fxAmount.pct());
        buf[track] = out;
    }

    void noteOn(uint8_t note, float _velocity, void* = nullptr) override
    {
        Engine::noteOn(note, _velocity);
        velocity = _velocity;
        setFreq(note);  // Calculate ratio-based frequency
        wavetable.sampleIndex = 0;
        sampleIndexLfo = 0.0f;
        envPitch.reset(props.sampleRate * 0.15f); // 150ms pitch envelope decay
    }
};
