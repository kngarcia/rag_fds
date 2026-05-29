from pathlib import Path
from dataclasses import dataclass
from typing import List
import fitz  # PyMuPDF
import zipfile


# =========================================
# DOCUMENT METADATA
# =========================================

@dataclass
class PDFDocument:

    path: Path
    filename: str
    total_pages: int
    file_size_mb: float


# =========================================
# PDF LOADER
# =========================================

class PDFLoader:

    def __init__(self):

        self.allowed_extension = ".pdf"

    # =====================================
    # VALIDATE FILE
    # =====================================

    def validate_pdf(self, pdf_path: str):

        path = Path(pdf_path)

        # File exists
        if not path.exists():
            raise FileNotFoundError(
                f"PDF not found: {pdf_path}"
            )

        # Correct extension
        if path.suffix.lower() != self.allowed_extension:
            raise ValueError(
                f"Invalid file type: {path.suffix}"
            )

        # Try opening PDF
        try:
            pdf = fitz.open(pdf_path)
            pdf.close()

        except Exception as e:
            raise ValueError(
                f"Corrupted or invalid PDF: {e}"
            )

    # =====================================
    # DISCOVER PDFS
    # =====================================

    def discover_pdfs(self, path: str) -> List[Path]:
        """
        Detectar y listar PDFs en una ruta (archivo, carpeta o ZIP).
        """
        path_obj = Path(path)
        pdf_files = []

        if path_obj.is_file():
            if path_obj.suffix.lower() == ".pdf":
                pdf_files.append(path_obj)
            elif path_obj.suffix.lower() == ".zip":
                pdf_files.extend(self._handle_zip(path_obj))
        elif path_obj.is_dir():
            pdf_files.extend(list(path_obj.glob("**/*.pdf")))

        return pdf_files

    def _handle_zip(self, zip_path: Path) -> List[Path]:
        """
        Extrae PDFs de un archivo ZIP a un directorio temporal.
        """
        temp_dir = Path("data/temp_extracted")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        extracted_pdfs = []
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            for file in zip_ref.namelist():
                if file.lower().endswith('.pdf'):
                    zip_ref.extract(file, temp_dir)
                    extracted_pdfs.append(temp_dir / file)
        
        return extracted_pdfs

    # =====================================
    # LOAD PDF
    # =====================================

    def load_pdf(self, pdf_path: str) -> PDFDocument:

        # Validate first
        self.validate_pdf(pdf_path)

        path = Path(pdf_path)

        pdf = fitz.open(pdf_path)

        total_pages = len(pdf)

        pdf.close()

        file_size_mb = (
            path.stat().st_size / (1024 * 1024)
        )

        document = PDFDocument(
            path=path,
            filename=path.name,
            total_pages=total_pages,
            file_size_mb=round(file_size_mb, 2)
        )

        return document
