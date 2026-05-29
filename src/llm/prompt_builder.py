from typing import List
from src.chunker.models import Chunk
from src.parser.traceability_builder import TraceabilityBuilder


class PromptBuilder:
    """
    Construye prompts estructurados para el sistema RAG, asegurando trazabilidad.
    """

    SYSTEM_PROMPT = (
        "Eres un asistente experto en seguridad industrial y Fichas de Datos de Seguridad (SDS/FDS).\n"
        "Tu objetivo es responder preguntas basadas exclusivamente en el contexto proporcionado.\n"
        "REGLAS CRÍTICAS:\n"
        "1. Cita siempre la fuente, la página y la sección para cada afirmación importante.\n"
        "2. Si la información no está en el contexto, di que no lo sabes. No inventes.\n"
        "3. Usa un tono profesional y técnico.\n"
        "4. Si hay imágenes asociadas a la fuente citada, menciónalas por su nombre de archivo."
    )

    @staticmethod
    def build_rag_prompt(query: str, retrieved_chunks: List[Chunk]) -> str:
        """
        Crea el prompt final para el LLM.
        """
        context = TraceabilityBuilder.build_traceable_context(retrieved_chunks)
        
        prompt = (
            f"Basándote en la siguiente información de las Fichas de Datos de Seguridad:\n\n"
            f"{context}\n\n"
            f"Pregunta del usuario: {query}\n\n"
            f"Respuesta trazable:"
        )
        
        return prompt
