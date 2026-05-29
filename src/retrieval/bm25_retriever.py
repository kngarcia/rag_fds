from typing import List, Tuple
from rank_bm25 import BM25Okapi
from src.chunker.models import Chunk


class BM25Retriever:
    """
    Recuperador basado en palabras clave usando el algoritmo BM25.
    """

    def __init__(self, chunks: List[Chunk]):
        self.chunks = chunks
        self.tokenized_corpus = [chunk.content.lower().split() for chunk in chunks]
        self.bm25 = BM25Okapi(self.tokenized_corpus)

    def search(self, query: str, k: int = 5) -> List[Tuple[Chunk, float]]:
        """
        Busca los k chunks más relevantes usando BM25.
        """
        tokenized_query = query.lower().split()
        scores = self.bm25.get_scores(tokenized_query)
        
        # Obtener los índices ordenados por score descendente
        top_n_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]
        
        results = []
        for idx in top_n_indices:
            results.append((self.chunks[idx], float(scores[idx])))
        
        return results
