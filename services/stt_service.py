import sys
import logging
import re

try:
    import pyaudio
except ImportError:
    try:
        import pyaudiowpatch as pyaudio
        sys.modules['pyaudio'] = pyaudio
    except ImportError:
        pyaudio = None

import speech_recognition as sr

class STTEngine:
    def __init__(self):
        self.logger = logging.getLogger("STTEngine")
        self.recognizer = sr.Recognizer()
        # Enable dynamic energy threshold to adapt to ambient noise levels automatically
        self.recognizer.dynamic_energy_threshold = True

    def listen_and_transcribe(self, timeout=5, phrase_time_limit=8, calibrate=True):
        """Captures audio from the default microphone and transcribes it using Google Web Speech.
        This call is blocking and should be run inside a background thread."""
        try:
            with sr.Microphone() as source:
                # Calibrate background noise level before listening
                if calibrate:
                    self.recognizer.adjust_for_ambient_noise(source, duration=1.0)
                audio = self.recognizer.listen(source, timeout=timeout, phrase_time_limit=phrase_time_limit)
            
            # Request translation from Google Speech Service
            text = self.recognizer.recognize_google(audio)
            return True, text.strip()
        except sr.WaitTimeoutError:
            return False, "Listening timed out. No speech was detected."
        except sr.UnknownValueError:
            return False, "Speech was not recognized. Please speak clearly."
        except sr.RequestError as e:
            return False, f"API service request error: Check internet connection. Details: {e}"
        except AttributeError as e:
            # Often raised if PyAudio is missing
            self.logger.error(f"Microphone dependency error: {e}")
            return False, "Microphone interface unavailable. Ensure PyAudio is installed."
        except Exception as e:
            self.logger.error(f"Error during audio transcription: {e}")
            return False, f"Speech interface failure: {str(e)}"

    def check_wake_word(self, transcription, wake_word="hey assistant"):
        """Checks if the wake word is present in the transcription.
        If yes, extracts any command text that follows it.
        Returns (is_match, command)."""
        if not transcription:
            return False, ""
            
        # Clean transcription
        trans = transcription.lower().strip()
        # Remove common punctuation
        trans = trans.replace(",", "").replace(".", "").replace("?", "").replace("!", "")
        
        # Match "assistant" with an optional preceding greeting (hey, hi, hello, ok, okay) anywhere in text
        pattern = r"\b(?:hey|hi|hello|ok|okay)?\s*assistant\b"
        match = re.search(pattern, trans)
        
        if match:
            # Extract everything after the matched wake word
            command = trans[match.end():].strip()
            # Remove leading filler words like "please", "could you", "can you", "to"
            command = re.sub(r'^(?:please|could you|can you|to)\s+', '', command)
            return True, command.strip()
            
        return False, ""
