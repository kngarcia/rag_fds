import re
from typing import List
from src.chunker.models import Chunk
from src.parser.section_parser import SectionParser


class SemanticChunker:
    """
    Divide documentos SDS en fragmentos semánticos basados en su estructura.
    Evita cortes arbitrarios y preserva la integridad de las secciones y párrafos.
    """

    def __init__(self, max_chunk_size: int = 1500, overlap: int = 200):
        self.max_chunk_size = max_chunk_size
        self.overlap = overlap

    def chunk_sections(self, sections: dict, source_file: str) -> List[Chunk]:
        """
        Toma el diccionario de secciones (output del SectionParser) y lo divide en Chunks.
        """
        all_chunks = []
        
        for sec_num, sec_data in sections.items():
            title = sec_data["title"]
            content = sec_data["content"]
            
            # Detectar página inicial de la sección (buscando marcador [[PAGE_X]])
            page_match = re.search(r'\[\[PAGE_(\d+)\]\]', content)
            start_page = int(page_match.group(1)) if page_match else None

            # Si el contenido es pequeño, un solo chunk
            if len(content) <= self.max_chunk_size:
                # Limpiar marcadores antes de guardar el contenido del chunk
                clean_content = re.sub(r'\[\[PAGE_\d+\]\]', '', content).strip()
                chunk = Chunk(
                    chunk_id=f"{sec_num}_0",
                    content=clean_content,
                    section_number=sec_num,
                    section_title=title,
                    source_file=source_file,
                    chunk_index=0,
                    token_count=len(clean_content.split()),
                    page_start=start_page,
                    page_end=start_page
                )
                all_chunks.append(chunk)
            else:
                # Si es grande, dividimos por párrafos o bloques
                sub_chunks_data = self._split_content_with_pages(content, start_page)
                for i, sub_data in enumerate(sub_chunks_data):
                    sub_content = sub_data["content"]
                    chunk_page = sub_data["page"]
                    chunk = Chunk(
                        chunk_id=f"{sec_num}_{i}",
                        content=sub_content,
                        section_number=sec_num,
                        section_title=title,
                        source_file=source_file,
                        chunk_index=i,
                        token_count=len(sub_content.split()),
                        page_start=chunk_page,
                        page_end=chunk_page
                    )
                    all_chunks.append(chunk)
                    
        return all_chunks

    def _split_content_with_pages(self, content: str, initial_page: int) -> List[dict]:
        """
        Divide el contenido y rastrea cambios de página.
        """
        current_page = initial_page
        paragraphs = re.split(r'\n\s*\n', content)
        
        chunks_data = []
        current_chunk_text = ""
        current_chunk_page = current_page
        
        for para in paragraphs:
            para = para.strip()
            if not para:
                continue
            
            # Detectar cambio de página
            page_match = re.search(r'\[\[PAGE_(\d+)\]\]', para)
            if page_match:
                current_page = int(page_match.group(1))
                para = re.sub(r'\[\[PAGE_\d+\]\]', '', para).strip()
                if not para: continue
            
            if len(para) > self.max_chunk_size:
                if current_chunk_text:
                    chunks_data.append({"content": current_chunk_text.strip(), "page": current_chunk_page})
                    current_chunk_text = ""
                
                # Dividir párrafo largo
                sentences = re.split(r'(?<=[.!?])\s+', para)
                temp_chunk = ""
                for sent in sentences:
                    if len(temp_chunk) + len(sent) < self.max_chunk_size:
                        temp_chunk += sent + " "
                    else:
                        chunks_data.append({"content": temp_chunk.strip(), "page": current_page})
                        temp_chunk = sent + " "
                if temp_chunk:
                    current_chunk_text = temp_chunk
                    current_chunk_page = current_page
            else:
                if len(current_chunk_text) + len(para) < self.max_chunk_size:
                    if not current_chunk_text:
                        current_chunk_page = current_page
                    current_chunk_text += para + "\n\n"
                else:
                    chunks_data.append({"content": current_chunk_text.strip(), "page": current_chunk_page})
                    current_chunk_text = para + "\n\n"
                    current_chunk_page = current_page
        
        if current_chunk_text:
            chunks_data.append({"content": current_chunk_text.strip(), "page": current_chunk_page})
            
        return chunks_data
