"""CSV parser for loading and validating song data."""

import csv
import re
from dataclasses import dataclass
from pathlib import Path
from typing import List


@dataclass
class Song:
    """Represents a song with its metadata."""
    title: str
    artist: str
    year: int
    spotify_url: str
    spotify_uri: str  # Converted URI for direct app opening
    
    def __post_init__(self):
        """Validate song data after initialization."""
        if not self.title:
            raise ValueError("Song title cannot be empty")
        if not self.artist:
            raise ValueError("Artist cannot be empty")
        if not 1900 <= self.year <= 2100:
            raise ValueError(f"Year {self.year} is out of valid range (1900-2100)")


def extract_spotify_track_id(url: str) -> str:
    """
    Extract the Spotify track ID from a URL.
    
    Supports formats:
    - https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT
    - https://open.spotify.com/track/4cOdK2wGLETKBW3PvgPWqT?si=...
    - spotify:track:4cOdK2wGLETKBW3PvgPWqT
    """
    # Handle spotify URI format
    if url.startswith("spotify:track:"):
        return url.split(":")[-1]
    
    # Handle URL format
    pattern = r'spotify\.com/track/([a-zA-Z0-9]+)'
    match = re.search(pattern, url)
    if match:
        return match.group(1)
    
    raise ValueError(f"Could not extract Spotify track ID from: {url}")


def url_to_spotify_uri(url: str) -> str:
    """Convert a Spotify URL to a spotify: URI for direct app opening."""
    track_id = extract_spotify_track_id(url)
    return f"spotify:track:{track_id}"


def load_songs(csv_path: Path) -> List[Song]:
    """
    Load songs from a CSV file.
    
    Expected columns: title, artist, year, spotify_url
    
    Args:
        csv_path: Path to the CSV file
        
    Returns:
        List of Song objects
        
    Raises:
        FileNotFoundError: If the CSV file doesn't exist
        ValueError: If the CSV is malformed or contains invalid data
    """
    if not csv_path.exists():
        raise FileNotFoundError(f"CSV file not found: {csv_path}")
    
    songs = []
    required_columns = {'title', 'artist', 'year', 'spotify_url'}
    
    with open(csv_path, 'r', encoding='utf-8') as f:
        reader = csv.DictReader(f)
        
        # Validate columns
        if reader.fieldnames is None:
            raise ValueError("CSV file is empty or has no header row")
        
        missing_columns = required_columns - set(reader.fieldnames)
        if missing_columns:
            raise ValueError(f"CSV is missing required columns: {missing_columns}")
        
        for row_num, row in enumerate(reader, start=2):  # Start at 2 (header is row 1)
            try:
                # Parse and validate the row
                title = row['title'].strip()
                artist = row['artist'].strip()
                year_str = row['year'].strip()
                spotify_url = row['spotify_url'].strip()
                
                # Validate year is a number
                try:
                    year = int(year_str)
                except ValueError:
                    raise ValueError(f"Invalid year '{year_str}' - must be a number")
                
                # Convert URL to URI
                spotify_uri = url_to_spotify_uri(spotify_url)
                
                song = Song(
                    title=title,
                    artist=artist,
                    year=year,
                    spotify_url=spotify_url,
                    spotify_uri=spotify_uri
                )
                songs.append(song)
                
            except Exception as e:
                raise ValueError(f"Error in row {row_num}: {e}")
    
    if not songs:
        raise ValueError("CSV file contains no songs")
    
    return songs

