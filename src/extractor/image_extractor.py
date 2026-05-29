import fitz
from pathlib import Path
from typing import List, Dict


class ImageExtractor:
    """
    Extrae imágenes de un PDF y las guarda asociadas a su página.
    """

    def __init__(self, output_dir: str = "data/images"):
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def extract_images(self, pdf_path: str) -> List[Dict]:
        """
        Extrae todas las imágenes del PDF y retorna metadatos de las mismas.
        """
        pdf_path_obj = Path(pdf_path)
        doc = fitz.open(pdf_path)
        extracted_metadata = []

        for page_index in range(len(doc)):
            page = doc[page_index]
            image_list = page.get_images(full=True)

            for img_index, img in enumerate(image_list):
                xref = img[0]
                base_image = doc.extract_image(xref)
                image_bytes = base_image["image"]
                image_ext = base_image["ext"]
                
                image_filename = f"{pdf_path_obj.stem}_p{page_index}_img{img_index}.{image_ext}"
                image_path = self.output_dir / image_filename
                
                with open(image_path, "wb") as f:
                    f.write(image_bytes)
                
                extracted_metadata.append({
                    "page": page_index + 1,
                    "filename": image_filename,
                    "path": str(image_path),
                    "xref": xref
                })

        doc.close()
        return extracted_metadata
