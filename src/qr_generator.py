"""QR code generator for Spotify URIs."""

import qrcode
from qrcode.image.pil import PilImage
from PIL import Image
from io import BytesIO


def generate_qr_code(data: str, size: int = 200) -> Image.Image:
    """
    Generate a QR code image for the given data.
    
    Args:
        data: The data to encode in the QR code (e.g., spotify:track:xxx)
        size: The desired size of the QR code in pixels
        
    Returns:
        PIL Image object containing the QR code
    """
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_M,
        box_size=10,
        border=2,
    )
    qr.add_data(data)
    qr.make(fit=True)
    
    img = qr.make_image(fill_color="black", back_color="white")
    
    # Resize to desired size
    img = img.resize((size, size), Image.Resampling.LANCZOS)
    
    return img


def generate_spotify_qr(spotify_uri: str, size: int = 200) -> Image.Image:
    """
    Generate a QR code for a Spotify URI.
    
    When scanned on a mobile device, this will open directly in the Spotify app.
    
    Args:
        spotify_uri: Spotify URI (e.g., spotify:track:4cOdK2wGLETKBW3PvgPWqT)
        size: The desired size of the QR code in pixels
        
    Returns:
        PIL Image object containing the QR code
    """
    return generate_qr_code(spotify_uri, size)


def qr_to_bytes(img: Image.Image, format: str = "PNG") -> bytes:
    """
    Convert a PIL Image to bytes.
    
    Useful for embedding in PDFs or other formats.
    
    Args:
        img: PIL Image object
        format: Image format (PNG, JPEG, etc.)
        
    Returns:
        Image data as bytes
    """
    buffer = BytesIO()
    img.save(buffer, format=format)
    buffer.seek(0)
    return buffer.getvalue()

