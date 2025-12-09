/**
 * ChordEngine — 4-voice chord synthesizer
 *
 * One note triggers all voices with chord intervals (Maj, Min, Sus4, Power, Maj7, Min7)
 *
 * Features:
 * - 4 voices with selectable waveform and morph control
 * - Selectable chord type (Major, Minor, Sus4, Power, Maj7, Min7)
 * - Detune spread across voices for thicker sound
 * - Glide/portamento with legato support
 * - Filter (LP/HP)
 * - FX
 * - AR amplitude envelope handled by Engine base class
 *
 * Parameters (12 total, matching VALUE_COUNT):
 * 0-1: Attack, Release (from Engine base)
 * 2-11: Body, Chord, Wave, Morph, Voices, Detune, Glide, Cutoff, FX type, FX amount
 */
#pragma once

#include "helpers/math.h"
#include "plugins/audio/MultiEngine/Engine.h"
#include "plugins/audio/utils/valMMfilterCutoff.h"
#include "audio/WavetableGenerator2.h"
#include "audio/MMfilter.h"
#include "audio/MultiFx.h"

#include <array>
#include <cstdlib>

class ChordEngine : public Engine {
protected:
    static constexpr int VOICES = 4;
    WavetableGenerator* wavegens[VOICES] = {nullptr, nullptr, nullptr, nullptr};
    MMfilter filter;
    MultiFx multiFx;

    float phases[VOICES] = {0.0f};
    float currentFreq[VOICES] = {0.0f};
    float targetFreq[VOICES] = {0.0f};
    uint8_t lastNote = 0;   // Last note played (for same-note retrigger check)
    int heldNotes = 0;      // Count of currently held notes

    float glideSpeed = 0.02f; // smoothing factor per sample (higher = faster)
    bool glideEnabled = true;  // false when glide = 0ms
    float velocity = 1.0f;
    
    // Cached values for sample() performance
    int cachedNumVoices = 4;

    // chord definitions: semitone offsets per voice (4 voices)
    static constexpr std::array<std::array<int, VOICES>, 6> chordDefs = {{
        {{0, 4, 7, 12}},   // Major
        {{0, 3, 7, 12}},   // Minor
        {{0, 5, 7, 12}},   // Sus4
        {{0, 7, 12, 19}},  // Power
        {{0, 4, 7, 11}},   // Maj7
        {{0, 3, 7, 10}}    // Min7
    }};

    enum ChordType { Major = 0, Minor = 1, Sus4 = 2, Power = 3, Maj7 = 4, Min7 = 5 };

public:
    // --- Parameters (10 here + 2 from Engine = 12 total) ---
    
    // Pitch & Chord
    Val& body = val(0.0f, "BODY", { .label = "Body", .type = VALUE_CENTERED, .min = -24, .max = 24 }, [&](auto p) {
        p.val.setFloat(p.value);
        setBaseFreq(p.val.get());
    });

    Val& chordType = val(0, "CHORD", { .label = "Chord", .type = VALUE_STRING, .max = 5 }, [&](auto p) {
        p.val.setFloat(p.value);
        static const char* names[] = {"Maj", "Min", "Sus4", "Pwr", "Maj7", "Min7"};
        int idx = CLAMP((int)p.val.get(), 0, 5);
        p.val.setString(std::string(names[idx]));
    });

    // Wave & Morph
    Val& waveType = val(0, "WAVE", { .label = "Wave", .type = VALUE_STRING, .max = (int)WavetableGenerator::Type::COUNT - 1 }, [&](auto p) {
        p.val.setFloat(p.value);
        int idx = (int)p.val.get();
        for (int i = 0; i < VOICES; ++i) {
            if (wavegens[i]) wavegens[i]->setType((WavetableGenerator::Type)idx);
        }
        static const char* waveNames[] = {"Sine", "Saw", "Square", "Tri", "Pulse", "FM", "FMSq"};
        if (idx >= 0 && idx < (int)WavetableGenerator::Type::COUNT) {
            p.val.setString(std::string(waveNames[idx]));
        }
    });

    Val& morph = val(0.0f, "MORPH", { .label = "Morph", .unit = "%" }, [&](auto p) {
        p.val.setFloat(p.value);
        float m = p.val.pct();
        for (int i = 0; i < VOICES; ++i) {
            if (wavegens[i]) wavegens[i]->setMorph(m);
        }
    });

    // Voices & Detune
    Val& voicesVal = val(4, "VOICES", { .label = "Voices", .min = 1, .max = 4, .step = 1.0f }, [&](auto p) {
        p.val.setFloat(p.value);
        cachedNumVoices = (int)p.val.get();
    });

    Val& detune = val(0.0f, "DETUNE", { .label = "Detune", .unit = "%" }, [&](auto p) { 
        p.val.setFloat(p.value); 
    });

    // Glide
    Val& glide = val(50.0f, "GLIDE", { .label = "Glide", .min = 0.0f, .max = 2000.0f, .unit = "ms" }, [&](auto p) {
        p.val.setFloat(p.value);
        float ms = p.val.get();
        if (ms <= 0.0f) {
            glideSpeed = 1.0f; // instant
            glideEnabled = false;
        } else {
            glideSpeed = 1.0f / (ms * 0.001f * props.sampleRate);
            glideEnabled = true;
        }
        glideSpeed = CLAMP(glideSpeed, 0.0001f, 1.0f);
    });

    // Filter (LP/HP cutoff only - resonance removed to fit in 12 params)
    Val& filterCutoff = val(0.0f, "CUTOFF", { .label = "LPF | HPF", .type = VALUE_CENTERED | VALUE_STRING, .min = -100.0, .max = 100.0 }, [&](auto p) {
        valMMfilterCutoff(p, filter);
    });

    // FX
    Val& fxType = val(0, "FX_TYPE", { .label = "FX type", .type = VALUE_STRING, .max = MultiFx::FXType::FX_COUNT - 1 }, multiFx.setFxType);
    Val& fxAmount = val(0, "FX_AMOUNT", { .label = "FX edit", .unit = "%" });

    ChordEngine(AudioPlugin::Props& p, AudioPlugin::Config& c)
        : Engine(p, c, "Chord")
        , multiFx(props.sampleRate, props.lookupTable)
    {
        for (int i = 0; i < VOICES; ++i) {
            wavegens[i] = new WavetableGenerator(p.lookupTable, p.sampleRate);
            wavegens[i]->setType(WavetableGenerator::Type::Sine);
        }

        initValues();
    }

    ~ChordEngine()
    {
        for (int i = 0; i < VOICES; ++i) {
            if (wavegens[i]) delete wavegens[i];
        }
    }

    void sample(float* buf, float envAmpVal) override
    {
        float fxAmt = fxAmount.pct();
        
        if (envAmpVal == 0.0f) {
            buf[track] = multiFx.apply(buf[track], fxAmt);
            return;
        }

        float mix = 0.0f;
        
        // Detune amount: max ~8% spread at 100% for noticeable chorusing
        float detuneAmt = detune.pct() * 0.08f;
        
        // Process all active voices (envelope controls whether we hear them)
        for (int i = 0; i < cachedNumVoices; ++i) {
            // Glide smoothing towards targetFreq
            float delta = targetFreq[i] - currentFreq[i];
            currentFreq[i] += delta * glideSpeed;

            // Apply detune spread: voices spread from -detuneAmt to +detuneAmt
            float voicePos = 0.0f;
            if (cachedNumVoices > 1) {
                voicePos = ((float)i / (cachedNumVoices - 1) - 0.5f) * 2.0f;
            }
            float detuneMultiplier = 1.0f + voicePos * detuneAmt;
            float finalFreq = currentFreq[i] * detuneMultiplier;

            // WavetableGenerator expects freq as ratio to 110Hz
            float freqRatio = finalFreq * (1.0f / 110.0f);
            mix += wavegens[i]->sample(&phases[i], freqRatio);
        }

        // Scale by voice count
        float scale = cachedNumVoices > 0 ? 1.0f / (float)cachedNumVoices : 1.0f;
        float out = mix * scale;
        
        // Apply filter
        out = filter.process(out);
        
        // Apply envelope and velocity
        out = out * envAmpVal * velocity;
        
        // Apply FX
        out = multiFx.apply(out, fxAmt);

        buf[track] = out;
    }

    void noteOn(uint8_t note, float _velocity, void* = nullptr) override
    {
        velocity = _velocity;
        
        // Glide if enabled AND envelope is still active (works with sequencer)
        // If glide = 0ms, always retrigger (no glide)
        bool shouldGlide = glideEnabled && (note != lastNote) && (envelopAmp.get() > 0.01f);

        if (!shouldGlide) {
            // Retrigger envelope when glide disabled or same note
            Engine::noteOn(note, _velocity);
        }
        
        // CRITICAL: Set base frequency from the actual note pressed!
        setBaseFreq(body.get(), note);
        
        int ctype = (int)chordType.get();
        auto offsets = chordDefs[CLAMP(ctype, 0, (int)chordDefs.size() - 1)];

        // Set target frequencies for all voices
        for (int v = 0; v < VOICES; ++v) {
            if (v < cachedNumVoices) {
                float target = baseFreq * powf(2.0f, offsets[v] / 12.0f);
                targetFreq[v] = target;
                // Snap to target and randomize phase if not gliding (prevents pop)
                if (!shouldGlide || currentFreq[v] == 0.0f) {
                    currentFreq[v] = target;
                    phases[v] = ((float)rand() / RAND_MAX);
                }
            }
        }
        
        // Track this note
        lastNote = note;
        heldNotes++;
    }

    void noteOff(uint8_t note, float _velocity, void* userdata = NULL) override
    {
        // Decrement held note count
        if (heldNotes > 0) {
            heldNotes--;
        }
        
        // Release envelope only when ALL notes are released
        if (heldNotes == 0) {
            Engine::noteOff(note, _velocity, userdata);
        }
    }
};
