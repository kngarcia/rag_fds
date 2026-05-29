from src.extractor.markdown_converter import (
    MarkdownConverter
)

converter = MarkdownConverter()

markdown = converter.convert_pdf_to_markdown(
    "data/raw_pdfs/fds_91.pdf"
)

print(markdown[:3000])

converter.save_markdown(
    markdown,
    "data/markdown/fds_91_raw.md"
)

print("\nMarkdown saved successfully")