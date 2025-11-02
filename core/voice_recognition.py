"""
Voice Recognition Module
Handles offline speech recognition using Vosk
"""
import json
import pyaudio
from vosk import Model, KaldiRecognizer
import os
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class VoiceRecognizer:
    """Offline voice recognition using Vosk"""
    
    def __init__(self, model_path=None):
        """
        Initialize voice recognizer
        
        Args:
            model_path: Path to Vosk model directory. If None, looks for 'model' in project root
        """
        self.model_path = model_path or self._find_model_path()
        self.model = None
        self.recognizer = None
        self.is_listening = False
        
        if self.model_path and os.path.exists(self.model_path):
            try:
                self.model = Model(self.model_path)
                self.recognizer = KaldiRecognizer(self.model, 16000)
                logger.info(f"Voice recognition model loaded from {self.model_path}")
            except Exception as e:
                logger.error(f"Failed to load voice model: {e}")
                self.model = None
        else:
            logger.warning("Vosk model not found. Please download a model from https://alphacephei.com/vosk/models")
    
    def _find_model_path(self):
        """Try to find Vosk model in common locations"""
        possible_paths = [
            os.path.join(os.getcwd(), "model"),
            os.path.join(os.path.dirname(os.path.dirname(__file__)), "model"),
            os.path.expanduser("~/vosk-model-en-us-0.22"),
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                return path
        return None
    
    def listen(self, timeout=None):
        """
        Listen for voice input and return recognized text
        
        Args:
            timeout: Maximum time to listen in seconds (None for no timeout)
            
        Returns:
            str: Recognized text or None if error/timeout
        """
        if not self.model:
            logger.error("Voice model not loaded")
            return None
        
        try:
            p = pyaudio.PyAudio()
            stream = p.open(format=pyaudio.paInt16,
                          channels=1,
                          rate=16000,
                          input=True,
                          frames_per_buffer=4000)
            stream.start_stream()
            
            logger.info("Listening... (say something)")
            self.is_listening = True
            
            # Read audio data
            while self.is_listening:
                data = stream.read(4000, exception_on_overflow=False)
                
                if self.recognizer.AcceptWaveform(data):
                    result = json.loads(self.recognizer.Result())
                    if result.get('text'):
                        text = result['text'].strip()
                        stream.stop_stream()
                        stream.close()
                        p.terminate()
                        self.is_listening = False
                        logger.info(f"Recognized: {text}")
                        return text
                else:
                    partial = json.loads(self.recognizer.PartialResult())
                    if partial.get('partial'):
                        logger.debug(f"Partial: {partial['partial']}")
            
            # Get final result
            final_result = json.loads(self.recognizer.FinalResult())
            stream.stop_stream()
            stream.close()
            p.terminate()
            self.is_listening = False
            
            if final_result.get('text'):
                text = final_result['text'].strip()
                logger.info(f"Recognized: {text}")
                return text
            
            return None
            
        except Exception as e:
            logger.error(f"Error during voice recognition: {e}")
            self.is_listening = False
            return None
    
    def stop_listening(self):
        """Stop listening for voice input"""
        self.is_listening = False
    
    def is_ready(self):
        """Check if recognizer is ready to use"""
        return self.model is not None and self.recognizer is not None

