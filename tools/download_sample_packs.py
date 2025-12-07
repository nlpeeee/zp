#!/usr/bin/env python3
"""
ZicPixel Sample Pack Downloader (No API Key Required)
Downloads CC0/Public Domain samples from Archive.org and other sources

Usage:
    python download_sample_packs.py --pack 808
    python download_sample_packs.py --pack 909
    python download_sample_packs.py --pack all
    python download_sample_packs.py --list
"""

import os
import sys
import argparse
import urllib.request
import ssl
from pathlib import Path
from typing import Dict, List, Tuple

# Disable SSL verification for some older servers
ssl._create_default_https_context = ssl._create_unverified_context

# Output directory
SCRIPT_DIR = Path(__file__).parent.parent
SAMPLES_DIR = SCRIPT_DIR / "data" / "audio" / "samples"

# Direct download URLs for CC0/Public Domain samples
# Format: { pack_name: { subfolder: [(url, filename), ...] } }
SAMPLE_PACKS: Dict[str, Dict[str, List[Tuple[str, str]]]] = {
    "808": {
        "kicks": [
            ("https://archive.org/download/Roland_TR-808_Samples/BD/BD0000.WAV", "808_kick_low.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/BD/BD0010.WAV", "808_kick_mid.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/BD/BD0025.WAV", "808_kick_high.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/BD/BD0050.WAV", "808_kick_punchy.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/BD/BD0075.WAV", "808_kick_deep.wav"),
        ],
        "snares": [
            ("https://archive.org/download/Roland_TR-808_Samples/SD/SD0000.WAV", "808_snare_low.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/SD/SD0010.WAV", "808_snare_mid.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/SD/SD0025.WAV", "808_snare_high.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/SD/SD0050.WAV", "808_snare_tight.wav"),
        ],
        "hihats": [
            ("https://archive.org/download/Roland_TR-808_Samples/CH/CH.WAV", "808_hihat_closed.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/OH/OH00.WAV", "808_hihat_open_short.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/OH/OH10.WAV", "808_hihat_open_mid.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/OH/OH25.WAV", "808_hihat_open_long.wav"),
        ],
        "claps": [
            ("https://archive.org/download/Roland_TR-808_Samples/CP/CP.WAV", "808_clap.wav"),
        ],
        "toms": [
            ("https://archive.org/download/Roland_TR-808_Samples/LT/LT00.WAV", "808_tom_low.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/MT/MT00.WAV", "808_tom_mid.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/HT/HT00.WAV", "808_tom_high.wav"),
        ],
        "percussion": [
            ("https://archive.org/download/Roland_TR-808_Samples/CY/CY0000.WAV", "808_cymbal_short.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/CY/CY0010.WAV", "808_cymbal_mid.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/CY/CY0025.WAV", "808_cymbal_long.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/CB/CB.WAV", "808_cowbell.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/RS/RS.WAV", "808_rimshot.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/MA/MA.WAV", "808_maracas.wav"),
            ("https://archive.org/download/Roland_TR-808_Samples/CL/CL.WAV", "808_clave.wav"),
        ],
    },
    
    "909": {
        "kicks": [
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/BD/BD0000.WAV", "909_kick_soft.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/BD/BD0010.WAV", "909_kick_mid.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/BD/BD0025.WAV", "909_kick_hard.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/BD/BD0050.WAV", "909_kick_punchy.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/BD/BD0075.WAV", "909_kick_attack.wav"),
        ],
        "snares": [
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/SD/SD0000.WAV", "909_snare_soft.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/SD/SD0010.WAV", "909_snare_mid.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/SD/SD0025.WAV", "909_snare_hard.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/SD/SD0050.WAV", "909_snare_tight.wav"),
        ],
        "hihats": [
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/HH/CH.WAV", "909_hihat_closed.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/HH/OH00.WAV", "909_hihat_open_short.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/HH/OH10.WAV", "909_hihat_open_mid.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/HH/OH25.WAV", "909_hihat_open_long.wav"),
        ],
        "claps": [
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/CP/CP.WAV", "909_clap.wav"),
        ],
        "percussion": [
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/CY/CY0000.WAV", "909_crash_short.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/CY/CY0025.WAV", "909_crash_long.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/CY/RD0000.WAV", "909_ride_short.wav"),
            ("https://archive.org/download/Roland_TR-909_Drum_Samples/TR909%20WAV/CY/RD0025.WAV", "909_ride_long.wav"),
        ],
    },
    
    # Additional minimal packs using samplefocus/other CC0 sources
    "essentials": {
        "kicks": [
            # Archive.org has various public domain drum samples
        ],
        "info": [
            # This pack uses samples from the 808/909 packs
            # Run --pack 808 and --pack 909 to get essentials
        ],
    },
}

# Alternative: Hydrogen drum kit samples (GPL, commonly redistributed)
HYDROGEN_KITS = {
    "gmkit": "https://github.com/hydrogen-music/hydrogen/raw/master/data/drumkits/GMRockKit/",
}


def download_file(url: str, output_path: Path) -> bool:
    """Download a file from URL to output path."""
    try:
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Add user agent to avoid blocks
        request = urllib.request.Request(
            url,
            headers={"User-Agent": "Mozilla/5.0 (ZicPixel Sample Downloader)"}
        )
        
        with urllib.request.urlopen(request, timeout=30) as response:
            with open(output_path, "wb") as f:
                f.write(response.read())
        
        return True
    except Exception as e:
        print(f"    Error: {e}")
        return False


def download_pack(pack_name: str, dry_run: bool = False) -> int:
    """Download a sample pack."""
    if pack_name not in SAMPLE_PACKS:
        print(f"Unknown pack: {pack_name}")
        print(f"Available packs: {', '.join(SAMPLE_PACKS.keys())}")
        return 0

    pack = SAMPLE_PACKS[pack_name]
    pack_dir = SAMPLES_DIR / pack_name
    
    print(f"\n{'=' * 50}")
    print(f"Downloading {pack_name.upper()} sample pack")
    print(f"Output: {pack_dir}")
    print(f"{'=' * 50}")
    
    downloaded = 0
    skipped = 0
    failed = 0

    for category, samples in pack.items():
        if category == "info":
            continue
            
        category_dir = pack_dir / category
        print(f"\n[{category.upper()}]")
        
        for url, filename in samples:
            output_path = category_dir / filename
            
            # Skip if already exists
            if output_path.exists():
                print(f"  ○ Skipped (exists): {filename}")
                skipped += 1
                continue
            
            if dry_run:
                print(f"  Would download: {filename}")
                print(f"    From: {url}")
                continue
            
            print(f"  Downloading: {filename}...", end=" ", flush=True)
            if download_file(url, output_path):
                print("✓")
                downloaded += 1
            else:
                print("✗")
                failed += 1

    print(f"\n{'=' * 50}")
    print(f"Pack: {pack_name}")
    print(f"Downloaded: {downloaded}, Skipped: {skipped}, Failed: {failed}")
    print(f"{'=' * 50}")
    
    return downloaded


def list_packs():
    """List available sample packs."""
    print("\n" + "=" * 50)
    print("Available Sample Packs (No API Key Required)")
    print("=" * 50)
    
    for pack_name, pack in SAMPLE_PACKS.items():
        categories = [c for c in pack.keys() if c != "info"]
        total_samples = sum(len(samples) for c, samples in pack.items() if c != "info")
        
        print(f"\n  {pack_name.upper()}")
        print(f"    Categories: {', '.join(categories)}")
        print(f"    Samples: {total_samples}")
    
    print(f"\n{'=' * 50}")
    print("Usage: python download_sample_packs.py --pack 808")
    print("       python download_sample_packs.py --pack all")
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Download CC0/Public Domain sample packs for ZicPixel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --pack 808         Download TR-808 samples
  %(prog)s --pack 909         Download TR-909 samples
  %(prog)s --pack all         Download all available packs
  %(prog)s --list             List available packs
  %(prog)s --pack 808 --dry   Preview what would be downloaded

No API key required! All samples are from Archive.org and public domain sources.
        """
    )
    
    parser.add_argument("--pack", "-p", help="Sample pack to download (or 'all')")
    parser.add_argument("--list", "-l", action="store_true", help="List available packs")
    parser.add_argument("--dry", "-d", action="store_true", help="Dry run - show what would be downloaded")
    parser.add_argument("--output", "-o", type=Path, help=f"Output directory (default: {SAMPLES_DIR})")
    
    args = parser.parse_args()
    
    if args.output:
        global SAMPLES_DIR
        SAMPLES_DIR = args.output
    
    if args.list:
        list_packs()
        return
    
    if not args.pack:
        parser.print_help()
        return
    
    # Create samples directory
    SAMPLES_DIR.mkdir(parents=True, exist_ok=True)
    
    total = 0
    if args.pack.lower() == "all":
        for pack_name in SAMPLE_PACKS:
            if pack_name != "essentials":  # Skip meta-pack
                total += download_pack(pack_name, args.dry)
    else:
        total = download_pack(args.pack.lower(), args.dry)
    
    if not args.dry:
        print(f"\n✓ Total samples downloaded: {total}")
        print(f"  Saved to: {SAMPLES_DIR}")


if __name__ == "__main__":
    main()
