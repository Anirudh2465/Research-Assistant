import fitz  # PyMuPDF
from pathlib import Path
from backend.core.logging import logger

def extract_text_blocks(pdf_path: str):
    doc = fitz.open(pdf_path)
    blocks = []
    for page_num, page in enumerate(doc):
        text_blocks = page.get_text("blocks")
        for b in text_blocks:
            # (x0, y0, x1, y1, "lines", block_no, block_type)
            if b[6] == 0: # Text
                blocks.append({
                    "text": b[4],
                    "page": page_num + 1,
                    # "rect": b[:4]
                })
    return blocks

def extract_images(pdf_path: str, output_dir: Path):
    doc = fitz.open(pdf_path)
    images = []
    for page_num, page in enumerate(doc):
        image_list = page.get_images(full=True)
        for img_index, img in enumerate(image_list):
            xref = img[0]
            base_image = doc.extract_image(xref)
            image_bytes = base_image["image"]
            ext = base_image["ext"]
            
            image_filename = f"p{page_num+1}_img{img_index}.{ext}"
            image_path = output_dir / image_filename
            
            with open(image_path, "wb") as f:
                f.write(image_bytes)
            
            images.append({
                "path": str(image_path),
                "page": page_num + 1,
                "caption": None # OCR/Context needed for caption
            })
    return images
