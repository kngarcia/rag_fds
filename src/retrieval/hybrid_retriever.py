from typing import List, Dict, Tuple
from src.chunker.models import Chunk
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_retriever import BM25Retriever


class HybridRetriever:
    """
    Combina búsqueda semántica (VectorStore) y búsqueda por palabras clave (BM25)
    usando Reciprocal Rank Fusion (RRF).
    """

    def __init__(self, vector_store: VectorStore, bm25_retriever: BM25Retriever):
        self.vector_store = vector_store
        self.bm25_retriever = bm25_retriever

    def search(self, query: str, query_embedding: List[float], k: int = 5, rrf_k: int = 60) -> List[Chunk]:
        """
        Ejecuta búsqueda híbrida y fusiona los resultados.
        """
        # 1. Obtener resultados de ambos recuperadores (pedimos un poco más para la fusión)
        vector_results = self.vector_store.search(query_embedding, k=k*2)
        bm25_results = self.bm25_retriever.search(query, k=k*2)

        # 2. Aplicar Reciprocal Rank Fusion (RRF)
        # rrf_score = sum( 1 / (k + rank) )
        scores: Dict[str, float] = {}
        chunks_map: Dict[str, Chunk] = {}

        # Procesar resultados vectoriales
        for rank, (chunk, _) in enumerate(vector_results):
            chunk_id = f"{chunk.source_file}_{chunk.chunk_id}"
            chunks_map[chunk_id] = chunk
            scores[chunk_id] = scores.get(chunk_id, 0) + (1.0 / (rrf_k + rank + 1))

        # Procesar resultados BM25
        for rank, (chunk, _) in enumerate(bm25_results):
            chunk_id = f"{chunk.source_file}_{chunk.chunk_id}"
            chunks_map[chunk_id] = chunk
            scores[chunk_id] = scores.get(chunk_id, 0) + (1.0 / (rrf_k + rank + 1))

        # 3. Ordenar por score RRF y devolver top k
        sorted_ids = sorted(scores.keys(), key=lambda x: scores[x], reverse=True)[:k]
        
        return [chunks_map[cid] for cid in sorted_ids]
