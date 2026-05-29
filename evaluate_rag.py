import json
import os
from typing import List, Dict
from src.extractor.ingestion_pipeline import IngestionPipeline
from src.llm.rag_engine import RAGEngine
import time

class RAGEvaluator:
    def __init__(self, gt_path: str):
        self.gt_path = gt_path
        with open(gt_path, 'r', encoding='utf-8') as f:
            self.ground_truth = json.load(f)
        
        print("Cargando motor RAG para evaluación (Modo Rápido)...")
        pipeline = IngestionPipeline()
        
        # Obtenemos solo los archivos necesarios del GT para ahorrar tiempo
        target_docs = {entry['document'] for entry in self.ground_truth}
        pdf_paths = pipeline.loader.discover_pdfs("data/raw_pdfs/")
        filtered_paths = [p for p in pdf_paths if p.name in target_docs]
        
        print(f"Procesando solo {len(filtered_paths)} documentos relevantes...")
        
        all_chunks = []
        for pdf_path in filtered_paths:
            print(f"Procesando: {pdf_path.name}...")
            # Versión simplificada del pipeline para evaluación rápida
            markdown = pipeline.converter.convert_pdf_to_markdown(str(pdf_path), "data/markdown")
            sections = pipeline.parser.parse_sections(markdown)
            chunks = pipeline.chunker.chunk_sections(sections, pdf_path.name)
            all_chunks.extend(chunks)
        
        self.rag = RAGEngine(all_chunks)
        print("Motor RAG listo.")

    def run_evaluation(self) -> List[Dict]:
        results = []
        print(f"\nIniciando evaluación de {len(self.ground_truth)} preguntas...")
        
        for entry in self.ground_truth:
            print(f"Evaluando {entry['id']}: {entry['question']}...")
            start_time = time.time()
            
            try:
                # Ejecutar consulta al RAG
                response = self.rag.query(entry['question'])
                latency = time.time() - start_time
                print(f"Respuesta recibida en {latency:.2f}s")
                
                # Extraer información de fuentes
                found_sources = []
                correct_doc_found = False
                correct_page_found = False
                
                for source in response["sources"]:
                    source_info = {
                        "file": source.source_file,
                        "section": source.section_number,
                        "page": source.page_start
                    }
                    found_sources.append(source_info)
                    
                    if source.source_file == entry['document']:
                        correct_doc_found = True
                        if source.page_start == entry['expected_page']:
                            correct_page_found = True

                result = {
                    "id": entry["id"],
                    "question": entry["question"],
                    "expected_answer": entry["expected_answer"],
                    "generated_answer": response["answer"],
                    "expected_doc": entry["document"],
                    "expected_page": entry["expected_page"],
                    "found_sources": found_sources,
                    "correct_doc_found": correct_doc_found,
                    "correct_page_found": correct_page_found,
                    "latency_sec": round(latency, 2)
                }
                results.append(result)
            except Exception as e:
                print(f"Error evaluando {entry['id']}: {e}")
            
        return results

    def save_report(self, results: List[Dict], output_path: str):
        if not results:
            print("No se generaron resultados.")
            return

        total = len(results)
        doc_precision = sum(1 for r in results if r.get("correct_doc_found", False)) / total
        page_precision = sum(1 for r in results if r.get("correct_page_found", False)) / total
        
        with open(output_path, 'w', encoding='utf-8') as f:
            f.write("# Informe de Evaluación del Desempeño RAG - Corona\n\n")
            f.write(f"## Resumen de Métricas\n")
            f.write(f"- **Total de preguntas:** {total}\n")
            f.write(f"- **Precisión de Recuperación (Documento):** {doc_precision*100:.1f}%\n")
            f.write(f"- **Precisión de Recuperación (Página):** {page_precision*100:.1f}%\n")
            f.write(f"- **Latencia promedio:** {sum(r['latency_sec'] for r in results)/total:.2f}s\n\n")
            
            f.write("## Detalle por Pregunta\n")
            for r in results:
                f.write(f"### {r['id']}: {r['question']}\n")
                f.write(f"- **Esperado ({r['expected_doc']}, pág {r['expected_page']})**\n")
                f.write(f"- **Respuesta Generada:** {r['generated_answer']}\n")
                status_doc = "✅" if r['correct_doc_found'] else "❌"
                status_page = "✅" if r['correct_page_found'] else "❌"
                f.write(f"- **Trazabilidad:** Documento {status_doc}, Página {status_page}\n")
                f.write(f"- **Fuentes encontradas:** {r['found_sources']}\n\n")
                f.write("---\n\n")
        
        print(f"Reporte guardado en: {output_path}")

if __name__ == "__main__":
    evaluator = RAGEvaluator("data/evaluation/ground_truth.json")
    results = evaluator.run_evaluation()
    evaluator.save_report(results, "data/evaluation/results.md")
