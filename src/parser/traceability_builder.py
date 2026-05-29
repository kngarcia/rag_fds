from typing import List, Dict
from src.chunker.models import Chunk


class TraceabilityBuilder:
    """
    Se encarga de mantener y formatear la trazabilidad entre el contenido extraído
    y su fuente original (PDF, página, imágenes).
    """

    @staticmethod
    def associate_images_to_chunks(chunks: List[Chunk], images_metadata: List[Dict]) -> List[Chunk]:
        """
        Asocia nombres de archivos de imagen a chunks basándose en el número de página.
        """
        for chunk in chunks:
            if chunk.page_start:
                # Encontrar imágenes que pertenecen a la misma página que el chunk
                chunk_images = [
                    img["filename"] for img in images_metadata 
                    if img["page"] == chunk.page_start
                ]
                
                # Asegurar que no duplicamos imágenes si ya existen en metadata
                existing_images = chunk.metadata.get("images", [])
                for img in chunk_images:
                    if img not in existing_images:
                        existing_images.append(img)
                
                chunk.metadata["images"] = existing_images
        
        return chunks

    @staticmethod
    def format_citation(chunk: Chunk) -> str:
        """
        Formatea una cita legible para ser usada por el LLM o mostrada al usuario.
        """
        source = chunk.source_file
        page = f"pág. {chunk.page_start}" if chunk.page_start else "pág. desconocida"
        section = f"Sección {chunk.section_number}: {chunk.section_title}"
        
        citation = f"[{source}, {page}, {section}]"
        return citation

    @staticmethod
    def build_traceable_context(chunks: List[Chunk]) -> str:
        """
        Construye un contexto enriquecido con metadatos de trazabilidad para el Prompt.
        """
        context_blocks = []
        for i, chunk in enumerate(chunks):
            citation = TraceabilityBuilder.format_citation(chunk)
            block = f"--- FUENTE {i+1} {citation} ---\n{chunk.content}\n"
            context_blocks.append(block)
        
        return "\n".join(context_blocks)
