# RAG-FDS — Sistema RAG para Fichas de Datos de Seguridad

> Pipeline reproducible de procesamiento documental y consulta inteligente sobre FDS de pinturas **CORONA**, construido íntegramente con herramientas open source y cero dependencias de APIs externas.

**Asignatura:** Procesamiento de Lenguaje Natural (NLP) — Parcial Final  
**Fabricante asignado:** CORONA  
**Stack:** PyMuPDF · MarkItDown · sentence-transformers · FAISS · BM25 · Ollama (phi3)

---

## Tabla de Contenidos

- [Descripción](#-descripción)
- [Arquitectura](#-arquitectura)
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Requisitos](#-requisitos)
- [Instalación y Ejecución](#-instalación-y-ejecución)
- [Pipeline Documental](#-pipeline-documental)
- [Sistema RAG](#-sistema-rag)
- [Trazabilidad](#-trazabilidad)
- [Limitaciones Conocidas](#-limitaciones-conocidas)
- [Trabajo Futuro](#-trabajo-futuro)

---

## Descripción

Este proyecto implementa un sistema **RAG (Retrieval-Augmented Generation)** para consultar Fichas de Datos de Seguridad (FDS) en formato PDF, convirtiendo los documentos a Markdown estructurado, extrayendo las **16 secciones normativas GHS/SGA**, y respondiendo preguntas en lenguaje natural con trazabilidad completa hacia el fragmento fuente.

### Características principales

- ✅ Conversión PDF → Markdown preservando estructura normativa GHS
- ✅ Extracción y validación de las 16 secciones obligatorias (Decreto 1496/2018 · Resolución 773/2021)
- ✅ Chunking semántico por sección y párrafo con metadatos de página
- ✅ Recuperación híbrida: búsqueda vectorial (FAISS) + palabras clave (BM25) con Reciprocal Rank Fusion
- ✅ Generación con LLM local vía Ollama — **sin APIs externas, sin costo por token**
- ✅ Trazabilidad fuente → página → sección → imagen en cada respuesta
- ✅ Pipeline reproducible desde cualquier conjunto de PDFs de FDS

---

## 🏗️ Arquitectura

```
PDFs (data/raw_pdfs/)
       │
       ├──▶ PDFLoader (fitz/PyMuPDF)
       │       validación · descubrimiento · soporte ZIP
       │
       ├──▶ ImageExtractor (fitz/PyMuPDF)
       │       extrae imágenes por página → data/images/
       │
       └──▶ MarkdownConverter (MarkItDown + MarkdownCleaner)
               normalización · mark_pages([[PAGE_X]]) · normalize_section_titles()
               → data/markdown/fds_91.md
                       │
                       ├──▶ SectionParser (regex)
                       │       extrae 16 secciones GHS · valida completitud
                       │
                       └──▶ SemanticChunker
                               max=1500 chars · division por párrafos/oraciones
                               → List[Chunk] con metadatos completos
                                       │
                               TraceabilityBuilder
                               asocia imágenes a chunks por página
                                       │
                    ┌──────────────────┴──────────────────┐
                    │                                       │
           EmbeddingsManager                        BM25Retriever
           (all-MiniLM-L6-v2)                       (BM25Okapi)
           384 dimensiones                          keywords exactos
                    │                                       │
              VectorStore                            BM25 scores
           (FAISS IndexFlatL2)                             │
                    └──────────────┬────────────────────────┘
                                   │
                          HybridRetriever
                     Reciprocal Rank Fusion (rrf_k=60)
                                   │
                            top-k Chunks
                                   │
                          PromptBuilder
                   contexto trazable + pregunta usuario
                                   │
                       OllamaClient (phi3 local)
                                   │
                    Respuesta + sources (trazabilidad)
```

### Decisiones de diseño

| Componente | Elección | Justificación |
|---|---|---|
| PDF parsing | MarkItDown | Preserva listas y tablas en Markdown sin configuración adicional · MIT |
| Extracción de imágenes | PyMuPDF (fitz) | API programática nativa, sin herramientas externas |
| Embeddings | `all-MiniLM-L6-v2` (384d) | Modelo compacto (22M params), ejecución local, descarga única |
| Índice vectorial | FAISS CPU `IndexFlatL2` | Sin servidor, portable, costo de infraestructura cero |
| Recuperación keywords | BM25Okapi (rank_bm25) | Captura términos técnicos exactos: CAS, códigos H, regulaciones |
| Fusión de rankings | Reciprocal Rank Fusion | Robusto, sin calibrar scores heterogéneos, sin parámetros frágiles |
| LLM | Ollama + phi3 (3.8B) | Local, cero costo por token, cumple restricción de zero APIs externas |
| Chunking | Por sección GHS + párrafo | Respeta la semántica normativa; trazabilidad sección→chunk unívoca |

---

## 📁 Estructura del Proyecto

```
rag_fds-main/
├── main.py                          # Punto de entrada · CLI interactiva
├── requirements.txt                 # Dependencias pip
│
├── data/
│   ├── raw_pdfs/                    # PDFs de entrada (FDS CORONA)
│   ├── markdown/                    # Markdown generado (fds_91.md)
│   └── images/                      # Imágenes extraídas por página
│
└── src/
    ├── extractor/
    │   ├── ingestion_pipeline.py    # Orquestador del pipeline de ingesta
    │   ├── pdf_loader.py            # PDFLoader · validación · descubrimiento · ZIP
    │   ├── markdown_converter.py    # MarkItDown wrapper + limpieza
    │   ├── markdown_cleaner.py      # Normalización · mark_pages · section titles
    │   └── image_extractor.py       # Extracción de imágenes por página (fitz)
    │
    ├── parser/
    │   ├── section_parser.py        # Regex GHS · extracción 16 secciones · validación
    │   └── traceability_builder.py  # Asociación imagen↔chunk · contexto trazable
    │
    ├── chunker/
    │   ├── models.py                # Dataclass Chunk (metadatos completos)
    │   └── semantic_chunker.py      # Chunking por sección/párrafo/oración + PAGE tracking
    │
    ├── retrieval/
    │   ├── embeddings.py            # EmbeddingsManager (sentence-transformers)
    │   ├── vector_store.py          # VectorStore (FAISS IndexFlatL2)
    │   ├── bm25_retriever.py        # BM25Retriever (rank_bm25 / BM25Okapi)
    │   └── hybrid_retriever.py      # HybridRetriever (Reciprocal Rank Fusion)
    │
    └── llm/
        ├── ollama_client.py         # Cliente Ollama local (phi3)
        ├── prompt_builder.py        # Prompt trazable · system prompt experto en FDS
        └── rag_engine.py            # RAGEngine · orquestador de consulta completa
```

---

## ⚙️ Requisitos

### Software

- Python ≥ 3.11 (ver `.python-version`)
- [Ollama](https://ollama.com/) instalado localmente

### Modelo LLM

```bash
ollama pull phi3
```

### Dependencias Python

```
pymupdf
markitdown
sentence-transformers
faiss-cpu
rank-bm25
ollama
numpy
```

---

## Instalación y Ejecución

```bash
# 1. Clonar el repositorio
git clone https://github.com/<usuario>/rag_fds-main.git
cd rag_fds-main

# 2. Crear entorno virtual e instalar dependencias
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

# 3. Asegurarse de tener Ollama corriendo con phi3
ollama serve &
ollama pull phi3

# 4. Colocar los PDFs de FDS en la carpeta de entrada
cp /ruta/a/tus/pdfs/*.pdf data/raw_pdfs/

# 5. Ejecutar el sistema
python main.py
```

### Uso interactivo

```
=== SDS RAG System - Corona ===

Iniciando ingesta de documentos...
Encontrados 1 archivos PDF.
Procesando: fds_91.pdf...
  - Extrayendo imágenes...
  - Convirtiendo a Markdown...
  - Parseando secciones...
  - Generando chunks semánticos...
  - Vinculando imágenes y trazabilidad...
  ✓ Procesado exitosamente. Generados 32 chunks.

Ingesta completada. 32 chunks procesados.
Inicializando RAG Engine...

========================================
SISTEMA LISTO. Puedes hacer preguntas sobre las FDS.
Escribe 'salir' para terminar.
========================================

Pregunta: ¿Qué componentes peligrosos contiene la pintura?
Buscando respuesta...

-------------------- RESPUESTA --------------------
Según la Sección 3 del documento fds_91.pdf (pág. 1), la pintura contiene:
- Dióxido de titanio (CAS 13463-67-7), clasificado como Carc. 2 (H351),
  en concentración del 10 al 20%.
- Piritionato cíncico (CAS 13463-41-7), con múltiples clasificaciones de
  peligro (H400, H410, H318, H360, H372, H330, H301), en concentración
  menor al 5%.
[Fuente: fds_91.pdf, Sección 3: COMPOSICIÓN/INFORMACIÓN SOBRE LOS COMPONENTES]
---------------------------------------------------

Fuentes consultadas:
1. fds_91.pdf - Sección 3, pág. 1
2. fds_91.pdf - Sección 2, pág. 1
```

---

## Pipeline Documental

El pipeline se ejecuta automáticamente al correr `main.py`. Los pasos son:

| Paso | Clase / Función | Descripción |
|---|---|---|
| 1 | `PDFLoader.discover_pdfs()` | Descubre PDFs en directorio, archivo individual o ZIP |
| 2 | `PDFLoader.validate_pdf()` | Valida existencia, extensión y apertura con fitz |
| 3 | `ImageExtractor.extract_images()` | Extrae imágenes por página → `data/images/{stem}_p{N}_img{M}.{ext}` |
| 4 | `MarkdownConverter.convert_pdf_to_markdown()` | MarkItDown + MarkdownCleaner → `data/markdown/{stem}.md` |
| 5 | `SectionParser.parse_sections()` | Regex sobre `## SECCIÓN N: ...` → dict de 16 secciones |
| 6 | `SectionParser.validate_sections()` | Verifica presencia de secciones 1–16, reporta faltantes |
| 7 | `SemanticChunker.chunk_sections()` | Divide por párrafos respetando fronteras de sección |
| 8 | `TraceabilityBuilder.associate_images_to_chunks()` | Asocia imágenes a chunks por número de página |

### Marcadores de página en Markdown

El cleaner convierte `Página X/Y` en tokens estructurados embebidos en el Markdown:

```markdown
## SECCIÓN 3: COMPOSICIÓN/INFORMACIÓN SOBRE LOS COMPONENTES

CAS: 13463-67-7 | Dioxido de titanio Carc.2 | 10-<20%
CAS: 13463-41-7 | Piritionato cincico        | <5%

[[PAGE_1]]

## SECCIÓN 4: PRIMEROS AUXILIOS
...
```

Estos tokens permiten al chunker rastrear la página de cada fragmento sin acceder al PDF original en tiempo de retrieval.

---

## Sistema RAG

### Recuperación híbrida

Para cada consulta se ejecutan dos estrategias en paralelo y sus resultados se fusionan con **Reciprocal Rank Fusion**:

```python
# Búsqueda semántica (FAISS)
vector_results = vector_store.search(query_embedding, k=k*2)

# Búsqueda por keywords (BM25)
bm25_results = bm25_retriever.search(query, k=k*2)

# RRF: score = Σ 1 / (rrf_k + rank)   con rrf_k = 60
scores[chunk_id] += 1.0 / (60 + rank + 1)
```

La búsqueda semántica captura consultas conceptuales ("¿qué hacer en caso de exposición?") mientras BM25 recupera con precisión términos técnicos exactos ("CAS 13463-67-7", "H400", "Decreto 1496").

### Dataclass Chunk

Cada fragmento del corpus lleva sus metadatos de trazabilidad completos:

```python
@dataclass
class Chunk:
    chunk_id:       str           # "{section_num}_{chunk_index}"  ej: "9_2"
    content:        str           # Texto limpio del chunk
    section_number: str           # "9"
    section_title:  str           # "PROPIEDADES FÍSICAS Y QUÍMICAS..."
    source_file:    str           # "fds_91.pdf"
    chunk_index:    int
    token_count:    int           # len(content.split())
    page_start:     Optional[int] # Detectado desde [[PAGE_X]]
    page_end:       Optional[int]
    metadata:       dict          # {"images": ["fds_91_p4_img0.png"]}
```

---

## 🔍 Trazabilidad

La trazabilidad se implementa en cuatro capas complementarias:

| Capa | Mecanismo | Implementación |
|---|---|---|
| **Marcadores de página** | `[[PAGE_X]]` embebidos en Markdown | `MarkdownCleaner.mark_pages()` |
| **Metadatos del Chunk** | `page_start`, `section_number`, `source_file` | `Chunk` dataclass |
| **Asociación imagen↔chunk** | Cruce por número de página | `TraceabilityBuilder.associate_images_to_chunks()` |
| **Contexto trazable en prompt** | Bloques `--- FUENTE N [archivo, pág., Sección] ---` | `TraceabilityBuilder.build_traceable_context()` |

El system prompt instruye explícitamente al LLM a citar siempre la fuente, la página y la sección, y a abstenerse de generar información no presente en el contexto.

---

## 🔬 Tests

```bash
# Test del loader
python test_loader.py

# Test del converter
python test_converter.py

# Test del cleaner
python test_cleaner.py

# Test del section parser
python test_section_parser.py

# Test de trazabilidad
python test_traceability.py
```

---

## ⚠️ Limitaciones Conocidas

| Limitación | Descripción |
|---|---|
| Sin OCR | Solo procesa PDFs con capa de texto digital. PDFs escaneados producen texto vacío. |
| Overlap sin activar | El parámetro `overlap=200` está declarado en `SemanticChunker` pero no se aplica en `_split_content_with_pages()`. |
| Índice FAISS efímero | El índice se regenera en cada arranque. Los métodos `VectorStore.save()` y `load()` existen pero no se invocan en `main.py`. |
| Embeddings en inglés | `all-MiniLM-L6-v2` fue entrenado primariamente en inglés. Para mejor rendimiento en español: `paraphrase-multilingual-MiniLM-L12-v2`. |
| Duplicación de secciones | La paginación del PDF genera encabezados de sección repetidos en el Markdown, creando chunks redundantes. |

---

## Trabajo Futuro

- [ ] Activar persistencia del índice FAISS (`VectorStore.save()` / `load()`)
- [ ] Reemplazar modelo de embeddings por `paraphrase-multilingual-MiniLM-L12-v2`
- [ ] Implementar el `overlap` en `_split_content_with_pages()`
- [ ] Integrar OCR (Tesseract / EasyOCR) como fallback para páginas escaneadas
- [ ] Deduplicar secciones repetidas antes del chunking
- [ ] Script de evaluación automática con ground truth (15 pares Q/A documentados)
- [ ] Interfaz web con FastAPI + Streamlit
- [ ] Reranking con cross-encoder posterior al retriever híbrido

---

## 📦 Dependencias

```txt
pymupdf              # Lectura de PDF y extracción de imágenes
markitdown           # Conversión PDF → Markdown
sentence-transformers # Embeddings locales (all-MiniLM-L6-v2)
faiss-cpu            # Índice vectorial sin servidor
rank-bm25            # Recuperación BM25Okapi
ollama               # Cliente para LLM local (phi3)
numpy                # Operaciones matriciales
```

> **Costo total de infraestructura: $0.**  
> Todo corre en local. No se requieren cuentas en la nube, claves de API ni bases de datos externas.

---

## 📄 Licencia

Proyecto académico — uso educativo.
