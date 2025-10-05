import json
try:
    import ollama
except ImportError:
    print("Warning: ollama library not installed. Run: pip install ollama")
    ollama = None


class HCISChatbot:
    """
    AI chatbot for explaining HCIS analysis results
    """
    
    def __init__(self, model_name="llama3.2:latest"):
        self.model_name = model_name
        self.conversation_history = []
        
        if ollama is None:
            print("Chatbot will not function - ollama not installed")
        else:
            print(f"Chatbot initialized with model: {model_name}")
    
    def create_system_prompt(self):
        """System instructions for the chatbot"""
        return """You are an AI assistant for the Holistic Content Integrity System (HCIS).
Your role is to explain deepfake detection results clearly and helpfully.

Key responsibilities:
- Explain why content was flagged as authentic, suspicious, or fake
- Describe what each component (video, audio, text) detected
- Provide recommendations for further verification
- Answer questions about detection methods

Be concise, accurate, and helpful. Avoid technical jargon unless asked."""
    
    def explain_results(self, analysis_results, user_question=None):
        """
        Generate explanation of HCIS results
        
        Args:
            analysis_results: Dict from fusion engine
            user_question: Optional specific question
            
        Returns:
            AI-generated explanation
        """
        if ollama is None:
            return "Error: Ollama not installed. Please install ollama library."
        
        # Build context from results
        context = self._build_context(analysis_results)
        
        # Create prompt
        if user_question:
            prompt = f"{context}\n\nUser Question: {user_question}\n\nResponse:"
        else:
            prompt = f"{context}\n\nProvide a clear explanation of these results."
        
        # Get response from LLM
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                system=self.create_system_prompt(),
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 300
                }
            )
            
            return response['response']
            
        except Exception as e:
            return f"Error generating response: {str(e)}"
    
    def _build_context(self, results):
        """Build context string from analysis results"""
        verdict = results.get('verdict', 'UNKNOWN')
        final_score = results.get('final_score', 0)
        confidence = results.get('confidence', 0)
        
        scores = results.get('component_scores', {})
        video = scores.get('video', 0)
        audio = scores.get('audio', 0)
        text = scores.get('text', 0)
        
        explanation = results.get('explanation', '')
        
        context = f"""
HCIS Analysis Results:

Overall Verdict: {verdict}
Final Score: {final_score:.1f}%
System Confidence: {confidence:.1f}%

Component Scores:
- Video Analysis: {video:.1f}%
- Audio Analysis: {audio:.1f}%
- Text Verification: {text:.1f}%

Technical Explanation: {explanation}
"""
        return context
    
    def chat(self, message, context_results=None):
        """
        General chat interface
        
        Args:
            message: User's message
            context_results: Optional HCIS results for context
            
        Returns:
            Chatbot response
        """
        if ollama is None:
            return "Chatbot unavailable - ollama not installed"
        
        # Add to conversation history
        self.conversation_history.append({
            'role': 'user',
            'content': message
        })
        
        # Build prompt with context if available
        if context_results:
            full_prompt = f"{self._build_context(context_results)}\n\nUser: {message}"
        else:
            full_prompt = message
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                system=self.create_system_prompt()
            )
            
            bot_response = response['response']
            
            # Add to history
            self.conversation_history.append({
                'role': 'assistant',
                'content': bot_response
            })
            
            return bot_response
            
        except Exception as e:
            return f"Error: {str(e)}"


# Test
if __name__ == "__main__":
    chatbot = HCISChatbot()
    
    # Mock results
    test_results = {
        'verdict': 'SUSPICIOUS',
        'final_score': 45.0,
        'confidence': 75.0,
        'component_scores': {
            'video': 70,
            'audio': 25,
            'text': 80
        },
        'explanation': 'Audio exhibits synthetic characteristics'
    }
    
    explanation = chatbot.explain_results(test_results)
    print(f"\nExplanation:\n{explanation}")