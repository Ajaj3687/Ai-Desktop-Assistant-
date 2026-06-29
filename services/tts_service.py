import pyttsx3
import logging

class TTSEngine:
    def __init__(self, rate=180, volume=1.0, gender="female"):
        self.logger = logging.getLogger("TTSEngine")
        self.engine = None
        try:
            # Initialize pyttsx3 engine.
            # We initialize it once to prevent memory leaks and threading conflicts.
            self.engine = pyttsx3.init()
            self.configure(rate, volume, gender)
        except Exception as e:
            self.logger.error(f"Failed to initialize pyttsx3 engine: {e}")

    def configure(self, rate=180, volume=1.0, gender="female"):
        """Configures speech properties like rate, volume, and voice gender."""
        if not self.engine:
            return
        
        try:
            self.engine.setProperty('rate', rate)
            self.engine.setProperty('volume', volume)
            
            # Retrieve available system voices
            voices = self.engine.getProperty('voices')
            target_voice = None
            
            # Search for a voice that matches the gender preference
            for voice in voices:
                voice_name = voice.name.lower()
                voice_id = voice.id.lower()
                if gender == "female" and ("female" in voice_name or "zira" in voice_name or "hazel" in voice_name or "heera" in voice_name):
                    target_voice = voice.id
                    break
                elif gender == "male" and ("male" in voice_name or "david" in voice_name or "ravi" in voice_name):
                    target_voice = voice.id
                    break
            
            # Fallback to the first available voice if specific gender isn't found
            if not target_voice and voices:
                target_voice = voices[0].id
                
            if target_voice:
                self.engine.setProperty('voice', target_voice)
        except Exception as e:
            self.logger.error(f"Error configuring TTS engine: {e}")

    def speak(self, text):
        """Vocalizes the given text. This call is blocking, so run it in a background thread."""
        if not self.engine:
            print(f"[Fallback TTS Engine] Speech: {text}")
            return
        
        try:
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            self.logger.error(f"Error during TTS playback: {e}")
            # Attempt to recover by reinitializing
            try:
                self.engine = pyttsx3.init()
            except:
                self.engine = None
