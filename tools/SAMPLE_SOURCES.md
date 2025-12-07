# ZicPixel CC0 Sample Sources - Curated List
# ===========================================
# 
# These are verified CC0/Public Domain sample packs you can download manually.
# All links are to legal, free-to-use samples with no attribution required.
#
# Download the samples and place them in: data/audio/samples/

## ESSENTIAL DRUM MACHINES (CC0)
## -----------------------------

### Roland TR-808 Samples
- https://archive.org/details/Roland_TR-808_Samples
  - Classic 808 kicks, snares, hihats, toms, claps
  - Perfect for: Hip-hop, House, Techno, Trap

### Roland TR-909 Samples  
- https://archive.org/details/Roland_TR-909_Drum_Samples
  - Essential for House and Techno
  - Punchy kicks, crisp hihats, iconic claps

### LinnDrum Samples
- https://archive.org/details/LinnDrum_Samples
  - 80s drum machine sounds
  - Great for: Synthwave, Pop, Electro


## GENRE PACKS (CC0/Public Domain)
## -------------------------------

### House / Disco
- Freesound Pack: Piano House Chords
  https://freesound.org/people/Tristan_Lohengrin/packs/20379/
  
- Freesound: Disco Samples  
  Search: https://freesound.org/search/?q=disco&f=license:%22Creative+Commons+0%22

### Jungle / DnB
- The Amen Break (Public Domain discussion - widely considered fair use)
  - Most jungle relies on classic breaks
  
- Freesound: Breakbeat Collection
  https://freesound.org/search/?q=breakbeat+loop&f=license:%22Creative+Commons+0%22

### Techno / Industrial
- Freesound: Industrial Sounds
  https://freesound.org/search/?q=industrial+hit&f=license:%22Creative+Commons+0%22
  
- Noise Engineering (some free CC0 packs)
  https://noiseengineering.us/pages/samples

### Ambient / Textures
- NASA Sound Library (Public Domain)
  https://www.nasa.gov/connect/sounds/index.html
  - Space sounds, mission audio, ambient textures
  
- Freesound: Field Recordings
  https://freesound.org/search/?q=field+recording&f=license:%22Creative+Commons+0%22


## VOCAL SAMPLES (CC0)
## -------------------

### Vocal Chops
- Freesound CC0 Vocals
  https://freesound.org/search/?q=vocal+chop&f=license:%22Creative+Commons+0%22
  
- Freesound: Female Vocals
  https://freesound.org/search/?q=female+vocal&f=license:%22Creative+Commons+0%22

### Spoken Word
- LibriVox Public Domain Audiobooks
  https://librivox.org/
  - Cut your own vocal samples from classic literature readings


## FX & RISERS (CC0)
## -----------------

- Freesound: Risers and Sweeps
  https://freesound.org/search/?q=riser+sweep&f=license:%22Creative+Commons+0%22

- Freesound: Impacts
  https://freesound.org/search/?q=impact+hit&f=license:%22Creative+Commons+0%22


## INSTRUMENT HITS (CC0)
## ---------------------

### Piano
- Salamander Grand Piano (CC0)
  https://sfzinstruments.github.io/pianos/salamander
  - Extract individual note WAVs for chord stabs

### Orchestra
- VSCO Community Orchestra (CC0)
  https://vis.versilstudios.com/vsco-community.html
  - Strings, brass, woodwinds

### Vintage Synths
- Freesound: Synth Stabs
  https://freesound.org/search/?q=synth+stab&f=license:%22Creative+Commons+0%22


## QUICK START RECOMMENDATIONS
## ---------------------------

For a minimal but versatile sample library, download:

1. **808 Kit** - Archive.org TR-808 (kicks, snares, hats)
2. **909 Kit** - Archive.org TR-909 (house/techno essentials)  
3. **One breakbeat loop** - For jungle/dnb
4. **Piano chord stabs** - Freesound search
5. **A few vocal chops** - Freesound CC0 vocals
6. **Riser + Impact FX** - Freesound

This gives you ~50 samples covering most genres in under 20MB.


## FOLDER STRUCTURE
## ----------------

Organize your downloads like this:

data/audio/samples/
├── 808/
│   ├── kick.wav
│   ├── snare.wav
│   └── hihat.wav
├── 909/
│   ├── kick.wav
│   └── clap.wav
├── breaks/
│   ├── amen.wav
│   └── funky.wav
├── chords/
│   ├── piano_Cmaj.wav
│   └── organ_stab.wav
├── vocals/
│   ├── yeah.wav
│   └── chop1.wav
└── fx/
    ├── riser.wav
    └── impact.wav


## BATCH DOWNLOAD COMMANDS
## -----------------------

# Using wget to download from Archive.org 808 pack:
wget -r -np -nH --cut-dirs=2 -R "index.html*" \
  "https://archive.org/download/Roland_TR-808_Samples/"

# Using curl for individual files:
curl -O "https://archive.org/download/Roland_TR-808_Samples/kick.wav"


## CONVERT MP3 TO WAV (if needed)
## ------------------------------

# Using ffmpeg (single file):
ffmpeg -i input.mp3 -ar 48000 -ac 1 output.wav

# Batch convert all MP3s in a folder:
for f in *.mp3; do ffmpeg -i "$f" -ar 48000 -ac 1 "${f%.mp3}.wav"; done

# PowerShell (Windows):
Get-ChildItem *.mp3 | ForEach-Object { 
  ffmpeg -i $_.FullName -ar 48000 -ac 1 ($_.FullName -replace '\.mp3$','.wav')
}
