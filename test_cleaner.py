from src.extractor.markdown_converter import MarkdownConverter

converter = MarkdownConverter()

markdown = converter.convert_pdf_to_markdown(
    pdf_path="data/raw_pdfs/fds_91.pdf",
    output_dir="data/markdown"
)

print(markdown[:5000])