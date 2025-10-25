import json
try:
    import ollama
except ImportError:
    print("Warning: ollama library not installed. Run: pip install ollama")
    ollama = None


class HCISChatbot:
    """
    AI chatbot that can:
    1. Explain HCIS analysis results when requested
    2. Have normal conversations about deepfakes, AI, etc.
    """
    
    def __init__(self, model_name="llama3.2:latest"):
        self.model_name = model_name
        self.conversation_history = []
        
        if ollama is None:
            print("⚠️  Chatbot will not function - ollama not installed")
        else:
            print(f"✅ Chatbot initialized with model: {model_name}")
    
    def create_system_prompt(self, mode="general"):
        """
        Create system prompts for different modes
        
        Args:
            mode: "general" for normal chat, "analysis" for explaining results
        """
        if mode == "analysis":
            return """You are an AI assistant for the Holistic Content Integrity System (HCIS).
Your role is to explain deepfake detection results clearly and helpfully.

Key responsibilities:
- Explain why content was flagged as authentic, suspicious, or fake
- Describe what each component (video, audio, text) detected based on its score
- Provide recommendations for further verification
- Answer user questions based on the provided HCIS analysis results

Be concise, accurate, and helpful. Reference the Fusion Score and Component Scores provided in the context."""
        
        else:  # general mode
            return """You are a helpful AI assistant specializing in deepfake detection, AI-generated content, and digital media authenticity.

You can:
- Answer general questions about deepfakes, AI, technology, and any other topics
- Explain how deepfake detection works
- Discuss current events, science, history, etc.
- Have natural conversations on any topic

IMPORTANT: Only reference HCIS analysis results if the user explicitly asks about them or if context is provided. Otherwise, have a normal conversation like any AI assistant would.

Be friendly, helpful, and conversational."""
    
    def explain_results(self, analysis_results, user_question=None):
        """
        Generate explanation of HCIS results (used for initial summary in Detector page)
        
        Args:
            analysis_results: Dict from fusion engine
            user_question: Optional specific question
            
        Returns:
            AI-generated explanation
        """
        if ollama is None:
            return "Error: Ollama not installed. Please install ollama library."
        
        # Build context using fusion results
        context = self._build_analysis_context(analysis_results)
        
        # Create prompt
        if user_question:
            prompt = f"{context}\n\nUser Question: {user_question}\n\nResponse:"
        else:
            prompt = f"{context}\n\nProvide a clear, detailed explanation of the analysis results, including the verdict and what each component score means."
        
        # Get response from LLM in ANALYSIS mode
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=prompt,
                system=self.create_system_prompt(mode="analysis"),
                options={
                    'temperature': 0.7,
                    'top_p': 0.9,
                    'max_tokens': 300
                }
            )
            
            return response['response']
            
        except Exception as e:
            print(f"❌ LLM Generation Error: {e}")
            return self._fallback_explanation(analysis_results)
    
    def _build_analysis_context(self, results):
        """
        Build context string for analysis explanation
        """
        score = results.get('fusion_score', 0)
        verdict = results.get('verdict', 'UNKNOWN')
        
        video = results.get('video_score', 0)
        audio = results.get('audio_score', 0)
        text = results.get('text_score', 0)
        
        active_modalities = results.get('active_modalities', [])
        
        context = f"""
HCIS Analysis Results:

Overall Verdict: {verdict}
Fusion Score: {score:.2f}%

Component Scores:
- Video: {video:.2f}% {'(Analyzed)' if 'video' in active_modalities else '(Not Analyzed)'}
- Audio: {audio:.2f}% {'(Analyzed)' if 'audio' in active_modalities else '(Not Analyzed)'}
- Text: {text:.2f}% {'(Analyzed)' if 'text' in active_modalities else '(Not Analyzed)'}

Active Components: {', '.join(active_modalities)}
"""
        return context
    
    def _fallback_explanation(self, results):
        """Fallback explanation when LLM fails"""
        score = results.get('fusion_score', 0)
        verdict = results.get('verdict', 'UNKNOWN')
        
        if score >= 70:
            return f"The content has been analyzed with a fusion score of {score:.1f}%, indicating it appears to be {verdict}. The analysis found no significant signs of manipulation."
        elif score >= 40:
            return f"The content received a fusion score of {score:.1f}%, marking it as {verdict}. Some inconsistencies were detected that warrant further investigation."
        else:
            return f"The content scored {score:.1f}%, classified as {verdict}. Multiple indicators suggest this may be manipulated or AI-generated content."
    
    def chat(self, message, context_results=None):
        """
        General chat interface - can handle both normal conversation and analysis questions
        
        Args:
            message: User's message
            context_results: Optional - only include if user is asking about specific analysis
            
        Returns:
            AI response
        """
        if ollama is None:
            return "Chatbot unavailable - ollama not installed"
        
        # Detect if user is asking about analysis results
        analysis_keywords = [
            'analysis', 'score', 'result', 'detection', 'authentic', 
            'fake', 'deepfake', 'report', 'verdict', 'component',
            'video score', 'audio score', 'text score', 'fusion'
        ]
        
        message_lower = message.lower()
        is_asking_about_analysis = any(keyword in message_lower for keyword in analysis_keywords)
        
        # Only add context if user is actually asking about the analysis
        if is_asking_about_analysis and context_results:
            context_block = self._build_analysis_context(context_results)
            full_prompt = f"{context_block}\n\nUser Question: {message}\n\nAnswer the question based on the analysis results above."
            system_prompt = self.create_system_prompt(mode="analysis")
        else:
            # Normal conversation - no analysis context
            full_prompt = message
            system_prompt = self.create_system_prompt(mode="general")
        
        try:
            response = ollama.generate(
                model=self.model_name,
                prompt=full_prompt,
                system=system_prompt,
                options={
                    'temperature': 0.8,  # More creative for general chat
                    'top_p': 0.9,
                    'max_tokens': 400
                }
            )
            
            return response['response']
            
        except Exception as e:
            print(f"❌ Chat Error: {e}")
            return f"I apologize, but I encountered an error: {str(e)}. Please try again."
    
    def ask(self, question, context=None):
        """
        Alias for chat() - for backwards compatibility
        """
        return self.chat(question, context)


# Test
if __name__ == "__main__":
    chatbot = HCISChatbot()
    
    # Mock analysis results
    test_results = {
        'fusion_score': 75.75,
        'verdict': 'AUTHENTIC',
        'video_score': 85.0,
        'audio_score': 60.0,
        'text_score': 80.0,
        'active_modalities': ['video', 'audio', 'text'],
        'fileName': 'test_video.mp4'
    }
    
    print("\n" + "="*60)
    print("TEST 1: Explain analysis results")
    print("="*60)
    explanation = chatbot.explain_results(test_results)
    print(f"\n{explanation}")
    
    print("\n" + "="*60)
    print("TEST 2: Normal conversation (no context)")
    print("="*60)
    response1 = chatbot.chat("Hi, how are you?")
    print(f"\nBot: {response1}")
    
    print("\n" + "="*60)
    print("TEST 3: General question (no context)")
    print("="*60)
    response2 = chatbot.chat("Tell me about Tesla")
    print(f"\nBot: {response2}")
    
    print("\n" + "="*60)
    print("TEST 4: Question about analysis (with context)")
    print("="*60)
    response3 = chatbot.chat("What was the fusion score?", context_results=test_results)
    print(f"\nBot: {response3}")
    
    print("\n" + "="*60)
    print("TEST 5: Question about deepfakes (no context)")
    print("="*60)
    response4 = chatbot.chat("How do deepfakes work?")
    print(f"\nBot: {response4}")