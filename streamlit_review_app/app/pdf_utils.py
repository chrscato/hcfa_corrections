import fitz  # PyMuPDF
import os
import base64
from io import BytesIO

def get_pdf_region(pdf_folder, filename, region):
    """Extract a specific region of a PDF as a base64-encoded image."""
    pdf_filename = os.path.splitext(filename)[0] + '.pdf'
    pdf_path = os.path.join(pdf_folder, pdf_filename)
    
    if not os.path.exists(pdf_path):
        raise FileNotFoundError(f"PDF file not found: {pdf_path}")
    
    # Open PDF and extract the region
    doc = fitz.open(pdf_path)
    page = doc[0]  # Assuming the first page
    page_rect = page.rect
    height = page_rect.height
    width = page_rect.width
    
    regions = {
        'header': fitz.Rect(0, 0, width, height * 0.25),  # Top 25%
        'line_items': fitz.Rect(0, height * 0.35, width, height * 0.8),  # Middle section
        'footer': fitz.Rect(0, height * 0.8, width, height),  # Bottom 20%
    }
    
    if region not in regions:
        raise ValueError(f"Invalid region: {region}")
    
    # Render region as image
    rect = regions[region]
    pix = page.get_pixmap(clip=rect)
    img_data = pix.tobytes("png")
    
    # Convert image to base64
    img_base64 = base64.b64encode(img_data).decode("utf-8")
    return f"data:image/png;base64,{img_base64}"
