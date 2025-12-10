# Hitster Card Generator

A Python tool that generates printable QR code cards for a Hitster-style music guessing game. Cards link to Spotify tracks when scanned.

## Features

- 🎴 **Card Generator** - Create printable QR code cards from Spotify playlists
- 📱 **Web Player** - Scan cards and control Spotify playback from a web app
- 🎵 **Spotify Integration** - Import playlists and control playback

## Setup

1. Create a virtual environment and install dependencies:

```bash
# Install virtualenv if you don't have it
pip install virtualenv

# Create and activate the virtual environment
virtualenv venv
source venv/bin/activate  # On macOS/Linux/WSL
# or: venv\Scripts\activate  # On Windows

pip install -r requirements.txt
```

## Card Generator Usage

### Option 1: Import from Spotify Playlist (Recommended)

Automatically import all songs from any Spotify playlist:

```bash
# Set your Spotify API credentials (get them at https://developer.spotify.com/dashboard)
export SPOTIPY_CLIENT_ID="your_client_id"
export SPOTIPY_CLIENT_SECRET="your_client_secret"

# Import a playlist
python -m src.main import -p "https://open.spotify.com/playlist/0Dsp6i8lvmcTg5aiusjnFH" -o playlist.csv

# Generate cards from the imported playlist
python -m src.main generate -i playlist.csv -o output/cards.pdf
```

Or pass credentials directly:

```bash
python -m src.main import \
  -p "https://open.spotify.com/playlist/0Dsp6i8lvmcTg5aiusjnFH" \
  -o playlist.csv \
  --client-id "your_client_id" \
  --client-secret "your_client_secret"
```

### Option 2: Manual CSV

1. Create or edit `songs.csv` with your song data:

```csv
title,artist,year,spotify_url
Bohemian Rhapsody,Queen,1975,https://open.spotify.com/track/4u7EnebtmKWzUH433cf5Qv
```

2. Generate the cards:

```bash
python -m src.main generate -i songs.csv -o output/cards.pdf
```

3. Print the PDF double-sided and cut out the cards.

## Web Player 🎵

The project includes a web-based QR scanner that automatically plays songs when you scan cards. Perfect for hosting game nights!

### Quick Start

```bash
cd player
npm install
npm run dev
```

Then open `http://localhost:5173` in your browser.

### Features

- 📷 Camera-based QR code scanning
- 🔊 Play on any Spotify Connect device (phone, speaker, etc.)
- 📱 Works on mobile - install as a PWA

See [player/README.md](player/README.md) for full setup instructions.

## Getting Spotify API Credentials

1. Go to [Spotify Developer Dashboard](https://developer.spotify.com/dashboard)
2. Log in with your Spotify account
3. Click "Create App"
4. Fill in the app name and description (anything you like)
5. For the web player, add redirect URI: `http://localhost:5173/callback`
6. Copy the **Client ID** and **Client Secret**

## Commands

### `import` - Import a Spotify playlist

```bash
python -m src.main import -p PLAYLIST_URL -o OUTPUT_CSV [--client-id ID] [--client-secret SECRET]
```

| Option | Description |
|--------|-------------|
| `-p, --playlist` | Spotify playlist URL or ID (required) |
| `-o, --output` | Output CSV file path (default: playlist.csv) |
| `--client-id` | Spotify API client ID (or set `SPOTIPY_CLIENT_ID` env var) |
| `--client-secret` | Spotify API client secret (or set `SPOTIPY_CLIENT_SECRET` env var) |

### `generate` - Generate PDF cards

```bash
python -m src.main generate -i INPUT_CSV -o OUTPUT_PDF
```

| Option | Description |
|--------|-------------|
| `-i, --input` | Input CSV file with song data (required) |
| `-o, --output` | Output PDF file path (default: output/cards.pdf) |

## CSV Format

| Column | Description |
|--------|-------------|
| `title` | Song name |
| `artist` | Artist or band name |
| `year` | Release year |
| `spotify_url` | Full Spotify track URL |

## How to Play

### Traditional (Phone Scanning)
1. Shuffle the printed cards (QR side up)
2. Players take turns scanning a QR code with their phone
3. The song plays on Spotify
4. Player guesses the year (and optionally song/artist)
5. Flip the card to reveal the answer
6. Score points for correct guesses!

### With Web Player (Recommended for Groups)
1. Set up a tablet/phone with the web player connected to a speaker
2. Shuffle the printed cards
3. Players take turns drawing a card and holding it up to the scanner
4. The song plays automatically on the speaker
5. Player guesses the year
6. Host taps "Reveal" to show the answer
7. Score points!

## Card Dimensions

Cards are sized at 2.5" x 3.5" (standard poker card size) by default.

## Printing Tips

1. Print double-sided (flip on **short edge**)
2. Use cardstock (heavier paper) for durability
3. Cut along the crop marks

## Project Structure

```
hitster/
├── src/                    # Card generator Python code
│   ├── main.py            # CLI entry point
│   ├── csv_parser.py      # CSV parsing
│   ├── pdf_generator.py   # PDF card generation
│   ├── qr_generator.py    # QR code generation
│   └── spotify_importer.py # Spotify playlist import
├── player/                 # Web player app
│   ├── src/               # JavaScript modules
│   ├── index.html         # Main page
│   └── styles.css         # Styling
├── output/                 # Generated PDFs
├── songs.csv              # Example song list
└── requirements.txt       # Python dependencies
```
