import os
import sys
from pathlib import Path
from src.extractor.ingestion_pipeline import IngestionPipeline
from src.llm.rag_engine import RAGEngine


def main():
    print("=== SDS RAG System - Corona ===")
    
    # 1. Configuración de rutas
    input_pdfs = "data/raw_pdfs/"
    if not os.path.exists(input_pdfs):
        os.makedirs(input_pdfs, exist_ok=True)
        print(f"Directorio {input_pdfs} creado. Por favor, añade PDFs para procesar.")
        return

    # 2. Ingestión de documentos
    pipeline = IngestionPipeline()
    print("\nIniciando ingesta de documentos...")
    chunks = pipeline.run(input_pdfs)
    
    if not chunks:
        print("No se generaron chunks. Verifica los archivos PDF en data/raw_pdfs/")
        return
    
    # 3. Inicializar el motor RAG
    print(f"\nIngesta completada. {len(chunks)} chunks procesados.")
    rag_engine = RAGEngine(chunks)
    
    # 4. Bucle de consulta
    print("\n" + "="*40)
    print("SISTEMA LISTO. Puedes hacer preguntas sobre las FDS.")
    print("Escribe 'salir' para terminar.")
    print("="*40)
    
    while True:
        query = input("\nPregunta: ").strip()
        
        if query.lower() in ['salir', 'exit', 'quit']:
            break
        
        if not query:
            continue
            
        print("Buscando respuesta...")
        try:
            result = rag_engine.query(query)
            
            print("\n" + "-"*20 + " RESPUESTA " + "-"*20)
            print(result["answer"])
            print("-" * 51)
            
            print("\nFuentes consultadas:")
            for i, source in enumerate(result["sources"]):
                page_info = f", pág. {source.page_start}" if source.page_start else ""
                imgs = source.metadata.get("images", [])
                img_info = f" (Imágenes: {', '.join(imgs)})" if imgs else ""
                print(f"{i+1}. {source.source_file} - Sección {source.section_number}{page_info}{img_info}")
                
        except Exception as e:
            print(f"Error procesando la consulta: {e}")
            import traceback
            traceback.print_exc()

if __name__ == "__main__":
    main()
