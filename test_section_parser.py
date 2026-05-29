from pathlib import Path

from src.parser.section_parser import (
    SectionParser
)

markdown_path = (
    Path("data/markdown/fds_91.md")
)

markdown = markdown_path.read_text(
    encoding="utf-8"
)

parser = SectionParser()

sections = parser.parse_sections(markdown)

validation = parser.validate_sections(
    sections
)

print("\nVALIDATION:")
print(validation)

print("\nSECTIONS FOUND:\n")

for sec_num, sec_data in sections.items():

    print(
        f"SECTION {sec_num}: "
        f"{sec_data['title']}"
    )

    print(
        sec_data["content"][:1000]
    )

    print("\n" + "="*50 + "\n")