from src.extractor.pdf_loader import PDFLoader

loader = PDFLoader()

document = loader.load_pdf(
    "data/raw_pdfs/fds_91.pdf"
)

print(document)