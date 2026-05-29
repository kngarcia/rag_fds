import faiss
import numpy as np
from typing import List, Tuple
from src.chunker.models import Chunk


class VectorStore:
    """
    Almacén de vectores basado en FAISS para búsqueda semántica.
    """

    def __init__(self, dimension: int):
        self.dimension = dimension
        self.index = faiss.IndexFlatL2(dimension)
        self.chunks: List[Chunk] = []

    def add_chunks(self, chunks: List[Chunk], embeddings: np.ndarray):
        """
        Agrega chunks y sus embeddings al índice.
        """
        if len(chunks) != embeddings.shape[0]:
            raise ValueError("El número de chunks no coincide con el número de embeddings.")
        
        self.index.add(embeddings.astype('float32'))
        self.chunks.extend(chunks)

    def search(self, query_embedding: np.ndarray, k: int = 5) -> List[Tuple[Chunk, float]]:
        """
        Busca los k chunks más similares.
        """
        query_embedding = query_embedding.reshape(1, -1).astype('float32')
        distances, indices = self.index.search(query_embedding, k)
        
        results = []
        for dist, idx in zip(distances[0], indices[0]):
            if idx != -1:
                results.append((self.chunks[idx], float(dist)))
        
        return results

    def save(self, path: str):
        """
        Guarda el índice FAISS en disco.
        """
        faiss.write_index(self.index, path)

    def load(self, path: str, chunks: List[Chunk]):
        """
        Carga el índice FAISS desde disco.
        """
        self.index = faiss.read_index(path)
        self.chunks = chunks
