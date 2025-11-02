"""
Screen Reading Module
Handles OCR-based screen reading using pytesseract
"""
import pytesseract
from PIL import Image
import pyautogui
import logging

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Configure pyautogui fail-safe
pyautogui.FAILSAFE = True


class ScreenReader:
    """OCR-based screen reading using pytesseract"""
    
    def __init__(self):
        """Initialize screen reader"""
        try:
            # Test if tesseract is available
            pytesseract.get_tesseract_version()
            logger.info("Screen reader initialized")
        except Exception as e:
            logger.warning(f"Tesseract OCR not found. Please install Tesseract OCR: {e}")
            logger.warning("Download from: https://github.com/UB-Mannheim/tesseract/wiki")
    
    def capture_screen(self, region=None):
        """
        Capture screen or screen region
        
        Args:
            region: Tuple (x, y, width, height) for region, or None for full screen
            
        Returns:
            PIL.Image: Captured screenshot
        """
        try:
            if region:
                x, y, width, height = region
                screenshot = pyautogui.screenshot(region=(x, y, width, height))
            else:
                screenshot = pyautogui.screenshot()
            
            logger.info("Screen captured successfully")
            return screenshot
        except Exception as e:
            logger.error(f"Error capturing screen: {e}")
            return None
    
    def read_screen(self, region=None, lang='eng'):
        """
        Read text from screen using OCR
        
        Args:
            region: Tuple (x, y, width, height) for region, or None for full screen
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            str: Extracted text
        """
        try:
            screenshot = self.capture_screen(region)
            if screenshot:
                # Extract text using OCR
                text = pytesseract.image_to_string(screenshot, lang=lang)
                logger.info(f"Extracted {len(text)} characters from screen")
                return text.strip()
            else:
                return ""
        except Exception as e:
            logger.error(f"Error reading screen: {e}")
            return ""
    
    def read_file_image(self, image_path, lang='eng'):
        """
        Read text from an image file
        
        Args:
            image_path: Path to image file
            lang: Language code for OCR (default: 'eng')
            
        Returns:
            str: Extracted text
        """
        try:
            image = Image.open(image_path)
            text = pytesseract.image_to_string(image, lang=lang)
            logger.info(f"Extracted {len(text)} characters from image: {image_path}")
            return text.strip()
        except Exception as e:
            logger.error(f"Error reading image file: {e}")
            return ""

