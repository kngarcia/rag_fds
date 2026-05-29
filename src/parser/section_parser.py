import re


class SectionParser:

    def __init__(self):

        self.section_pattern = re.compile(
            r"(?m)^##\s*SECCIÓN\s+(\d+)\s*:\s*(.+)$"
        )

    def parse_sections(self, markdown: str) -> dict:

        matches = list(
            self.section_pattern.finditer(markdown)
        )

        sections = {}

        for i, match in enumerate(matches):

            section_number = match.group(1)

            section_title = match.group(2).strip()

            start = match.end()

            end = (
                matches[i + 1].start()
                if i + 1 < len(matches)
                else len(markdown)
            )

            content = markdown[start:end].strip()

            sections[section_number] = {
                "section_number": section_number,
                "title": section_title,
                "content": content
            }

        return sections

    def validate_sections(
        self,
        sections: dict
    ) -> dict:

        expected_sections = [
            str(i) for i in range(1, 17)
        ]

        found_sections = list(sections.keys())

        missing_sections = []

        for sec in expected_sections:

            if sec not in found_sections:
                missing_sections.append(sec)

        return {
            "total_found": len(found_sections),
            "missing_sections": missing_sections,
            "is_complete": len(missing_sections) == 0
        }