from typing import List, Dict, Any
from src.retrieval.embeddings import EmbeddingsManager
from src.retrieval.vector_store import VectorStore
from src.retrieval.bm25_retriever import BM25Retriever
from src.retrieval.hybrid_retriever import HybridRetriever
from src.llm.ollama_client import OllamaClient
from src.llm.prompt_builder import PromptBuilder
from src.chunker.models import Chunk


class RAGEngine:
    """
    Orquestador principal del sistema RAG.
    """

    def __init__(
        self, 
        chunks: List[Chunk], 
        embeddings_model: str = "all-MiniLM-L6-v2",
        ollama_model: str = "phi3"
    ):
        print("Inicializando RAG Engine...")
        self.chunks = chunks
        
        # 1. Preparar Embeddings
        self.embeddings_manager = EmbeddingsManager(model_name=embeddings_model)
        chunk_texts = [c.content for c in chunks]
        embeddings = self.embeddings_manager.get_embeddings(chunk_texts)
        
        # 2. Configurar Recuperadores
        self.vector_store = VectorStore(dimension=embeddings.shape[1])
        self.vector_store.add_chunks(chunks, embeddings)
        
        self.bm25_retriever = BM25Retriever(chunks)
        
        self.hybrid_retriever = HybridRetriever(
            self.vector_store, 
            self.bm25_retriever
        )
        
        # 3. Configurar LLM
        self.ollama_client = OllamaClient(model_name=ollama_model)
        self.prompt_builder = PromptBuilder()

    def query(self, question: str, k: int = 4) -> Dict[str, Any]:
        """
        Procesa una consulta completa.
        """
        # A. Obtener embedding de la consulta
        query_embedding = self.embeddings_manager.get_query_embedding(question)
        
        # B. Recuperar chunks relevantes (Híbrido)
        relevant_chunks = self.hybrid_retriever.search(
            question, 
            query_embedding, 
            k=k
        )
        
        # C. Construir Prompt
        prompt = self.prompt_builder.build_rag_prompt(question, relevant_chunks)
        
        # D. Generar respuesta
        answer = self.ollama_client.generate_response(
            prompt, 
            system_prompt=self.prompt_builder.SYSTEM_PROMPT
        )
        
        return {
            "question": question,
            "answer": answer,
            "sources": relevant_chunks
        }
