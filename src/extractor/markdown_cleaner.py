import re


class MarkdownCleaner:

    def mark_pages(self, text: str) -> str:
        """
        Convierte indicadores de página en marcadores estructurados.
        Ejemplo: Página 1/16 -> [[PAGE_1]]
        """
        def replace_page(match):
            page_num = match.group(1)
            return f"\n\n[[PAGE_{page_num}]]\n\n"

        # Buscar "Página X/Y" o similar
        pattern = r'Página\s+(\d+)(?:/\d+)?'
        return re.sub(pattern, replace_page, text, flags=re.IGNORECASE)

    def clean(self, markdown: str) -> str:

        markdown = self.remove_form_feed(markdown)
        
        markdown = self.mark_pages(markdown)

        markdown = self.remove_page_headers(markdown)

        # markdown = self.remove_page_footers(markdown) # Ahora usamos mark_pages

        markdown = self.normalize_section_titles(markdown)

        markdown = self.remove_continua_text(markdown)

        markdown = self.normalize_spacing(markdown)

        return markdown.strip()

    def remove_form_feed(self, text: str) -> str:
        """
        Elimina caracteres especiales tipo \f
        """
        return text.replace("\f", "")

    def remove_page_headers(self, text: str) -> str:
        """
        Elimina headers repetidos de cada página
        """

        patterns = [
            r'Ficha de datos de seguridad.*?\n',
            r'PINTURA EXTERIORES\s*\n',
            r'Emisión:.*?Versión:.*?\n'
        ]

        for pattern in patterns:
            text = re.sub(
                pattern,
                '',
                text,
                flags=re.IGNORECASE
            )

        return text

    def remove_page_footers(self, text: str) -> str:
        """
        Elimina pies de página
        """

        patterns = [
            r'Página\s+\d+/\d+',
            r'- CONTINÚA EN LA SIGUIENTE PÁGINA -'
        ]

        for pattern in patterns:
            text = re.sub(
                pattern,
                '',
                text,
                flags=re.IGNORECASE
            )

        return text

    def normalize_section_titles(self, text: str) -> str:
        """
        Convierte:
        SECCIÓN 1: IDENTIFICACIÓN
        
        en:
        ## SECCIÓN 1: IDENTIFICACIÓN
        """

        pattern = r'(SECCIÓN\s+\d+\s*:\s*.+)'

        return re.sub(
            pattern,
            r'\n## \1\n',
            text,
            flags=re.IGNORECASE
        )

    def remove_continua_text(self, text: str) -> str:
        """
        Elimina "(continúa)"
        """

        return re.sub(
            r'\(continúa\)',
            '',
            text,
            flags=re.IGNORECASE
        )

    def normalize_spacing(self, text: str) -> str:
        """
        Limpia saltos excesivos
        """

        text = re.sub(r'\n{3,}', '\n\n', text)

        text = re.sub(r'[ \t]{2,}', ' ', text)

        return text