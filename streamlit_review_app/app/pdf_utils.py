import fitz  # PyMuPDF
import os
import base64
from io import BytesIO

def get_pdf_region(pdf_path, region):
    """Extracts a specific region from the first page of the PDF."""
    try:
        doc = fitz.open(pdf_path)
        page = doc[0]  # Process only the first page

        # Get page dimensions
        page_rect = page.rect
        width, height = page_rect.width, page_rect.height

        # Define regions
        regions = {
            "header": fitz.Rect(0, 0, width, height * 0.25),
            "line_items": fitz.Rect(0, height * 0.35, width, height * 0.8),
            "footer": fitz.Rect(0, height * 0.8, width, height),
        }

        # Ensure the region is valid
        if region not in regions:
            raise ValueError(f"Invalid region '{region}'. Valid regions are: {list(regions.keys())}.")

        # Extract the specified region
        pixmap = page.get_pixmap(clip=regions[region])
        return pixmap.tobytes("png")

    except Exception as e:
        print(f"Error in get_pdf_region: {e}")
        return None

