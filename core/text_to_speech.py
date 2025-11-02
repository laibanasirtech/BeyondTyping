"""
Text-to-Speech Module
Handles text-to-speech conversion using pyttsx3
"""
import pyttsx3
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class TextToSpeech:
    """Text-to-speech engine using pyttsx3"""
    
    def __init__(self, rate=150, volume=0.8, voice_id=None):
        """
        Initialize TTS engine
        
        Args:
            rate: Speech rate (words per minute)
            volume: Volume level (0.0 to 1.0)
            voice_id: Specific voice ID to use (None for default)
        """
        try:
            self.engine = pyttsx3.init()
            self.set_rate(rate)
            self.set_volume(volume)
            
            if voice_id:
                self.set_voice(voice_id)
            
            logger.info("Text-to-speech engine initialized")
        except Exception as e:
            logger.error(f"Failed to initialize TTS engine: {e}")
            self.engine = None
    
    def speak(self, text):
        """
        Speak the given text
        
        Args:
            text: Text to speak
        """
        if not self.engine:
            logger.error("TTS engine not initialized")
            return
        
        try:
            logger.info(f"Speaking: {text[:50]}...")
            self.engine.say(text)
            self.engine.runAndWait()
        except Exception as e:
            logger.error(f"Error during speech: {e}")
    
    def set_rate(self, rate):
        """
        Set speech rate
        
        Args:
            rate: Words per minute (typically 50-300)
        """
        if self.engine:
            try:
                self.engine.setProperty('rate', rate)
                logger.info(f"Speech rate set to {rate} WPM")
            except Exception as e:
                logger.error(f"Error setting rate: {e}")
    
    def set_volume(self, volume):
        """
        Set volume level
        
        Args:
            volume: Volume level (0.0 to 1.0)
        """
        if self.engine:
            try:
                self.engine.setProperty('volume', max(0.0, min(1.0, volume)))
                logger.info(f"Volume set to {volume}")
            except Exception as e:
                logger.error(f"Error setting volume: {e}")
    
    def set_voice(self, voice_id):
        """
        Set voice by ID
        
        Args:
            voice_id: Voice ID from available voices
        """
        if self.engine:
            try:
                voices = self.engine.getProperty('voices')
                if voices and voice_id < len(voices):
                    self.engine.setProperty('voice', voices[voice_id].id)
                    logger.info(f"Voice set to: {voices[voice_id].name}")
            except Exception as e:
                logger.error(f"Error setting voice: {e}")
    
    def get_available_voices(self):
        """
        Get list of available voices
        
        Returns:
            list: List of voice information dictionaries
        """
        if not self.engine:
            return []
        
        try:
            voices = self.engine.getProperty('voices')
            return [{"id": i, "name": v.name, "languages": getattr(v, 'languages', [])} 
                   for i, v in enumerate(voices)]
        except Exception as e:
            logger.error(f"Error getting voices: {e}")
            return []
    
    def save_to_file(self, text, filename):
        """
        Save speech to audio file
        
        Args:
            text: Text to convert
            filename: Output audio filename
        """
        if not self.engine:
            logger.error("TTS engine not initialized")
            return False
        
        try:
            self.engine.save_to_file(text, filename)
            self.engine.runAndWait()
            logger.info(f"Speech saved to {filename}")
            return True
        except Exception as e:
            logger.error(f"Error saving speech to file: {e}")
            return False

