import os
import logging
import google.generativeai as genai
from dotenv import load_dotenv

class GeminiAIService:
    def __init__(self):
        self.logger = logging.getLogger("GeminiAIService")
        # Load dotenv relative to the project root
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_root, ".env")
        load_dotenv(dotenv_path)
        self.api_key = os.getenv("GEMINI_API_KEY")
        self.model = None
        self.history = []  # Active chat session history (up to last 4 turns)
        
        if self.api_key and self.api_key.strip() != "" and "YOUR_" not in self.api_key:
            try:
                genai.configure(api_key=self.api_key)
                # Initialize Gemini model with concise assistant behavior
                self.model = genai.GenerativeModel(
                    model_name="gemini-2.5-flash",
                    generation_config={"max_output_tokens": 150},
                    system_instruction=(
                        "You are a modern, lightweight desktop virtual assistant. "
                        "Keep your responses extremely helpful, precise, and under 2 sentences."
                    )
                )
            except Exception as e:
                self.logger.error(f"Failed to initialize Gemini GenerativeModel: {e}")
                self.model = None

    def get_response(self, user_query):
        """Sends the user's query to Gemini and returns the assistant's reply.
        Gracefully falls back to mock responses if the API key is not configured."""
        if not self.model:
            return self._get_mock_fallback(user_query)

        try:
            # Build conversation history context
            formatted_history = []
            for role, text in self.history:
                formatted_history.append({"role": role, "parts": [text]})
            
            # Append current turn
            formatted_history.append({"role": "user", "parts": [user_query]})
            
            # Request generation
            response = self.model.generate_content(formatted_history)
            reply = response.text.strip()
            
            # Update history cache
            self.history.append(("user", user_query))
            self.history.append(("model", reply))
            if len(self.history) > 8: # Keep last 4 turns (8 items)
                self.history = self.history[-8:]
                
            return reply
            
        except Exception as e:
            self.logger.error(f"Gemini API execution error: {e}")
            return f"API Connection Error: Could not reach Gemini. Details: {str(e)}"

    def _get_mock_fallback(self, query):
        """Provides smart, contextual mock replies when no API key is available."""
        q = query.lower().strip()
        
        # Simple rule-based mock chat
        if any(greet in q for greet in ["hello", "hi", "hey", "greetings"]):
            return "Hello! I am your AI Virtual Assistant. Please configure your GEMINI_API_KEY in the .env file to enable full conversations!"
        
        if "your name" in q or "who are you" in q:
            return "I am the AI Desktop Assistant. I can launch apps, search the web, check weather, or chat once my API key is set."
            
        if "thank" in q:
            return "You're welcome! Let me know if you need anything else."
            
        if "help" in q:
            return "You can type commands like 'open notepad', 'open calculator', 'weather in Paris', or search Wikipedia. Add your Gemini API key in the .env file to unlock conversational capabilities."
            
        # Generic conversational response outlining missing credentials
        return (
            f"You asked: '{query}'. To answer conversational questions like this, I need a valid Gemini API Key. "
            "Please register one for free at aistudio.google.com and set it as GEMINI_API_KEY in your .env file."
        )
