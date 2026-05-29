from typing import List
import numpy as np
from sentence_transformers import SentenceTransformer


class EmbeddingsManager:
    """
    Gestiona la generación de embeddings para chunks y consultas.
    """

    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)

    def get_embeddings(self, texts: List[str]) -> np.ndarray:
        """
        Genera embeddings para una lista de textos.
        """
        return self.model.encode(texts, convert_to_numpy=True)

    def get_query_embedding(self, query: str) -> np.ndarray:
        """
        Genera el embedding para una consulta única.
        """
        return self.model.encode([query], convert_to_numpy=True)[0]
