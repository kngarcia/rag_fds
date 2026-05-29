from pathlib import Path

from markitdown import MarkItDown

from src.extractor.markdown_cleaner import MarkdownCleaner


class MarkdownConverter:

    def __init__(self):

        self.md = MarkItDown(enable_plugins=False)

        self.cleaner = MarkdownCleaner()

    def convert_pdf_to_markdown(
        self,
        pdf_path: str,
        output_dir: str
    ) -> str:

        try:

            result = self.md.convert(pdf_path)

            raw_markdown = result.text_content

            clean_markdown = self.cleaner.clean(
                raw_markdown
            )

            output_path = (
                Path(output_dir) /
                f"{Path(pdf_path).stem}.md"
            )

            with open(
                output_path,
                "w",
                encoding="utf-8"
            ) as f:

                f.write(clean_markdown)

            return clean_markdown

        except Exception as e:

            raise RuntimeError(
                f"Markdown conversion failed: {e}"
            )