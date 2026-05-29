import ollama
from typing import List, Dict, Any


class OllamaClient:
    """
    Cliente para interactuar con Ollama localmente.
    """

    def __init__(self, model_name: str = "phi3"):
        self.model_name = model_name

    def generate_response(self, prompt: str, system_prompt: str = "") -> str:
        """
        Envía un prompt a Ollama y devuelve la respuesta.
        """
        messages = []
        if system_prompt:
            messages.append({'role': 'system', 'content': system_prompt})
        
        messages.append({'role': 'user', 'content': prompt})
        
        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']

    def chat(self, messages: List[Dict[str, str]]) -> str:
        """
        Mantiene una conversación completa.
        """
        response = ollama.chat(model=self.model_name, messages=messages)
        return response['message']['content']
