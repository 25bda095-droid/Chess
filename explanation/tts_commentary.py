import os

# A prompt template for generating explanations in Hindi.
HINDI_COMMENTARY_PROMPT = """
आप एक चेस ग्रैंडमास्टर कमेंटर हैं। कृपया निम्नलिखित चेस चाल का स्पष्ट और ज्ञानवर्धक स्पष्टीकरण दें।
आपका स्पष्टीकरण पूरी तरह से हिंदी में होना चाहिए। (You are a chess grandmaster commentator. Please provide a clear and insightful explanation of the following chess move. Your explanation must be completely in Hindi.)

Move: {move}
Board State (FEN): {fen}
Context/History: {context}

हिंदी स्पष्टीकरण (Hindi Explanation):
"""

try:
    from gtts import gTTS
    GTTS_AVAILABLE = True
except ImportError:
    GTTS_AVAILABLE = False

class TTSCommentator:
    """
    A class that handles Text-to-Speech (TTS) integration for chess commentary.
    If gTTS is installed, it uses it for basic TTS generation.
    Otherwise, it falls back to a mock implementation.
    """

    def __init__(self, default_lang: str = 'hi'):
        self.default_lang = default_lang

    def generate_prompt(self, move: str, fen: str, context: str) -> str:
        """
        Generates the LLM prompt for Hindi commentary.
        """
        return HINDI_COMMENTARY_PROMPT.format(move=move, fen=fen, context=context)

    def speak(self, text: str, lang: str = None, output_file: str = "commentary.mp3", play: bool = False):
        """
        Converts the given text explanation to speech.
        """
        language = lang or self.default_lang

        if GTTS_AVAILABLE:
            print(f"[TTS] Generating audio in language '{language}'...")
            try:
                tts = gTTS(text=text, lang=language, slow=False)
                tts.save(output_file)
                print(f"[TTS] Audio saved successfully to {output_file}")
                
                if play:
                    print(f"[TTS] Playing audio: {output_file}")
                    # Basic cross-platform play command (mpg321/afplay/start)
                    if os.name == 'nt':
                        os.system(f"start {output_file}")
                    else:
                        os.system(f"mpg321 {output_file} >/dev/null 2>&1 || afplay {output_file} >/dev/null 2>&1 || echo 'Please install mpg321 to play audio.'")
            except Exception as e:
                print(f"[TTS ERROR] Failed to generate or save TTS: {e}")
        else:
            print(f"[MOCK TTS] (gTTS not installed. Run 'pip install gTTS' to enable real TTS)")
            print(f"[MOCK TTS] Language: {language}")
            print(f"[MOCK TTS] Speaking Text: {text}")
            print(f"[MOCK TTS] Audio would be saved to: {output_file}")

# Example usage:
if __name__ == "__main__":
    commentator = TTSCommentator()
    
    # Mock LLM generation
    mock_move = "e4"
    mock_fen = "rnbqkbnr/pppppppp/8/8/4P3/8/PPPP1PPP/RNBQKBNR b KQkq e3 0 1"
    mock_context = "Opening move."
    
    print("--- Prompt Generated ---")
    prompt = commentator.generate_prompt(mock_move, mock_fen, mock_context)
    print(prompt)
    
    print("\n--- Running TTS ---")
    mock_explanation = "ई फोर (e4) एक बहुत ही मजबूत और लोकप्रिय ओपनिंग चाल है। यह केंद्र पर नियंत्रण स्थापित करता है।"
    commentator.speak(mock_explanation, play=False)
