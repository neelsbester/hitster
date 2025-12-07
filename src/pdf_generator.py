"""PDF generator for printable double-sided cards."""

from io import BytesIO
from pathlib import Path
from typing import List

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import inch, mm
from reportlab.lib.colors import black, white, HexColor
from reportlab.pdfgen import canvas
from reportlab.lib.utils import ImageReader

from .csv_parser import Song
from .qr_generator import generate_spotify_qr


# Card dimensions (poker card size)
CARD_WIDTH = 2.5 * inch
CARD_HEIGHT = 3.5 * inch

# Page margins
MARGIN = 0.5 * inch

# Colors
CARD_BG_COLOR = white
CARD_BORDER_COLOR = HexColor("#333333")
QR_BG_COLOR = HexColor("#1DB954")  # Spotify green
TEXT_COLOR = black
YEAR_COLOR = HexColor("#1DB954")


def calculate_cards_per_page(page_width: float, page_height: float) -> tuple:
    """Calculate how many cards fit on a page."""
    usable_width = page_width - (2 * MARGIN)
    usable_height = page_height - (2 * MARGIN)
    
    cols = int(usable_width // CARD_WIDTH)
    rows = int(usable_height // CARD_HEIGHT)
    
    return cols, rows


def draw_card_border(c: canvas.Canvas, x: float, y: float):
    """Draw a card border with rounded corners."""
    c.setStrokeColor(CARD_BORDER_COLOR)
    c.setLineWidth(1)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=5*mm, stroke=1, fill=0)


def draw_crop_marks(c: canvas.Canvas, x: float, y: float, length: float = 5*mm):
    """Draw crop marks at card corners for cutting guide."""
    c.setStrokeColor(CARD_BORDER_COLOR)
    c.setLineWidth(0.5)
    
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


def draw_qr_front(c: canvas.Canvas, x: float, y: float, song: Song, card_num: int):
    """Draw the front of a card (QR code side)."""
    # Card background
    c.setFillColor(CARD_BG_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=5*mm, stroke=0, fill=1)
    
    # Border
    draw_card_border(c, x, y)
    
    # Generate QR code
    qr_size = int(CARD_WIDTH * 0.7)
    qr_img = generate_spotify_qr(song.spotify_uri, size=qr_size)
    
    # Convert PIL image to reportlab-compatible format
    img_buffer = BytesIO()
    qr_img.save(img_buffer, format='PNG')
    img_buffer.seek(0)
    qr_reader = ImageReader(img_buffer)
    
    # Center QR code on card
    qr_x = x + (CARD_WIDTH - qr_size) / 2
    qr_y = y + (CARD_HEIGHT - qr_size) / 2 + 10
    
    c.drawImage(qr_reader, qr_x, qr_y, width=qr_size, height=qr_size)
    
    # Card number at bottom
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica", 10)
    c.drawCentredString(x + CARD_WIDTH/2, y + 15, f"#{card_num}")
    
    # "SCAN ME" text at top
    c.setFont("Helvetica-Bold", 12)
    c.drawCentredString(x + CARD_WIDTH/2, y + CARD_HEIGHT - 25, "SCAN TO PLAY")


def draw_song_back(c: canvas.Canvas, x: float, y: float, song: Song, card_num: int):
    """Draw the back of a card (song details side)."""
    # Card background
    c.setFillColor(CARD_BG_COLOR)
    c.roundRect(x, y, CARD_WIDTH, CARD_HEIGHT, radius=5*mm, stroke=0, fill=1)
    
    # Border
    draw_card_border(c, x, y)
    
    # Year (large, prominent)
    c.setFillColor(YEAR_COLOR)
    c.setFont("Helvetica-Bold", 48)
    year_y = y + CARD_HEIGHT/2 + 20
    c.drawCentredString(x + CARD_WIDTH/2, year_y, str(song.year))
    
    # Song title
    c.setFillColor(TEXT_COLOR)
    c.setFont("Helvetica-Bold", 11)
    title_y = year_y - 40
    
    # Truncate long titles
    title = song.title
    if len(title) > 25:
        title = title[:22] + "..."
    c.drawCentredString(x + CARD_WIDTH/2, title_y, title)
    
    # Artist
    c.setFont("Helvetica", 10)
    artist_y = title_y - 18
    
    artist = song.artist
    if len(artist) > 28:
        artist = artist[:25] + "..."
    c.drawCentredString(x + CARD_WIDTH/2, artist_y, artist)
    
    # Card number at bottom
    c.setFont("Helvetica", 10)
    c.drawCentredString(x + CARD_WIDTH/2, y + 15, f"#{card_num}")


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
    
    # Process songs in batches (one batch = one sheet of paper, front and back)
    for batch_start in range(0, len(songs), cards_per_page):
        batch = songs[batch_start:batch_start + cards_per_page]
        
        # === FRONT PAGE (QR codes) ===
        for idx, song in enumerate(batch):
            row = idx // cols
            col = idx % cols
            
            # Position from bottom-left
            x = start_x + (col * CARD_WIDTH)
            y = start_y + ((rows - 1 - row) * CARD_HEIGHT)  # Top to bottom
            
            card_num = batch_start + idx + 1
            draw_crop_marks(c, x, y)
            draw_qr_front(c, x, y, song, card_num)
        
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
            draw_crop_marks(c, x, y)
            draw_song_back(c, x, y, song, card_num)
        
        c.showPage()
    
    c.save()
    print(f"Generated {len(songs)} cards in {output_path}")
    print(f"Layout: {cols} columns x {rows} rows = {cards_per_page} cards per page")
    print(f"Total pages: {((len(songs) - 1) // cards_per_page + 1) * 2} (front + back)")

