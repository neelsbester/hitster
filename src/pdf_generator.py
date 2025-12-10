"""PDF generator for printable double-sided cards with premium concentric circles design."""

from io import BytesIO
from pathlib import Path
from typing import List
import math
import random

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, white, HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from .csv_parser import Song
from .qr_generator import generate_spotify_qr


# Card dimensions (square cards)
CARD_WIDTH = 2.5 * inch
CARD_HEIGHT = 2.5 * inch

# Page margins
MARGIN = 0.5 * inch

# Decade-based color themes - colors evoke each era's aesthetic
DECADE_THEMES = {
    2020: {
        "name": "2020s",
        "primary": HexColor("#6366f1"),       # Indigo (modern tech/social media)
        "light_accent": HexColor("#818cf8"),
    },
    2010: {
        "name": "2010s",
        "primary": HexColor("#ec4899"),       # Pink (EDM/pop era, Instagram)
        "light_accent": HexColor("#f472b6"),
    },
    2000: {
        "name": "2000s",
        "primary": HexColor("#10b981"),       # Emerald green (Y2K, iPod era)
        "light_accent": HexColor("#34d399"),
    },
    1990: {
        "name": "1990s",
        "primary": HexColor("#14b8a6"),       # Teal (grunge, alternative)
        "light_accent": HexColor("#2dd4bf"),
    },
    1980: {
        "name": "1980s",
        "primary": HexColor("#f43f5e"),       # Hot pink/neon (synthwave, MTV)
        "light_accent": HexColor("#fb7185"),
    },
    1970: {
        "name": "1970s",
        "primary": HexColor("#f97316"),       # Orange (disco, funk)
        "light_accent": HexColor("#fb923c"),
    },
    1960: {
        "name": "1960s",
        "primary": HexColor("#a855f7"),       # Purple (psychedelic, flower power)
        "light_accent": HexColor("#c084fc"),
    },
    1950: {
        "name": "1950s",
        "primary": HexColor("#ef4444"),       # Classic red (rock & roll, diners)
        "light_accent": HexColor("#f87171"),
    },
    0: {
        "name": "pre-1950s",
        "primary": HexColor("#78716c"),       # Warm gray (vintage, classic)
        "light_accent": HexColor("#a8a29e"),
    },
}


def get_decade_theme(year: int) -> dict:
    """Get the color theme for a song based on its decade."""
    if year >= 2020:
        return DECADE_THEMES[2020]
    elif year >= 2010:
        return DECADE_THEMES[2010]
    elif year >= 2000:
        return DECADE_THEMES[2000]
    elif year >= 1990:
        return DECADE_THEMES[1990]
    elif year >= 1980:
        return DECADE_THEMES[1980]
    elif year >= 1970:
        return DECADE_THEMES[1970]
    elif year >= 1960:
        return DECADE_THEMES[1960]
    elif year >= 1950:
        return DECADE_THEMES[1950]
    else:
        return DECADE_THEMES[0]

# Vibrant CMYK-inspired colors for the concentric circles design
CIRCLE_COLORS = [
    HexColor("#00e5ff"),  # Cyan
    HexColor("#ff00ff"),  # Magenta
    HexColor("#ffea00"),  # Yellow
    HexColor("#ff1493"),  # Deep pink
    HexColor("#00ff7f"),  # Spring green
]

# Card backgrounds
LIGHT_BG = HexColor("#f8f8f8")       # Off-white for front
CARD_BORDER_LIGHT = HexColor("#e0e0e0")  # Light border


def calculate_cards_per_page(page_width: float, page_height: float) -> tuple:
    """Calculate how many cards fit on a page."""
    usable_width = page_width - (2 * MARGIN)
    usable_height = page_height - (2 * MARGIN)
    
    cols = int(usable_width // CARD_WIDTH)
    rows = int(usable_height // CARD_HEIGHT)
    
    return cols, rows


def draw_crop_marks(c: canvas.Canvas, x: float, y: float, length: float = 5*mm):
    """Draw crop marks at card corners for cutting guide."""
    c.setStrokeColor(HexColor("#9ca3af"))
    c.setLineWidth(0.3)
    
    # Top-left
    c.line(x - length, y + CARD_HEIGHT, x - 2, y + CARD_HEIGHT)
    c.line(x, y + CARD_HEIGHT + 2, x, y + CARD_HEIGHT + length)
    
    # Top-right
    c.line(x + CARD_WIDTH + 2, y + CARD_HEIGHT, x + CARD_WIDTH + length, y + CARD_HEIGHT)
    c.line(x + CARD_WIDTH, y + CARD_HEIGHT + 2, x + CARD_WIDTH, y + CARD_HEIGHT + length)
    
    # Bottom-left
    c.line(x - length, y, x - 2, y)
    c.line(x, y - 2, x, y - length)
    
    # Bottom-right
    c.line(x + CARD_WIDTH + 2, y, x + CARD_WIDTH + length, y)
    c.line(x + CARD_WIDTH, y - 2, x + CARD_WIDTH, y - length)


def draw_corner_rosette(c: canvas.Canvas, cx: float, cy: float, radius: float, color: Color):
    """Draw a decorative rosette/flower pattern at the given center point."""
    c.setStrokeColor(color)
    c.setLineWidth(0.8)
    
    # Outer circle
    c.circle(cx, cy, radius, stroke=1, fill=0)
    
    # Inner decorative pattern - small circles around center
    inner_radius = radius * 0.4
    num_petals = 6
    for i in range(num_petals):
        angle = (i * 360 / num_petals) * math.pi / 180
        petal_x = cx + inner_radius * math.cos(angle)
        petal_y = cy + inner_radius * math.sin(angle)
        c.circle(petal_x, petal_y, radius * 0.2, stroke=1, fill=0)
    
    # Center dot
    c.circle(cx, cy, radius * 0.15, stroke=1, fill=0)


def draw_starburst_lines(c: canvas.Canvas, cx: float, cy: float, 
                         inner_radius: float, outer_radius: float, 
                         color: Color, num_lines: int = 48):
    """Draw radiating starburst lines from center."""
    c.setStrokeColor(color)
    c.setLineWidth(0.6)
    
    for i in range(num_lines):
        angle = (i * 360 / num_lines) * math.pi / 180
        
        # Start point (inner)
        x1 = cx + inner_radius * math.cos(angle)
        y1 = cy + inner_radius * math.sin(angle)
        
        # End point (outer)
        x2 = cx + outer_radius * math.cos(angle)
        y2 = cy + outer_radius * math.sin(angle)
        
        c.line(x1, y1, x2, y2)


def draw_broken_arc(c: canvas.Canvas, cx: float, cy: float, radius: float, 
                    start_angle: float, extent: float, color: Color, line_width: float = 1.0):
    """Draw a single arc segment."""
    c.setStrokeColor(color)
    c.setLineWidth(line_width)
    
    # ReportLab arc uses bounding box coordinates
    x1 = cx - radius
    y1 = cy - radius
    x2 = cx + radius
    y2 = cy + radius
    
    c.arc(x1, y1, x2, y2, start_angle, extent)


def draw_concentric_broken_circles(c: canvas.Canvas, cx: float, cy: float, 
                                   min_radius: float, max_radius: float,
                                   colors: list, seed: int = None):
    """
    Draw concentric broken/segmented circles in vibrant colors.
    Creates the signature HITSTER card design with three distinct layers.
    """
    if seed is not None:
        random.seed(seed)
    
    # Three layer configuration - inner, middle, outer
    total_range = max_radius - min_radius
    layer_size = total_range / 3
    
    layers = [
        {"start": min_radius, "end": min_radius + layer_size, "spacing": 8, "line_width": 0.8},
        {"start": min_radius + layer_size, "end": min_radius + 2 * layer_size, "spacing": 7, "line_width": 1.0},
        {"start": min_radius + 2 * layer_size, "end": max_radius, "spacing": 6, "line_width": 1.2},
    ]
    
    for layer_idx, layer in enumerate(layers):
        layer_start = layer["start"]
        layer_end = layer["end"]
        ring_spacing = layer["spacing"]
        base_line_width = layer["line_width"]
        
        num_rings = int((layer_end - layer_start) / ring_spacing)
        
        for ring_idx in range(num_rings):
            radius = layer_start + (ring_idx * ring_spacing) + 3
            
            # Each ring has multiple arcs with gaps
            num_segments = random.randint(3, 6)
            
            # Calculate arc positions - leave gaps between arcs
            total_arc_degrees = random.randint(240, 320)
            gap_degrees = (360 - total_arc_degrees) / num_segments
            
            # Random starting position for variety
            current_angle = random.randint(0, 360)
            
            for seg_idx in range(num_segments):
                # Arc extent varies
                arc_extent = total_arc_degrees / num_segments + random.randint(-20, 20)
                arc_extent = max(20, min(120, arc_extent))
                
                # Pick a color - alternate and vary
                color = colors[(layer_idx + ring_idx + seg_idx) % len(colors)]
                
                # Slight variation in line width within layer
                line_width = base_line_width + (ring_idx % 2) * 0.15
                
                draw_broken_arc(c, cx, cy, radius, current_angle, arc_extent, color, line_width)
                
                # Move to next position (arc extent + gap)
                current_angle += arc_extent + gap_degrees + random.randint(-10, 10)


def draw_inner_border(c: canvas.Canvas, x: float, y: float, color: Color, padding: float = 8):
    """Draw the inner rectangular border with rounded corners."""
    c.setStrokeColor(color)
    c.setLineWidth(1.2)
    
    border_x = x + padding
    border_y = y + padding
    border_width = CARD_WIDTH - 2 * padding
    border_height = CARD_HEIGHT - 2 * padding
    
    c.rect(border_x, border_y, border_width, border_height, stroke=1, fill=0)


def draw_qr_front(c: canvas.Canvas, x: float, y: float, song: Song, card_num: int, theme: dict):
    """Draw the front of a card (QR code side) with concentric broken circles design on black background."""
    # Card center
    cx = x + CARD_WIDTH / 2
    cy = y + CARD_HEIGHT / 2
    
    # Draw solid black background
    c.setFillColor(black)
    c.setStrokeColor(black)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, stroke=1, fill=1)
    
    # QR code size
    qr_size = int(CARD_WIDTH * 0.50)
    
    # Draw concentric broken circles around the QR code area
    min_radius = qr_size / 2 + 8  # Start just outside QR code
    max_radius = min(CARD_WIDTH, CARD_HEIGHT) / 2 - 5  # Leave small margin from edge
    
    # Use card_num as seed for reproducible but varied patterns
    draw_concentric_broken_circles(c, cx, cy, min_radius, max_radius, CIRCLE_COLORS, seed=card_num)
    
    # Generate white QR code on transparent background
    qr_img = generate_spotify_qr(song.spotify_uri, size=qr_size, inverted=True)
    
    # Convert PIL image to reportlab-compatible format
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_reader = ImageReader(img_buffer)
    
    # Draw QR code centered (directly on black background)
    qr_x = cx - qr_size / 2
    qr_y = cy - qr_size / 2
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size, mask='auto')


def draw_song_back(c: canvas.Canvas, x: float, y: float, song: Song, card_num: int, theme: dict):
    """Draw the back of a card (song details side) with starburst design - ink-saving outline version."""
    primary_color = theme["primary"]
    light_accent = theme["light_accent"]
    
    # Card center
    cx = x + CARD_WIDTH / 2
    cy = y + CARD_HEIGHT / 2
    
    # Draw starburst lines in theme color (no filled background)
    inner_radius = 45
    outer_radius = min(CARD_WIDTH, CARD_HEIGHT) / 2 - 15
    
    draw_starburst_lines(c, cx, cy, inner_radius, outer_radius, light_accent, num_lines=48)
    
    # Draw inner border in theme color
    c.setStrokeColor(light_accent)
    c.setLineWidth(1.2)
    padding = 8
    c.rect(x + padding, y + padding, CARD_WIDTH - 2*padding, CARD_HEIGHT - 2*padding, stroke=1, fill=0)
    
    # Draw corner rosettes in theme color
    rosette_radius = 6
    corner_offset = 18
    
    draw_corner_rosette(c, x + corner_offset, y + CARD_HEIGHT - corner_offset, rosette_radius, light_accent)
    draw_corner_rosette(c, x + CARD_WIDTH - corner_offset, y + CARD_HEIGHT - corner_offset, rosette_radius, light_accent)
    draw_corner_rosette(c, x + corner_offset, y + corner_offset, rosette_radius, light_accent)
    draw_corner_rosette(c, x + CARD_WIDTH - corner_offset, y + corner_offset, rosette_radius, light_accent)
    
    # Central content area - white circle with colored border
    content_radius = 55
    c.setFillColor(white)
    c.circle(cx, cy, content_radius, stroke=0, fill=1)
    
    # Colored ring around content
    c.setStrokeColor(primary_color)
    c.setLineWidth(2)
    c.circle(cx, cy, content_radius, stroke=1, fill=0)
    
    # Year - large and prominent
    c.setFillColor(primary_color)
    c.setFont("Helvetica-Bold", 32)
    year_y = cy + 8
    c.drawCentredString(cx, year_y, str(song.year))
    
    # Song title - below year
    c.setFont("Helvetica-Bold", 8)
    title = song.title
    if len(title) > 20:
        title = title[:17] + "..."
    c.drawCentredString(cx, year_y - 22, title)
    
    # Artist - below title
    c.setFont("Helvetica", 7)
    c.setFillColor(HexColor("#666666"))
    artist = song.artist
    if len(artist) > 22:
        artist = artist[:19] + "..."
    c.drawCentredString(cx, year_y - 34, artist)
    
    # Outer card border in theme color
    c.setStrokeColor(primary_color)
    c.setLineWidth(1.5)
    c.rect(x, y, CARD_WIDTH, CARD_HEIGHT, stroke=1, fill=0)


def generate_cards_pdf(songs: List[Song], output_path: Path):
    """
    Generate a PDF with printable double-sided cards.
    
    The PDF alternates between front pages (QR codes) and back pages (song details).
    Cards on back pages are mirrored horizontally so they align when printed double-sided.
    
    Args:
        songs: List of Song objects to generate cards for
        output_path: Path where the PDF will be saved
    """
    page_width, page_height = A4
    cols, rows = calculate_cards_per_page(page_width, page_height)
    cards_per_page = cols * rows
    
    # Create PDF
    c = canvas.Canvas(str(output_path), pagesize=A4)
    
    # Calculate starting position (centered on page)
    total_cards_width = cols * CARD_WIDTH
    total_cards_height = rows * CARD_HEIGHT
    start_x = (page_width - total_cards_width) / 2
    start_y = (page_height - total_cards_height) / 2
    
    total_songs = len(songs)
    
    # Process songs in batches (one batch = one sheet of paper, front and back)
    for batch_start in range(0, len(songs), cards_per_page):
        batch = songs[batch_start:batch_start + cards_per_page]
        
        # Progress indicator
        progress = min(batch_start + cards_per_page, total_songs)
        print(f"  Generating cards {batch_start + 1}-{progress} of {total_songs}...")
        
        # === FRONT PAGE (QR codes) ===
        for idx, song in enumerate(batch):
            row = idx // cols
            col = idx % cols
            
            # Position from bottom-left
            x = start_x + (col * CARD_WIDTH)
            y = start_y + ((rows - 1 - row) * CARD_HEIGHT)  # Top to bottom
            
            card_num = batch_start + idx + 1
            # Get theme based on song's decade
            theme = get_decade_theme(song.year)
            
            draw_crop_marks(c, x, y)
            draw_qr_front(c, x, y, song, card_num, theme)
        
        c.showPage()
        
        # === BACK PAGE (Song details) ===
        # Mirror horizontally for double-sided printing
        for idx, song in enumerate(batch):
            row = idx // cols
            col = idx % cols
            
            # Mirror column position for double-sided printing
            mirrored_col = cols - 1 - col
            
            x = start_x + (mirrored_col * CARD_WIDTH)
            y = start_y + ((rows - 1 - row) * CARD_HEIGHT)
            
            card_num = batch_start + idx + 1
            # Use same theme based on song's decade
            theme = get_decade_theme(song.year)
            
            draw_crop_marks(c, x, y)
            draw_song_back(c, x, y, song, card_num, theme)
        
        c.showPage()
    
    c.save()
    print(f"\nGenerated {len(songs)} cards in {output_path}")
    print(f"Layout: {cols} columns x {rows} rows = {cards_per_page} cards per page")
    print(f"Total pages: {((len(songs) - 1) // cards_per_page + 1) * 2} (front + back)")
