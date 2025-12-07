"""PDF generator for printable double-sided cards with premium starburst design."""

from io import BytesIO
from pathlib import Path
from typing import List
import math

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, white, HexColor, Color
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from .csv_parser import Song
from .qr_generator import generate_spotify_qr


# Card dimensions (poker card size)
CARD_WIDTH = 2.5 * inch
CARD_HEIGHT = 3.5 * inch

# Page margins
MARGIN = 0.5 * inch

# 5 Color Themes from the template (cycling through cards)
COLOR_THEMES = [
    {
        "name": "gray",
        "primary": HexColor("#5a5a5a"),      # Gray
        "light_accent": HexColor("#7a7a7a"),  # Lighter gray for lines
    },
    {
        "name": "teal",
        "primary": HexColor("#2a9d8f"),       # Teal/Green
        "light_accent": HexColor("#40b4a6"),  # Lighter teal
    },
    {
        "name": "orange",
        "primary": HexColor("#e9a033"),       # Orange/Amber
        "light_accent": HexColor("#f0b454"),  # Lighter orange
    },
    {
        "name": "red",
        "primary": HexColor("#c53a3a"),       # Red
        "light_accent": HexColor("#d65555"),  # Lighter red
    },
    {
        "name": "purple",
        "primary": HexColor("#6b2d5c"),       # Dark Purple/Maroon
        "light_accent": HexColor("#8a4275"),  # Lighter purple
    },
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


def draw_inner_border(c: canvas.Canvas, x: float, y: float, color: Color, padding: float = 8):
    """Draw the inner rectangular border with rounded corners."""
    c.setStrokeColor(color)
    c.setLineWidth(1.2)
    
    border_x = x + padding
    border_y = y + padding
    border_width = CARD_WIDTH - 2 * padding
    border_height = CARD_HEIGHT - 2 * padding
    
    c.roundRect(border_x, border_y, border_width, border_height, 
                radius=3*mm, stroke=1, fill=0)


def draw_qr_front(c: canvas.Canvas, x: float, y: float, song: Song, card_num: int, theme: dict):
    """Draw the front of a card (QR code side) with starburst design - ink-saving outline version."""
    # Card center (no filled background to save ink)
    cx = x + CARD_WIDTH / 2
    cy = y + CARD_HEIGHT / 2
    
    # Draw starburst lines radiating from center
    # Inner radius should be outside the QR code area
    qr_size = int(CARD_WIDTH * 0.55)
    inner_radius = qr_size / 2 + 15
    outer_radius = min(CARD_WIDTH, CARD_HEIGHT) / 2 - 15
    
    draw_starburst_lines(c, cx, cy, inner_radius, outer_radius, theme["light_accent"])
    
    # Draw inner border
    draw_inner_border(c, x, y, theme["light_accent"])
    
    # Draw corner rosettes
    rosette_radius = 6
    corner_offset = 18
    rosette_color = theme["light_accent"]
    
    # Four corners
    draw_corner_rosette(c, x + corner_offset, y + CARD_HEIGHT - corner_offset, rosette_radius, rosette_color)
    draw_corner_rosette(c, x + CARD_WIDTH - corner_offset, y + CARD_HEIGHT - corner_offset, rosette_radius, rosette_color)
    draw_corner_rosette(c, x + corner_offset, y + corner_offset, rosette_radius, rosette_color)
    draw_corner_rosette(c, x + CARD_WIDTH - corner_offset, y + corner_offset, rosette_radius, rosette_color)
    
    # Generate QR code
    qr_img = generate_spotify_qr(song.spotify_uri, size=qr_size)
    
    # Convert PIL image to reportlab-compatible format
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_reader = ImageReader(img_buffer)
    
    # QR code container - circular background
    qr_container_radius = qr_size / 2 + 12
    c.setFillColor(white)
    c.setStrokeColor(theme["primary"])
    c.setLineWidth(2)
    c.circle(cx, cy, qr_container_radius, stroke=1, fill=1)
    
    # Draw QR code centered
    qr_x = cx - qr_size / 2
    qr_y = cy - qr_size / 2
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Outer card border
    c.setStrokeColor(CARD_BORDER_LIGHT)
    c.setLineWidth(1)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=5*mm, stroke=1, fill=0)


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
    c.roundRect(x + padding, y + padding, CARD_WIDTH - 2*padding, CARD_HEIGHT - 2*padding, 
                radius=3*mm, stroke=1, fill=0)
    
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
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=5*mm, stroke=1, fill=0)


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
    num_themes = len(COLOR_THEMES)
    
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
            # Cycle through color themes
            theme = COLOR_THEMES[(card_num - 1) % num_themes]
            
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
            # Use same theme as front
            theme = COLOR_THEMES[(card_num - 1) % num_themes]
            
            draw_crop_marks(c, x, y)
            draw_song_back(c, x, y, song, card_num, theme)
        
        c.showPage()
    
    c.save()
    print(f"\nGenerated {len(songs)} cards in {output_path}")
    print(f"Layout: {cols} columns x {rows} rows = {cards_per_page} cards per page")
    print(f"Total pages: {((len(songs) - 1) // cards_per_page + 1) * 2} (front + back)")
