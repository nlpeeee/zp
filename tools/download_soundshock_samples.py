#!/usr/bin/env python3
"""
ZicPixel Sample Downloader - SoundShockAudio Edition
Downloads free sample packs from SoundShockAudio's curated collection.

These are royalty-free sample packs organized by genre.
Source: https://soundshockaudio.com/free-samples-loops/

Usage:
    python download_soundshock_samples.py              # Download all packs
    python download_soundshock_samples.py --list       # List available packs
    python download_soundshock_samples.py --genre house techno  # Specific genres
    python download_soundshock_samples.py --dry        # Show what would download
"""

import os
import sys
import argparse
import urllib.request
import ssl
import zipfile
import shutil
from pathlib import Path

# Allow older SSL for compatibility
ssl._create_default_https_context = ssl._create_unverified_context

SCRIPT_DIR = Path(__file__).parent.parent
SAMPLES_DIR = SCRIPT_DIR / "data" / "audio" / "samples"

# =============================================================================
# CURATED SAMPLE PACKS FROM SOUNDSHOCKAUDIO
# Direct download links to royalty-free sample packs
# =============================================================================

SAMPLE_PACKS = {
    # =========================================================================
    # DRUMS - Essential drum kits for all genres
    # =========================================================================
    "drums": {
        "description": "Essential drum kits - kicks, snares, hats, percussion",
        "packs": [
            {
                "name": "Roland MC-505 808 Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Roland_MC-505-%20808_Kit.zip",
                "samples": 64,
                "size": "12.5 MB",
                "description": "Classic 808 sounds from Roland MC-505"
            },
            {
                "name": "80s Retro Futuristic Drums",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/80s--Retro-Furutistic-Drum-Pack.zip",
                "samples": 307,
                "size": "84 MB",
                "description": "LinnDrum-style 80s drums, gated reverb snares"
            },
            {
                "name": "Unison Essential Drum Loops",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Unison%2BEssential%2BDrum%2BLoops.zip",
                "samples": 12,
                "size": "19 MB",
                "description": "Versatile drum loops for hip-hop to electronic"
            },
            {
                "name": "Golden Hour Drum Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Golden-Hour-Drum-Kit.zip",
                "samples": 165,
                "size": "302 MB",
                "description": "Warm punchy drums for house and chill"
            },
            {
                "name": "Jazz Drum Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Jazz_Drum_Kit.zip",
                "samples": 17,
                "size": "724 KB",
                "description": "Live jazz drum sounds with natural resonance"
            },
            {
                "name": "Analog Supplies Vol 1",
                "url": "https://free-sample-packs-direct-download-ssa-site.us-ord-1.linodeobjects.com/Analog_Supplies_Vol._1.zip",
                "samples": 66,
                "size": "190 MB",
                "description": "Vintage hardware drum samples"
            },
        ]
    },

    # =========================================================================
    # TECHNO - Hard-hitting electronic drums and loops
    # =========================================================================
    "techno": {
        "description": "Techno - Hard kicks, industrial percussion, driving beats",
        "packs": [
            {
                "name": "Techno Essentials 2022",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Free-Techno-Supplements-2022-Essentials-Sample-Pack.zip",
                "samples": 303,
                "size": "237 MB",
                "description": "Punchy kicks, deep bass, synth loops, pads"
            },
            {
                "name": "Hard Techno Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Bluezone_Corporation_Free_Hard_Techno_Sample_Pack.zip",
                "samples": 13,
                "size": "24 MB",
                "description": "Aggressive basslines, razor-sharp synths"
            },
            {
                "name": "Techno Sample Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Bluezone_Corporation_Free_Techno_Sample_Pack.zip",
                "samples": 11,
                "size": "21 MB",
                "description": "Punchy drums, resonant basslines"
            },
            {
                "name": "Free Techno Drums",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Free-Techno-Drums.zip",
                "samples": 102,
                "size": "43 MB",
                "description": "Booming kicks, crisp hats, snappy snares"
            },
        ]
    },

    # =========================================================================
    # HOUSE - 4/4 grooves, deep bass, piano stabs
    # =========================================================================
    "house": {
        "description": "House - 4/4 beats, deep grooves, piano, organs",
        "packs": [
            {
                "name": "House Drum Loops",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/House_Drum_Loops.zip",
                "samples": 100,
                "size": "102 MB",
                "description": "Classic house rhythms, punchy kicks, crisp hats"
            },
            {
                "name": "Stadium House",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Stadium-House-Samples.zip",
                "samples": 161,
                "size": "105 MB",
                "description": "Anthemic sounds, soaring synths, massive bass"
            },
            {
                "name": "Trends 2021",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Trends_2021.zip",
                "samples": 319,
                "size": "778 MB",
                "description": "Modern house with basslines, drums, vocals"
            },
        ]
    },

    # =========================================================================
    # HIP-HOP - Boom bap, trap, 808s
    # =========================================================================
    "hiphop": {
        "description": "Hip-Hop & Trap - 808s, boom bap, hard-hitting drums",
        "packs": [
            {
                "name": "Murda Beatz Type Drum Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/BVKER-Butterfly-Hip-Hop-Drum-Kit.zip",
                "samples": 94,
                "size": "23 MB",
                "description": "Hard-hitting drums, punchy kicks, crisp snares"
            },
            {
                "name": "Nick Mira Inspired Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/wavbvkery-dreams-hip-hop-drum-kit.zip",
                "samples": 90,
                "size": "16 MB",
                "description": "Punchy kicks, snappy snares, lush 808s"
            },
            {
                "name": "Travis Scott Drum Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Travis-Scott-Drum-Kit.zip",
                "samples": 115,
                "size": "47 MB",
                "description": "Punchy kicks, deep 808s, atmospheric loops"
            },
            {
                "name": "Uzi Hip Hop Sample Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/UziHipHop-Sample-Pack.zip",
                "samples": 90,
                "size": "101 MB",
                "description": "Hard drums, powerful 808s, creative FX"
            },
            {
                "name": "Scott Storch Drum Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Scott_Storch_Drum_Kit.zip",
                "samples": 688,
                "size": "31 MB",
                "description": "Iconic hip-hop producer sounds"
            },
            {
                "name": "Dr Dre Sound Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Dr-Dre-Sound-Pack.zip",
                "samples": 189,
                "size": "26 MB",
                "description": "West Coast G-Funk vibes"
            },
            {
                "name": "Hip Hop and Trap Samples",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Ghosthack_-_Hip_Hop_and_Trap_Freebie.zip",
                "samples": 50,
                "size": "35 MB",
                "description": "Drum kits, 808s, melodic loops"
            },
            {
                "name": "Smoked Out Sound Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/smoked-out-sound-kit.zip",
                "samples": 92,
                "size": "4 MB",
                "description": "Gritty raw hip-hop drums"
            },
            {
                "name": "Chaos Part 1",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/CHAOS_Part_1.zip",
                "samples": 55,
                "size": "282 MB",
                "description": "Heavy kicks, orchestral melodies, lofi vibes"
            },
        ]
    },

    # =========================================================================
    # DRUM & BASS - Fast breaks, heavy bass
    # =========================================================================
    "dnb": {
        "description": "Drum & Bass - Fast breaks, neuro bass, jungle",
        "packs": [
            {
                "name": "Experimental Breaks",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Experimental-Breaks-Samples.zip",
                "samples": 282,
                "size": "173 MB",
                "description": "Unconventional drum breaks, intricate rhythms"
            },
            {
                "name": "Atomic DnB Loops",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Atomic-Drum-and-Bass-Loops.zip",
                "samples": 60,
                "size": "68 MB",
                "description": "High-energy drum loops, pulsating basslines"
            },
            {
                "name": "Neuro DnB",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Tekvision_Neuro%20DnB.zip",
                "samples": 48,
                "size": "58 MB",
                "description": "Gritty basslines, dark atmospheres"
            },
            {
                "name": "Neuro Bass Tools",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Neuro_Bass_Tools.zip",
                "samples": 20,
                "size": "19 MB",
                "description": "Aggressive neuro bass loops"
            },
        ]
    },

    # =========================================================================
    # AMBIENT - Pads, atmospheres, textures
    # =========================================================================
    "ambient": {
        "description": "Ambient - Atmospheric pads, textures, soundscapes",
        "packs": [
            {
                "name": "Atmospheric Pads Vol 1",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Berx_Atmospheric_Pads.zip",
                "samples": 50,
                "size": "589 MB",
                "description": "Lush ethereal pad sounds"
            },
            {
                "name": "Aurora Atmospheres Vol 1",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Euphoric-Wave-Aurora-Atmospheres-Vol-1.zip",
                "samples": 48,
                "size": "690 MB",
                "description": "Lush pads, ethereal textures"
            },
            {
                "name": "Ambience Sound Effects",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Ambience_Sound_Effects.zip",
                "samples": 15,
                "size": "96 MB",
                "description": "Natural and urban ambient sounds"
            },
            {
                "name": "Ambient Sample Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Bluezone_Corporation_Free_Ambient_Sample_Pack.zip",
                "samples": 11,
                "size": "97 MB",
                "description": "Lush pads, drones, field recordings"
            },
        ]
    },

    # =========================================================================
    # GARAGE - UK Garage, 2-step
    # =========================================================================
    "garage": {
        "description": "UK Garage - 2-step rhythms, shuffled beats, deep bass",
        "packs": [
            {
                "name": "Dark Garage and Dubstep",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/garagedubstep_mini.zip",
                "samples": 11,
                "size": "17 MB",
                "description": "Gritty textures, heavy drums"
            },
            {
                "name": "Garage Sessions Vol 3",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Garage_Sessions_Vol_3.zip",
                "samples": 238,
                "size": "271 MB",
                "description": "Classic UK garage, punchy drums, deep bass"
            },
            {
                "name": "UK Garage Samples",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/musicradar-uk-garage-samples.zip",
                "samples": 316,
                "size": "165 MB",
                "description": "Classic UK garage drums, bass, synths"
            },
            {
                "name": "Emotional Garage",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/EmotionalGarage_Mini_SP.zip",
                "samples": 10,
                "size": "38 MB",
                "description": "Lush pads, vocal chops, punchy drums"
            },
        ]
    },

    # =========================================================================
    # LOFI - Dusty drums, vinyl crackle, warm tones
    # =========================================================================
    "lofi": {
        "description": "Lo-Fi - Dusty drums, vinyl crackle, warm nostalgic tones",
        "packs": [
            {
                "name": "Daydreaming Lo-Fi StarterKit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Daydreaming-The-Ultimate-Lo-Fi-StarterKit.zip",
                "samples": 67,
                "size": "177 MB",
                "description": "Dreamy textures, soft piano, vinyl samples"
            },
            {
                "name": "Lunar Lo-Fi Sample Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Lunar-Lo-Fi-Sample-Pack.zip",
                "samples": 120,
                "size": "222 MB",
                "description": "Warm drum loops, melancholic melodies"
            },
            {
                "name": "Eternity Vintage Collection",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Eternity_Vintage_Collection.zip",
                "samples": 467,
                "size": "984 MB",
                "description": "Dusty samples, vintage keys, soulful guitars"
            },
            {
                "name": "Lofi Toolkit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/CymaticsLofiToolkit-V1-m2d.zip",
                "samples": 184,
                "size": "228 MB",
                "description": "Crunchy drums, lush keys, soulful melodies"
            },
        ]
    },

    # =========================================================================
    # TRAP - 808s, hi-hat rolls, dark melodies
    # =========================================================================
    "trap": {
        "description": "Trap - 808s, hi-hat rolls, dark melodies",
        "packs": [
            {
                "name": "Free Dose Sample Loops",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/FREE.DOSE.SAMPLE.PACK.zip",
                "samples": 276,
                "size": "396 MB",
                "description": "Drum loops, melodic loops, punchy 808s"
            },
            {
                "name": "Trap Starter Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Trap-Starter-Pack.zip",
                "samples": 180,
                "size": "225 MB",
                "description": "Powerful 808s, crisp hi-hats, melodies"
            },
            {
                "name": "Trap Melody Loop Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Trap-Melody-Loop-Pack.zip",
                "samples": 34,
                "size": "80 MB",
                "description": "Catchy melodies, lush pads, bells"
            },
            {
                "name": "Dredhok Hybrid Trap",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Dredhok-Hybrid-Trap-Sample-Pack.zip",
                "samples": 108,
                "size": "59 MB",
                "description": "Aggressive synths, earth-shattering 808s"
            },
            {
                "name": "Pyrex Trap Sound Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/pyrex_trap_sound_pack.zip",
                "samples": 237,
                "size": "184 MB",
                "description": "Crispy hi-hats, booming 808s, dark loops"
            },
        ]
    },

    # =========================================================================
    # DUBSTEP - Heavy bass, wobbles, drops
    # =========================================================================
    "dubstep": {
        "description": "Dubstep - Heavy bass, wobbles, massive drops",
        "packs": [
            {
                "name": "Dubstep Pack 7",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Ghosthack_-_Dubstep_and_Trap_Pack_7.zip",
                "samples": 60,
                "size": "51 MB",
                "description": "Deep bass hits, synth stabs, punchy drums"
            },
            {
                "name": "Dubstep Bass Loops and Hits",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Dubstep_Bass_Loops_%26_Hits_by_Ghosthack.zip",
                "samples": 30,
                "size": "52 MB",
                "description": "Growling subs, punchy mid-range basses"
            },
            {
                "name": "Apashe Sample Pack",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Apashe-Sample-Pack.zip",
                "samples": 10,
                "size": "55 MB",
                "description": "Cinematic bass, epic brass, intense strings"
            },
            {
                "name": "Dubstep Empire Drum Kit",
                "url": "https://downloads.soundshockaudio.com/file/VST-Plugins-On-SSA-Site/Dubstep_Empire_Drum_Kit.zip",
                "samples": 1393,
                "size": "128 MB",
                "description": "Heavy drums, deep kicks, powerful claps"
            },
        ]
    },
}


def download_file(url: str, dest_path: Path) -> bool:
    """Download a file from URL to destination path."""
    try:
        print(f"  ↓ Downloading {dest_path.name}...", end=" ", flush=True)
        
        req = urllib.request.Request(
            url,
            headers={
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
            }
        )
        
        with urllib.request.urlopen(req, timeout=120) as response:
            with open(dest_path, 'wb') as f:
                shutil.copyfileobj(response, f)
        
        print("✓")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def extract_zip(zip_path: Path, extract_to: Path) -> bool:
    """Extract a zip file to the specified directory, skipping problematic files."""
    try:
        print(f"  📦 Extracting...", end=" ", flush=True)
        
        with zipfile.ZipFile(zip_path, 'r') as zf:
            for member in zf.namelist():
                # Skip macOS resource files that cause issues on Windows
                if 'Icon\r' in member or member.startswith('__MACOSX') or '.DS_Store' in member:
                    continue
                
                # Sanitize filename for Windows
                safe_name = member.replace('\r', '').replace(':', '-')
                
                try:
                    # Extract to sanitized path
                    source = zf.read(member)
                    target_path = extract_to / safe_name
                    
                    if member.endswith('/'):
                        target_path.mkdir(parents=True, exist_ok=True)
                    else:
                        target_path.parent.mkdir(parents=True, exist_ok=True)
                        target_path.write_bytes(source)
                except Exception:
                    # Skip any problematic files
                    continue
        
        # Remove the zip file after extraction
        zip_path.unlink()
        
        print("✓")
        return True
        
    except Exception as e:
        print(f"✗ Error: {e}")
        return False


def list_packs():
    """List all available sample packs."""
    print("\n" + "=" * 60)
    print("  AVAILABLE SAMPLE PACKS FROM SOUNDSHOCKAUDIO")
    print("=" * 60)
    
    total_samples = 0
    total_packs = 0
    
    for genre, data in SAMPLE_PACKS.items():
        print(f"\n{genre.upper()}")
        print(f"  {data['description']}")
        print("-" * 50)
        
        for pack in data["packs"]:
            total_packs += 1
            total_samples += pack["samples"]
            print(f"  • {pack['name']}")
            print(f"    {pack['samples']} samples, {pack['size']}")
            print(f"    {pack['description']}")
    
    print("\n" + "=" * 60)
    print(f"  TOTAL: {total_packs} packs, ~{total_samples} samples")
    print("=" * 60)


def download_genre(genre: str, dry_run: bool = False) -> tuple[int, int]:
    """Download all packs for a specific genre."""
    if genre not in SAMPLE_PACKS:
        print(f"Unknown genre: {genre}")
        return 0, 0
    
    data = SAMPLE_PACKS[genre]
    genre_dir = SAMPLES_DIR / genre
    
    print(f"\n{'=' * 60}")
    print(f"  {genre.upper()}")
    print(f"  {data['description']}")
    print(f"{'=' * 60}")
    
    downloaded = 0
    skipped = 0
    
    for pack in data["packs"]:
        pack_name = pack["name"].replace(" ", "_").replace("/", "-")
        pack_dir = genre_dir / pack_name
        
        # Check if already downloaded
        if pack_dir.exists() and any(pack_dir.iterdir()):
            print(f"  ○ {pack['name']} (already exists)")
            skipped += 1
            continue
        
        if dry_run:
            print(f"  ? {pack['name']} - {pack['samples']} samples, {pack['size']}")
            continue
        
        # Create directory and download
        pack_dir.mkdir(parents=True, exist_ok=True)
        
        zip_filename = pack["url"].split("/")[-1]
        zip_path = pack_dir / zip_filename
        
        if download_file(pack["url"], zip_path):
            if extract_zip(zip_path, pack_dir):
                downloaded += 1
            else:
                # Clean up failed extraction
                if zip_path.exists():
                    zip_path.unlink()
        
    return downloaded, skipped


def main():
    parser = argparse.ArgumentParser(
        description="Download free sample packs from SoundShockAudio"
    )
    parser.add_argument(
        "--list", action="store_true",
        help="List all available sample packs"
    )
    parser.add_argument(
        "--genre", nargs="+", choices=list(SAMPLE_PACKS.keys()),
        help="Download specific genres only"
    )
    parser.add_argument(
        "--dry", action="store_true",
        help="Dry run - show what would be downloaded"
    )
    parser.add_argument(
        "--output", type=str, default=None,
        help="Output directory (default: data/audio/samples)"
    )
    
    args = parser.parse_args()
    
    if args.output:
        global SAMPLES_DIR
        SAMPLES_DIR = Path(args.output)
    
    if args.list:
        list_packs()
        return
    
    # Determine which genres to download
    genres = args.genre if args.genre else list(SAMPLE_PACKS.keys())
    
    print("\n" + "=" * 60)
    print("  DOWNLOADING ZICPIXEL SAMPLE PACKS")
    print("  Source: SoundShockAudio (Royalty-Free)")
    print("=" * 60)
    
    if args.dry:
        print("\n  [DRY RUN - No files will be downloaded]")
    
    total_downloaded = 0
    total_skipped = 0
    
    for genre in genres:
        downloaded, skipped = download_genre(genre, args.dry)
        total_downloaded += downloaded
        total_skipped += skipped
    
    print(f"\n{'=' * 60}")
    print(f"  COMPLETE")
    print(f"  Downloaded: {total_downloaded}")
    print(f"  Skipped (existing): {total_skipped}")
    print(f"  Location: {SAMPLES_DIR}")
    print(f"{'=' * 60}\n")


if __name__ == "__main__":
    main()
