from pathlib import Path
from typing import List
from src.extractor.pdf_loader import PDFLoader
from src.extractor.markdown_converter import MarkdownConverter
from src.parser.section_parser import SectionParser
from src.parser.traceability_builder import TraceabilityBuilder
from src.chunker.semantic_chunker import SemanticChunker
from src.chunker.models import Chunk


from src.extractor.image_extractor import ImageExtractor


class IngestionPipeline:
    """
    Orquesta el flujo completo desde PDF hasta Chunks estructurados.
    """

    def __init__(self, output_dir: str = "data/markdown", image_dir: str = "data/images"):
        self.loader = PDFLoader()
        self.converter = MarkdownConverter()
        self.parser = SectionParser()
        self.traceability = TraceabilityBuilder()
        self.chunker = SemanticChunker()
        self.image_extractor = ImageExtractor(output_dir=image_dir)
        self.output_dir = Path(output_dir)
        self.output_dir.mkdir(parents=True, exist_ok=True)

    def run(self, input_path: str) -> List[Chunk]:
        """
        Ejecuta la tubería para una ruta dada (archivo, carpeta o ZIP).
        """
        all_chunks = []
        
        # 1. Descubrir archivos
        pdf_paths = self.loader.discover_pdfs(input_path)
        print(f"Encontrados {len(pdf_paths)} archivos PDF.")
        
        for pdf_path in pdf_paths:
            print(f"Procesando: {pdf_path.name}...")
            
            try:
                # 2. Extraer imágenes (Trazabilidad visual)
                print(f"  - Extrayendo imágenes...")
                images_metadata = self.image_extractor.extract_images(str(pdf_path))
                
                # 3. Convertir y limpiar
                print(f"  - Convirtiendo a Markdown...")
                markdown = self.converter.convert_pdf_to_markdown(
                    str(pdf_path), 
                    str(self.output_dir)
                )
                
                # 4. Parsear secciones
                print(f"  - Parseando secciones...")
                sections = self.parser.parse_sections(markdown)
                validation = self.parser.validate_sections(sections)
                
                if not validation["is_complete"]:
                    print(f"  Advertencia: Secciones faltantes en {pdf_path.name}: {validation['missing_sections']}")
                
                # 5. Chunking con metadatos de página
                print(f"  - Generando chunks semánticos...")
                chunks = self.chunker.chunk_sections(sections, pdf_path.name)
                
                # 6. Asociar imágenes a chunks basándose en la página (Traceability)
                print(f"  - Vinculando imágenes y trazabilidad...")
                chunks = self.traceability.associate_images_to_chunks(chunks, images_metadata)
                
                all_chunks.extend(chunks)
                
                print(f"  ✓ Procesado exitosamente. Generados {len(chunks)} chunks.")
                
            except Exception as e:
                print(f"  ✗ Error procesando {pdf_path.name}: {e}")
                import traceback
                traceback.print_exc()
                
        return all_chunks



if __name__ == "__main__":
    # Prueba rápida
    pipeline = IngestionPipeline()
    chunks = pipeline.run("data/raw_pdfs/")
    print(f"\nTotal de chunks generados: {len(chunks)}")
