#!/usr/bin/env python3
"""
ZicBox Wavetable Generator
==========================
Generates wavetable files for the WavetableEngine.

Each wavetable contains 64 single-cycle waveforms, each 2048 samples long.
Total: 64 * 2048 = 131,072 samples per file.

The wavetables morph smoothly from one shape to another, providing
rich sonic possibilities when swept with the WAVE_EDIT parameter.

Usage:
    python generate_wavetables.py [output_dir]
    
Default output: data/audio/wavetables/
"""

import os
import sys
import wave
import struct
import math
from pathlib import Path

# Constants matching ZicBox expectations
WAVEFORMS_PER_TABLE = 64
SAMPLES_PER_WAVEFORM = 2048
SAMPLE_RATE = 48000

def normalize(samples):
    """Normalize samples to [-1, 1] range"""
    max_val = max(abs(min(samples)), abs(max(samples)))
    if max_val > 0:
        return [s / max_val for s in samples]
    return samples

def save_wavetable(filename, all_waveforms):
    """Save wavetable as 32-bit float WAV file"""
    # Flatten all waveforms into single buffer
    samples = []
    for waveform in all_waveforms:
        samples.extend(waveform)
    
    # Convert to 16-bit PCM (ZicBox reads float but 16-bit is more compatible)
    with wave.open(filename, 'w') as wav:
        wav.setnchannels(1)
        wav.setsampwidth(2)  # 16-bit
        wav.setframerate(SAMPLE_RATE)
        
        for sample in samples:
            # Clamp and convert to 16-bit
            clamped = max(-1.0, min(1.0, sample))
            packed = struct.pack('<h', int(clamped * 32767))
            wav.writeframesraw(packed)
    
    print(f"  Created: {filename}")

def generate_sine(phase):
    """Generate sine wave"""
    return math.sin(2 * math.pi * phase)

def generate_saw(phase):
    """Generate sawtooth wave (band-limited approximation)"""
    # Use additive synthesis for band-limiting
    result = 0
    for k in range(1, 32):
        result += ((-1) ** (k+1)) * math.sin(2 * math.pi * k * phase) / k
    return result * 0.5

def generate_square(phase, duty=0.5):
    """Generate square/pulse wave (band-limited)"""
    result = 0
    for k in range(1, 32, 2):  # Odd harmonics only for square
        result += math.sin(2 * math.pi * k * phase) / k
    return result * 0.6

def generate_triangle(phase):
    """Generate triangle wave (band-limited)"""
    result = 0
    for k in range(1, 16):
        n = 2 * k - 1
        result += ((-1) ** (k+1)) * math.sin(2 * math.pi * n * phase) / (n * n)
    return result * 0.8

def generate_pulse(phase, width):
    """Generate pulse wave with variable width"""
    return 1.0 if (phase % 1.0) < width else -1.0

def lerp(a, b, t):
    """Linear interpolation"""
    return a + (b - a) * t

# ============================================================================
# WAVETABLE GENERATORS
# ============================================================================

def generate_basic_shapes():
    """
    Basic Shapes: Morphs through fundamental waveforms
    Sine → Triangle → Saw → Square → Sine
    Great for learning and basic synthesis
    """
    print("Generating: Basic_Shapes.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        t = i / (WAVEFORMS_PER_TABLE - 1)  # 0 to 1
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            
            # 4-way morph: sine→tri→saw→square
            if t < 0.25:
                # Sine to Triangle
                mix = t * 4
                sample = lerp(generate_sine(phase), generate_triangle(phase), mix)
            elif t < 0.5:
                # Triangle to Saw
                mix = (t - 0.25) * 4
                sample = lerp(generate_triangle(phase), generate_saw(phase), mix)
            elif t < 0.75:
                # Saw to Square
                mix = (t - 0.5) * 4
                sample = lerp(generate_saw(phase), generate_square(phase), mix)
            else:
                # Square back to Sine
                mix = (t - 0.75) * 4
                sample = lerp(generate_square(phase), generate_sine(phase), mix)
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_harmonic_series():
    """
    Harmonic Series: Adds harmonics progressively
    Pure sine → Rich harmonics (up to 32 partials)
    Perfect for pads and evolving textures
    """
    print("Generating: Harmonic_Series.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        # Number of harmonics increases with index
        num_harmonics = 1 + int(i * 31 / (WAVEFORMS_PER_TABLE - 1))
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            sample = 0
            
            for h in range(1, num_harmonics + 1):
                # Amplitude decreases with harmonic number
                amp = 1.0 / h
                sample += amp * math.sin(2 * math.pi * h * phase)
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_fm_bells():
    """
    FM Bells: Classic FM synthesis bell tones
    Uses 2-operator FM with varying modulation index
    Inspired by DX7 bell patches
    """
    print("Generating: FM_Bells.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        # Modulation index increases with table position
        mod_index = i * 8.0 / (WAVEFORMS_PER_TABLE - 1)
        # FM ratio for bell-like tones (carrier:modulator)
        ratio = 3.5  # Classic bell ratio
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            
            # 2-operator FM: carrier modulated by modulator
            modulator = math.sin(2 * math.pi * ratio * phase)
            carrier = math.sin(2 * math.pi * phase + mod_index * modulator)
            
            waveform.append(carrier)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_pwm_sweep():
    """
    PWM Sweep: Pulse Width Modulation
    Square wave with duty cycle from 50% to 5%
    Classic analog synth sound
    """
    print("Generating: PWM_Sweep.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        # Duty cycle from 50% down to 5%
        duty = 0.5 - (i * 0.45 / (WAVEFORMS_PER_TABLE - 1))
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            
            # Band-limited pulse using additive synthesis
            sample = 0
            for k in range(1, 32):
                # Pulse wave Fourier series
                coef = math.sin(math.pi * k * duty) / k
                sample += coef * math.sin(2 * math.pi * k * phase)
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_sync_sweep():
    """
    Sync Sweep: Oscillator sync effect
    Simulates hard sync with varying slave frequency
    Creates aggressive, cutting tones
    """
    print("Generating: Sync_Sweep.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        # Sync ratio from 1:1 to 1:8
        sync_ratio = 1.0 + (i * 7.0 / (WAVEFORMS_PER_TABLE - 1))
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            
            # Hard sync: slave resets when master completes cycle
            slave_phase = (phase * sync_ratio) % 1.0
            sample = generate_saw(slave_phase)
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_formant_vowels():
    """
    Formant Vowels: Vocal formant synthesis
    Morphs through A-E-I-O-U vowel sounds
    Great for vocal-like pads and leads
    """
    print("Generating: Formant_Vowels.wav")
    
    # Formant frequencies for vowels (F1, F2, F3) in Hz
    # Normalized to ratios for single-cycle generation
    vowels = {
        'A': [(730, 1.0), (1090, 0.5), (2440, 0.3)],   # "ah"
        'E': [(530, 1.0), (1840, 0.5), (2480, 0.3)],   # "eh" 
        'I': [(270, 1.0), (2290, 0.5), (3010, 0.3)],   # "ee"
        'O': [(570, 1.0), (840, 0.5), (2410, 0.3)],    # "oh"
        'U': [(440, 1.0), (1020, 0.5), (2240, 0.3)],   # "oo"
    }
    
    vowel_order = ['A', 'E', 'I', 'O', 'U', 'A']  # Loop back
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        
        # Determine which vowels to blend
        segment = i / (WAVEFORMS_PER_TABLE - 1) * (len(vowel_order) - 1)
        idx = int(segment)
        blend = segment - idx
        
        if idx >= len(vowel_order) - 1:
            idx = len(vowel_order) - 2
            blend = 1.0
        
        v1 = vowels[vowel_order[idx]]
        v2 = vowels[vowel_order[idx + 1]]
        
        # Interpolate formants
        formants = []
        for f1, f2 in zip(v1, v2):
            freq = lerp(f1[0], f2[0], blend)
            amp = lerp(f1[1], f2[1], blend)
            formants.append((freq, amp))
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            sample = 0
            
            # Generate formant peaks
            base_freq = 100  # Fundamental frequency reference
            for freq, amp in formants:
                ratio = freq / base_freq
                # Create resonant peak using multiple harmonics
                for h in range(-2, 3):
                    harmonic = int(ratio) + h
                    if harmonic > 0:
                        distance = abs(ratio - harmonic)
                        peak_amp = amp * math.exp(-distance * 2)
                        sample += peak_amp * math.sin(2 * math.pi * harmonic * phase) / harmonic
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_supersaw():
    """
    SuperSaw: Layered detuned sawtooth waves
    Morphs from single saw to 7-voice unison
    Classic trance/EDM lead sound (JP-8000 style)
    """
    print("Generating: SuperSaw.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        # Detune amount increases with index
        detune = i * 0.03 / (WAVEFORMS_PER_TABLE - 1)  # Up to 3% detune
        num_voices = 1 + int(i * 6 / (WAVEFORMS_PER_TABLE - 1))  # 1 to 7 voices
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            sample = 0
            
            for v in range(num_voices):
                # Spread voices around center
                voice_detune = (v - (num_voices - 1) / 2) * detune
                voice_phase = phase * (1 + voice_detune)
                sample += generate_saw(voice_phase)
            
            sample /= num_voices
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_noise_shapes():
    """
    Noise Shapes: From pure tone to noise
    Adds increasing amounts of harmonic noise
    Good for industrial/aggressive sounds
    """
    print("Generating: Noise_Shapes.wav")
    waveforms = []
    
    import random
    random.seed(42)  # Reproducible noise
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        noise_amount = i / (WAVEFORMS_PER_TABLE - 1)
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            
            # Base saw wave
            base = generate_saw(phase)
            
            # Add noise harmonics
            noise = 0
            for h in range(1, 64):
                # Random amplitude and slight phase offset
                amp = random.random() * noise_amount / h
                phase_offset = random.random() * 2 * math.pi * noise_amount
                noise += amp * math.sin(2 * math.pi * h * phase + phase_offset)
            
            sample = base * (1 - noise_amount * 0.5) + noise
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_organ():
    """
    Organ: Classic drawbar organ simulation
    Morphs through different drawbar registrations
    Hammond B3 inspired tones
    """
    print("Generating: Organ.wav")
    
    # Drawbar registrations (ratios: sub, fundamental, harmonics...)
    # Each registration is 9 drawbar values (0-8)
    registrations = [
        [0, 8, 0, 0, 0, 0, 0, 0, 0],  # Pure fundamental
        [8, 8, 0, 0, 0, 0, 0, 0, 0],  # With sub
        [8, 8, 8, 0, 0, 0, 0, 0, 0],  # Jazz
        [8, 8, 8, 8, 0, 0, 0, 0, 0],  # Gospel
        [8, 8, 8, 8, 8, 8, 8, 8, 8],  # Full organ
        [0, 0, 8, 8, 0, 0, 0, 0, 8],  # Percussive
        [8, 0, 0, 0, 0, 0, 0, 8, 8],  # Nasal
        [0, 8, 8, 0, 8, 0, 0, 0, 0],  # Smooth
    ]
    
    # Drawbar harmonics (16', 5 1/3', 8', 4', 2 2/3', 2', 1 3/5', 1 1/3', 1')
    harmonic_ratios = [0.5, 1.5, 1, 2, 3, 4, 5, 6, 8]
    
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        
        # Interpolate between registrations
        segment = i / (WAVEFORMS_PER_TABLE - 1) * (len(registrations) - 1)
        idx = int(segment)
        blend = segment - idx
        
        if idx >= len(registrations) - 1:
            idx = len(registrations) - 2
            blend = 1.0
        
        # Blend drawbar values
        drawbars = []
        for d in range(9):
            val = lerp(registrations[idx][d], registrations[idx + 1][d], blend)
            drawbars.append(val / 8.0)  # Normalize to 0-1
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            sample = 0
            
            for d, (ratio, amp) in enumerate(zip(harmonic_ratios, drawbars)):
                if amp > 0:
                    sample += amp * math.sin(2 * math.pi * ratio * phase)
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def generate_acid():
    """
    Acid: TB-303 style resonant sweeps
    Sawtooth with increasing resonance simulation
    Essential for acid house/techno
    """
    print("Generating: Acid.wav")
    waveforms = []
    
    for i in range(WAVEFORMS_PER_TABLE):
        waveform = []
        # Simulate filter resonance by boosting harmonics near cutoff
        resonance = i / (WAVEFORMS_PER_TABLE - 1)
        cutoff_harmonic = 4 + int(resonance * 12)  # Cutoff sweeps up
        
        for j in range(SAMPLES_PER_WAVEFORM):
            phase = j / SAMPLES_PER_WAVEFORM
            sample = 0
            
            for h in range(1, 32):
                base_amp = 1.0 / h
                
                # Resonance peak near cutoff
                distance = abs(h - cutoff_harmonic)
                if distance < 3:
                    resonance_boost = 1.0 + resonance * 4 * math.exp(-distance)
                else:
                    resonance_boost = 1.0
                
                # Simple lowpass rolloff
                if h > cutoff_harmonic:
                    rolloff = math.exp(-(h - cutoff_harmonic) * 0.5)
                else:
                    rolloff = 1.0
                
                amp = base_amp * resonance_boost * rolloff
                sample += amp * math.sin(2 * math.pi * h * phase)
            
            waveform.append(sample)
        
        waveforms.append(normalize(waveform))
    
    return waveforms

def main():
    # Determine output directory
    if len(sys.argv) > 1:
        output_dir = Path(sys.argv[1])
    else:
        # Default to data/audio/wavetables relative to script location
        script_dir = Path(__file__).parent.parent
        output_dir = script_dir / "data" / "audio" / "wavetables"
    
    output_dir.mkdir(parents=True, exist_ok=True)
    
    print(f"ZicBox Wavetable Generator")
    print(f"Output directory: {output_dir}")
    print(f"Format: {WAVEFORMS_PER_TABLE} waveforms × {SAMPLES_PER_WAVEFORM} samples")
    print("-" * 50)
    
    # Generate all wavetables
    generators = [
        ("Basic_Shapes", generate_basic_shapes),
        ("Harmonic_Series", generate_harmonic_series),
        ("FM_Bells", generate_fm_bells),
        ("PWM_Sweep", generate_pwm_sweep),
        ("Sync_Sweep", generate_sync_sweep),
        ("Formant_Vowels", generate_formant_vowels),
        ("SuperSaw", generate_supersaw),
        ("Noise_Shapes", generate_noise_shapes),
        ("Organ", generate_organ),
        ("Acid", generate_acid),
    ]
    
    for name, generator in generators:
        waveforms = generator()
        filename = output_dir / f"{name}.wav"
        save_wavetable(str(filename), waveforms)
    
    print("-" * 50)
    print(f"Generated {len(generators)} wavetable files.")
    print("Ready for use with ZicBox WavetableEngine!")

if __name__ == "__main__":
    main()
