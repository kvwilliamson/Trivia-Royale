#!/usr/bin/env python3
"""
Generate Sound Effects for Trivia Royale
Creates simple sound effects using numpy and scipy
"""

import numpy as np
from scipy.io import wavfile
import os

# Create output directory
os.makedirs("assets/audio/sfx", exist_ok=True)

def generate_sine_wave(frequency, duration, sample_rate=44100, amplitude=0.3):
    """Generate a sine wave"""
    t = np.linspace(0, duration, int(sample_rate * duration))
    wave = amplitude * np.sin(2 * np.pi * frequency * t)
    return wave

def apply_envelope(wave, attack=0.01, decay=0.05, sustain=0.7, release=0.1, sample_rate=44100):
    """Apply ADSR envelope to wave"""
    total_samples = len(wave)
    attack_samples = int(attack * sample_rate)
    decay_samples = int(decay * sample_rate)
    release_samples = int(release * sample_rate)
    sustain_samples = total_samples - attack_samples - decay_samples - release_samples
    
    # Create envelope
    envelope = np.ones(total_samples)
    
    # Attack
    if attack_samples > 0:
        envelope[:attack_samples] = np.linspace(0, 1, attack_samples)
    
    # Decay
    if decay_samples > 0:
        envelope[attack_samples:attack_samples + decay_samples] = np.linspace(1, sustain, decay_samples)
    
    # Sustain
    envelope[attack_samples + decay_samples:attack_samples + decay_samples + sustain_samples] = sustain
    
    # Release
    if release_samples > 0:
        envelope[-release_samples:] = np.linspace(sustain, 0, release_samples)
    
    return wave * envelope

def save_wav(filename, wave, sample_rate=44100):
    """Save wave to WAV file"""
    # Normalize and convert to int16
    wave = np.clip(wave, -1, 1)
    wave = (wave * 32767).astype(np.int16)
    wavfile.write(filename, sample_rate, wave)
    print(f"✓ Created: {filename}")

# 1. Button Click Sound
def create_button_click():
    freq1 = generate_sine_wave(800, 0.05)
    freq2 = generate_sine_wave(1200, 0.05)
    click = (freq1 + freq2) / 2
    click = apply_envelope(click, attack=0.001, decay=0.02, sustain=0.3, release=0.03)
    save_wav("assets/audio/sfx/button_click.wav", click)

# 2. Correct Answer Sound (triumphant)
def create_correct_answer():
    # Major chord: C-E-G (ascending)
    frequencies = [523.25, 659.25, 783.99]  # C5, E5, G5
    duration = 0.3
# 2. Correct Answer Sound (triumphant)
def create_correct_answer():
    # Major chord: C-E-G (ascending)
    frequencies = [523.25, 659.25, 783.99]  # C5, E5, G5
    duration = 0.4
    sample_rate = 44100
    
    waves = []
    for i, freq  in enumerate(frequencies):
        delay = i * 0.1
        note_duration = 0.2
        note = generate_sine_wave(freq, note_duration, sample_rate=sample_rate, amplitude=0.2)
        note = apply_envelope(note, attack=0.01, decay=0.05, sustain=0.7, release=0.1, sample_rate=sample_rate)
        # Add delay
        delay_samples = int(sample_rate * delay)
        note = np.concatenate([np.zeros(delay_samples), note])
        waves.append(note)
    
    # Find max length and pad all waves
    max_len = max(len(w) for w in waves)
    wave = np.zeros(max_len)
    for w in waves:
        wave[:len(w)] += w
    
    save_wav("assets/audio/sfx/correct_answer.wav", wave)

# 3. Wrong Answer Sound (buzzer)
def create_wrong_answer():
    # Descending dissonant notes
    wave1 = generate_sine_wave(200, 0.4)
    wave2 = generate_sine_wave(185, 0.4)
    buzzer = (wave1 + wave2) / 2
    buzzer = apply_envelope(buzzer, attack=0.01, decay=0.1, sustain=0.7, release=0.1)
    save_wav("assets/audio/sfx/wrong_answer.wav", buzzer)

# 4. Round Transition Sound (whoosh)
def create_round_transition():
    # Sweep from low to high
    duration = 0.6
    sample_rate = 44100
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Frequency sweep from 200 to 1000 Hz
    freq = 200 + (800 * (t / duration))
    phase = 2 * np.pi * np.cumsum(freq) / sample_rate
    sweep = 0.4 * np.sin(phase)
    
    # Apply envelope
    envelope = np.exp(-3 * t / duration)
    sweep = sweep * envelope
    
    save_wav("assets/audio/sfx/round_transition.wav", sweep)

# 5. Achievement Unlock Sound
def create_achievement():
    # Bright ascending arpeggio
    frequencies = [523.25, 659.25, 783.99, 1046.50]  # C5, E5, G5, C6
    duration = 0.6
    sample_rate = 44100
    
    waves = []
    for i, freq in enumerate(frequencies):
        delay = i * 0.08
        note_duration = 0.2
        note = generate_sine_wave(freq, note_duration, sample_rate=sample_rate, amplitude=0.2)
        note = apply_envelope(note, attack=0.005, decay=0.05, sustain=0.6, release=0.1, sample_rate=sample_rate)
        # Add delay
        delay_samples = int(sample_rate * delay)
        note = np.concatenate([np.zeros(delay_samples), note])
        waves.append(note)
    
    # Find max length and combine
    max_len = max(len(w) for w in waves)
    wave = np.zeros(max_len)
    for w in waves:
        wave[:len(w)] += w
    
    save_wav("assets/audio/sfx/achievement.wav", wave)

# 6. Score Change Sound (subtle ping)
def create_score_change():
    # Quick musical note
    wave = generate_sine_wave(880, 0.15)  # A5
    wave = apply_envelope(wave, attack=0.005, decay=0.03, sustain=0.6, release=0.08)
    save_wav("assets/audio/sfx/score_change.wav", wave)

# 7. Timer Tick Sound
def create_timer_tick():
    wave = generate_sine_wave(1200, 0.05)
    wave = apply_envelope(wave, attack=0.001, decay=0.01, sustain=0.5, release=0.02)
    save_wav("assets/audio/sfx/timer_tick.wav", wave)

# 8. Timer Warning Sound (urgent)
def create_timer_warning():
    wave1 = generate_sine_wave(800, 0.15)
    wave2 = generate_sine_wave(950, 0.15)
    warning = (wave1 + wave2) / 2
    warning = apply_envelope(warning, attack=0.005, decay=0.02, sustain=0.8, release=0.05)
    save_wav("assets/audio/sfx/timer_warning.wav", warning)

if __name__ == "__main__":
    print("🎵 Generating sound effects for Trivia Royale...\n")
    
    try:
        create_button_click()
        create_correct_answer()
        create_wrong_answer()
        create_round_transition()
        create_achievement()
        create_score_change()
        create_timer_tick()
        create_timer_warning()
        
        print("\n✅ All sound effects generated successfully!")
        print(f"📁 Saved to: assets/audio/sfx/")
        
    except Exception as e:
        print(f"\n❌ Error generating sound effects: {e}")
        print("   Make sure scipy is installed: pip install scipy")
