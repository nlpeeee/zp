#!/usr/bin/env python3
"""
ZicPixel CC0 Sample Downloader
Downloads genre-specific CC0 samples from Freesound.org

Setup:
1. Create a Freesound account at https://freesound.org/
2. Get an API key at https://freesound.org/apiv2/apply/
3. Set your API key: export FREESOUND_API_KEY="your_key_here"
   Or create a .env file with FREESOUND_API_KEY=your_key_here

Usage:
    python download_samples.py --genre house
    python download_samples.py --genre jungle --max 10
    python download_samples.py --all
    python download_samples.py --list
"""

import os
import sys
import json
import argparse
import urllib.request
import urllib.parse
import time
from pathlib import Path

# Freesound API settings
FREESOUND_API_URL = "https://freesound.org/apiv2"
API_KEY = os.environ.get("FREESOUND_API_KEY", "")
REQUEST_DELAY = 0.5  # Seconds between API requests to avoid rate limiting

# Output directory (relative to script or absolute)
SCRIPT_DIR = Path(__file__).parent.parent
SAMPLES_DIR = SCRIPT_DIR / "data" / "audio" / "samples"

# Genre-specific sample queries
# Using specific Freesound tags and terms for better results
# Format: { "subfolder": ["search query 1", "search query 2", ...] }
GENRE_PACKS = {
    "house": {
        "kicks": [
            "kick drum house electronic",
            "kick 4x4 dance",
            "kick sample edm",
        ],
        "claps": [
            "clap snare house",
            "clap electronic dance",
            "handclap sample",
        ],
        "hihats": [
            "hihat closed electronic",
            "hihat open house",
            "hat loop house",
        ],
        "chords": [
            "piano stab chord",
            "organ chord stab",
            "synth chord house",
        ],
        "bass": [
            "bass stab house",
            "sub bass 808",
            "bass synth deep",
        ],
        "vocals": [
            "vocal chop edm",
            "vocal sample dance",
            "vocal hook female",
        ],
    },
    "techno": {
        "kicks": [
            "kick techno hard",
            "kick 909 sample",
            "kick industrial dark",
        ],
        "claps": [
            "clap 909",
            "clap techno snare",
            "rimshot electronic",
        ],
        "hihats": [
            "hihat 909 closed",
            "hihat techno open",
            "ride cymbal electronic",
        ],
        "percussion": [
            "tom electronic drum",
            "percussion electronic hit",
            "shaker percussion loop",
        ],
        "fx": [
            "noise sweep synth",
            "riser synth build",
            "impact cinematic hit",
        ],
        "bass": [
            "bass acid 303",
            "bass techno dark",
            "sub bass sine",
        ],
    },
    "jungle": {
        "breaks": [
            "amen break loop",
            "breakbeat drum loop",
            "jungle drums loop",
            "break dnb fast",
        ],
        "bass": [
            "reese bass synth",
            "bass wobble dnb",
            "sub bass jungle",
        ],
        "fx": [
            "siren dub reggae",
            "airhorn sample",
            "vocal chop ragga",
        ],
    },
    "dnb": {
        "breaks": [
            "breakbeat 170 bpm",
            "drums dnb loop",
            "break fast electronic",
        ],
        "bass": [
            "bass neuro wobble",
            "reese bass dark",
            "bass growl synth",
        ],
        "fx": [
            "riser dnb build",
            "impact drum bass",
        ],
    },
    "garage": {
        "drums": [
            "kick 2step garage",
            "snare garage uk",
            "hihat shuffle garage",
        ],
        "vocals": [
            "vocal chop rnb",
            "vocal female soul",
            "vocal hook garage",
        ],
        "bass": [
            "bass garage uk",
            "bass 2step sub",
        ],
        "chords": [
            "chord stab garage",
            "piano chord rnb",
            "organ chord soul",
        ],
    },
    "synthwave": {
        "drums": [
            "snare gated reverb 80s",
            "kick 80s electronic",
            "tom electronic 80s",
            "clap reverb 80s",
        ],
        "synth": [
            "synth brass 80s",
            "lead synth retro",
            "pad synth analog",
        ],
        "bass": [
            "bass synth 80s",
            "bass analog retro",
        ],
    },
    "electro": {
        "drums": [
            "kick electro 808",
            "cowbell 808",
            "clap electro robotic",
            "hihat electro crisp",
        ],
        "bass": [
            "bass 303 acid",
            "bass electro synth",
        ],
        "synth": [
            "stab synth electro",
            "vocoder robot voice",
            "arp synth electronic",
        ],
    },
    "ambient": {
        "textures": [
            "pad ambient texture",
            "drone synth dark",
            "atmosphere space",
            "texture evolving pad",
        ],
        "nature": [
            "rain recording ambient",
            "wind field recording",
            "water stream nature",
            "forest birds ambient",
        ],
        "tonal": [
            "bell ambient reverb",
            "singing bowl tibetan",
            "chime wind",
            "piano ambient reverb",
        ],
    },
    "hiphop": {
        "drums": [
            "kick boom bap",
            "snare hip hop crisp",
            "hihat trap closed",
            "kick 808 trap",
        ],
        "bass": [
            "bass 808 long",
            "bass hip hop sub",
        ],
        "fx": [
            "vinyl crackle loop",
            "scratch dj turntable",
            "tape stop effect",
        ],
        "samples": [
            "guitar funk sample",
            "horn stab soul",
            "string sample orchestra",
        ],
    },
    "trance": {
        "kicks": [
            "kick trance punchy",
            "kick uplifting trance",
        ],
        "synth": [
            "lead supersaw trance",
            "pluck synth trance",
            "pad trance uplifting",
        ],
        "fx": [
            "riser white noise long",
            "build up trance",
            "impact reverse cymbal",
        ],
    },
    # Essential/universal drum samples
    "drums808": {
        "kicks": [
            "808 kick tr",
            "kick 808 roland",
            "bass drum 808",
        ],
        "snares": [
            "snare 808 tr",
            "rimshot 808",
            "clap 808 roland",
        ],
        "hihats": [
            "hihat 808 closed",
            "hihat 808 open",
        ],
        "percussion": [
            "cowbell 808",
            "clave 808",
            "conga 808",
            "tom 808",
            "maracas 808",
        ],
    },
    "drums909": {
        "kicks": [
            "909 kick tr",
            "kick 909 roland",
        ],
        "snares": [
            "snare 909 tr",
            "clap 909 roland",
        ],
        "hihats": [
            "hihat 909 closed",
            "hihat 909 open",
        ],
        "percussion": [
            "crash 909 cymbal",
            "ride 909 cymbal",
            "tom 909",
        ],
    },
}

# Tags that indicate irrelevant results (false positives)
EXCLUDE_TAGS = {
    'crowd', 'audience', 'applause', 'cheer', 'thunder', 'heartbeat',
    'speech', 'talking', 'conversation', 'voice-over', 'narration',
    'gun', 'gunshot', 'weapon', 'war', 'bomb',
    'car', 'engine', 'vehicle', 'traffic',
    'animal', 'dog', 'cat', 'bird', 'insect',
    'phone', 'ringtone', 'notification', 'alert',
    'game', 'video-game', 'arcade', 'retro-game',
    'movie', 'film', 'cinematic', 'trailer',
    'foley', 'water', 'sink', 'kitchen', 'bathroom',
    'door', 'footsteps', 'walking', 'running',
    'baby', 'child', 'laugh', 'scream', 'cry',
}

# Tags that indicate good drum/synth samples
GOOD_TAGS = {
    'drum', 'kick', 'snare', 'hihat', 'hi-hat', 'clap', 'percussion',
    'synth', 'synthesizer', 'bass', 'electronic', 'edm', 'dance',
    'house', 'techno', 'trance', '808', '909', 'tr-808', 'tr-909',
    'sample', 'one-shot', 'loop', 'beat', 'break', 'breakbeat',
}


def filter_results(results: list, query: str) -> list:
    """Filter search results to remove false positives."""
    filtered = []
    query_words = set(query.lower().split())
    
    for sound in results:
        tags = set(t.lower() for t in sound.get('tags', []))
        name = sound.get('name', '').lower()
        
        # Skip if has excluded tags
        if tags & EXCLUDE_TAGS:
            continue
        
        # Skip if name contains excluded words
        excluded_names = ['crowd', 'cheer', 'thunder', 'heartbeat', 'gun', 'speech', 
                          'foley', 'water', 'sink', 'kitchen', 'door', 'footstep',
                          'baby', 'laugh', 'scream', 'car', 'engine', 'vehicle']
        if any(ex in name for ex in excluded_names):
            continue
            
        # Prefer results with good tags
        has_good_tags = bool(tags & GOOD_TAGS)
        has_query_match = any(qw in name or qw in tags for qw in query_words if len(qw) > 2)
        
        if has_good_tags or has_query_match:
            filtered.append(sound)
    
    return filtered


def search_freesound(query: str, max_results: int = 5) -> list:
    """Search Freesound for CC0 samples."""
    if not API_KEY:
        print("ERROR: FREESOUND_API_KEY not set!")
        print("Get your API key at: https://freesound.org/apiv2/apply/")
        sys.exit(1)

    # Build filter: CC0 license + short duration for one-shots
    # For loops/breaks allow up to 15s, for one-shots prefer under 3s
    is_loop = any(word in query.lower() for word in ['loop', 'break', 'beat'])
    max_duration = 15 if is_loop else 5
    
    filter_str = f'license:"Creative Commons 0" duration:[0 TO {max_duration}]'
    
    # Request more results to compensate for filtering
    fetch_count = max_results * 3
    
    params = urllib.parse.urlencode({
        "query": query,
        "filter": filter_str,
        "fields": "id,name,duration,previews,download,filesize,tags",
        "sort": "score",  # Relevance sort instead of downloads
        "page_size": fetch_count,
        "token": API_KEY,
    })

    url = f"{FREESOUND_API_URL}/search/text/?{params}"
    
    try:
        time.sleep(REQUEST_DELAY)  # Rate limiting
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            results = data.get("results", [])
            
            # Filter out false positives and return top matches
            filtered = filter_results(results, query)
            return filtered[:max_results]
            
    except urllib.error.HTTPError as e:
        if e.code == 429:
            print(f"  Rate limited, waiting 5 seconds...")
            time.sleep(5)
            return search_freesound(query, max_results)  # Retry
        print(f"  HTTP Error {e.code}: {e.reason}")
        return []
    except Exception as e:
        print(f"  Error searching: {e}")
        return []


def download_sound(sound_id: int, output_path: Path) -> bool:
    """Download a sound from Freesound."""
    time.sleep(REQUEST_DELAY)  # Rate limiting
    
    # First get the sound details to get preview URL
    url = f"{FREESOUND_API_URL}/sounds/{sound_id}/?token={API_KEY}&fields=previews,name"
    
    try:
        with urllib.request.urlopen(url, timeout=30) as response:
            data = json.loads(response.read().decode())
            
        # Use HQ preview (MP3) - original requires OAuth
        preview_url = data.get("previews", {}).get("preview-hq-mp3")
        if not preview_url:
            preview_url = data.get("previews", {}).get("preview-lq-mp3")
        
        if not preview_url:
            print(f"  No preview URL for sound {sound_id}")
            return False

        # Download the file
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Change extension to mp3 for preview files
        mp3_path = output_path.with_suffix(".mp3")
        
        urllib.request.urlretrieve(preview_url, mp3_path)
        print(f"  ✓ Downloaded: {mp3_path.name}")
        return True
        
    except Exception as e:
        print(f"  ✗ Failed to download {sound_id}: {e}")
        return False


def sanitize_filename(name: str) -> str:
    """Create a safe filename from sound name."""
    # Remove/replace invalid characters
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        name = name.replace(char, "_")
    # Remove existing extensions to avoid .wav.mp3
    for ext in ['.wav', '.mp3', '.aif', '.aiff', '.flac', '.ogg']:
        if name.lower().endswith(ext):
            name = name[:-len(ext)]
    # Limit length and strip
    return name[:50].strip().replace(" ", "_")


def download_genre_pack(genre: str, max_per_query: int = 3, dry_run: bool = False, output_dir: Path = None):
    """Download all samples for a genre pack."""
    if output_dir is None:
        output_dir = SAMPLES_DIR
        
    if genre not in GENRE_PACKS:
        print(f"Unknown genre: {genre}")
        print(f"Available genres: {', '.join(GENRE_PACKS.keys())}")
        return

    pack = GENRE_PACKS[genre]
    genre_dir = output_dir / genre
    
    print(f"\n{'=' * 50}")
    print(f"Downloading {genre.upper()} sample pack")
    print(f"Output: {genre_dir}")
    print(f"{'=' * 50}\n")

    total_downloaded = 0
    
    for category, queries in pack.items():
        category_dir = genre_dir / category
        print(f"\n[{category.upper()}]")
        
        for query in queries:
            print(f"  Searching: '{query}'...")
            results = search_freesound(query, max_per_query)
            
            if not results:
                print(f"    No CC0 results found")
                continue
                
            for sound in results:
                if sound.get("duration", 0) > 30:
                    print(f"    Skipping {sound['name']} (too long: {sound['duration']:.1f}s)")
                    continue
                    
                filename = sanitize_filename(sound["name"])
                output_path = category_dir / f"{filename}.wav"
                
                if dry_run:
                    print(f"    Would download: {sound['name']} ({sound['duration']:.1f}s)")
                else:
                    if download_sound(sound["id"], output_path):
                        total_downloaded += 1

    print(f"\n{'=' * 50}")
    print(f"Downloaded {total_downloaded} samples for {genre}")
    print(f"{'=' * 50}\n")


def list_genres():
    """List available genre packs."""
    print("\nAvailable Genre Packs:")
    print("=" * 50)
    for genre, pack in GENRE_PACKS.items():
        categories = ", ".join(pack.keys())
        total_queries = sum(len(queries) for queries in pack.values())
        print(f"\n  {genre.upper()}")
        print(f"    Categories: {categories}")
        print(f"    Sample types: {total_queries}")
    print()


def main():
    parser = argparse.ArgumentParser(
        description="Download CC0 samples from Freesound.org for ZicPixel",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  %(prog)s --genre house          Download house sample pack
  %(prog)s --genre jungle --max 5 Download jungle pack (5 samples per query)
  %(prog)s --all                  Download all genre packs
  %(prog)s --list                 List available genre packs
  %(prog)s --genre house --dry    Preview what would be downloaded

Environment:
  FREESOUND_API_KEY   Your Freesound API key (required)
                      Get one at: https://freesound.org/apiv2/apply/
        """
    )
    
    parser.add_argument("--genre", "-g", help="Genre pack to download")
    parser.add_argument("--all", "-a", action="store_true", help="Download all genre packs")
    parser.add_argument("--list", "-l", action="store_true", help="List available genre packs")
    parser.add_argument("--max", "-m", type=int, default=3, 
                        help="Max samples per search query (default: 3)")
    parser.add_argument("--dry", "-d", action="store_true", 
                        help="Dry run - show what would be downloaded")
    parser.add_argument("--output", "-o", type=Path, 
                        help="Output directory (default: data/audio/samples)")
    
    args = parser.parse_args()
    
    if args.list:
        list_genres()
        return
    
    if not args.genre and not args.all:
        parser.print_help()
        return
    
    # Set output directory
    output_dir = args.output if args.output else SAMPLES_DIR
    
    if not API_KEY:
        print("\n" + "=" * 50)
        print("FREESOUND API KEY REQUIRED")
        print("=" * 50)
        print("\n1. Create account: https://freesound.org/")
        print("2. Get API key: https://freesound.org/apiv2/apply/")
        print("3. Set environment variable:")
        print("   Windows: set FREESOUND_API_KEY=your_key_here")
        print("   Linux/Mac: export FREESOUND_API_KEY=your_key_here")
        print("\nOr create a .env file in this directory with:")
        print("   FREESOUND_API_KEY=your_key_here\n")
        sys.exit(1)
    
    # Create samples directory
    output_dir.mkdir(parents=True, exist_ok=True)
    
    if args.all:
        for genre in GENRE_PACKS:
            download_genre_pack(genre, args.max, args.dry, output_dir)
    else:
        download_genre_pack(args.genre, args.max, args.dry, output_dir)
    
    print("\nDone! Samples saved to:", output_dir)
    print("\nNote: Freesound previews are MP3 format.")
    print("For best quality, consider converting to WAV using ffmpeg:")
    print(f"  for f in {output_dir}/**/*.mp3; do ffmpeg -i \"$f\" \"${{f%.mp3}}.wav\"; done")


if __name__ == "__main__":
    # Try to load .env file if it exists
    env_file = Path(__file__).parent / ".env"
    if env_file.exists():
        with open(env_file) as f:
            for line in f:
                if "=" in line and not line.startswith("#"):
                    key, value = line.strip().split("=", 1)
                    os.environ.setdefault(key, value)
        API_KEY = os.environ.get("FREESOUND_API_KEY", "")
    
    main()
