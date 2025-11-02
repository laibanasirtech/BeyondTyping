# BeyondTyping

BeyondTyping is a voice-controlled assistant designed to improve accessibility for users with physical disabilities or visual impairments. It enables users to interact with a computer using voice commands, performing tasks like opening files, writing documents, browsing folders, and reading content on the screen.

## Features

- **Voice Recognition**: Understands and interprets user voice commands using offline speech recognition
- **Text-to-Speech**: Reads content on screen or documents aloud with customizable settings
- **File Operations**: Open, create, edit, and save documents via voice commands
- **Folder Navigation**: Navigate directories and launch applications via voice
- **Screen Reading**: Reads visible content on the screen using OCR
- **Emoji and Unicode Support**: Full support for reading documents with emojis and special characters
- **Customizable Voice Output**: Adjustable speed, volume, and language settings
- **Command Logging**: Comprehensive logging of commands and actions for debugging

## Project Structure

```
BeyondTyping/
│
├── core/                  # Core modules and helpers
│   ├── __init__.py
│   ├── voice_recognition.py   # Voice recognition using Vosk
│   ├── text_to_speech.py      # Text-to-speech using pyttsx3
│   ├── file_operations.py     # File and folder operations
│   ├── screen_reader.py       # OCR-based screen reading
│   └── command_processor.py   # Command interpretation and execution
│
├── assets/                # Images, icons, sample documents (optional)
├── docs/                  # Project documentation, diagrams (optional)
├── main.py                # Entry point of the application
├── requirements.txt       # Python dependencies
├── README.md              # This file
└── beyondtyping.log       # Application logs (generated at runtime)
```

## Prerequisites

### Required Software

1. **Python 3.8 or higher**
   - Download from [python.org](https://www.python.org/downloads/)

2. **Vosk Speech Recognition Model**
   - Download a model from [Vosk Models](https://alphacephei.com/vosk/models)
   - Recommended: `vosk-model-en-us-0.22` for English
   - Extract and place in project root as `model/` folder
   - Or specify path during initialization

3. **Tesseract OCR** (for screen reading feature)
   - Windows: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
   - Install and ensure it's in your PATH
   - Or set `TESSDATA_PREFIX` environment variable

### System Requirements

- Windows 10/11 (initial version, can be extended to other platforms)
- Microphone for voice input
- Speakers/headphones for audio output

## Installation

### 1. Clone the Repository

```bash
git clone https://github.com/laibanasirtech/BeyondTyping.git
cd BeyondTyping
```

### 2. Install Python Dependencies

```bash
pip install -r requirements.txt
```

**Note for Windows users:**
- If `pyaudio` installation fails, you may need to install it manually:
  ```bash
  pip install pipwin
  pipwin install pyaudio
  ```
- Or download the appropriate wheel from [here](https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio)

### 3. Download Vosk Model

1. Download a Vosk model (e.g., `vosk-model-en-us-0.22`):
   ```bash
   # Option 1: Download manually from https://alphacephei.com/vosk/models
   # Extract to project root as 'model' folder
   
   # Option 2: Use wget/curl (if available)
   wget https://alphacephei.com/vosk/models/vosk-model-en-us-0.22.zip
   unzip vosk-model-en-us-0.22.zip
   mv vosk-model-en-us-0.22 model
   ```

2. Verify the model is in place:
   ```
   BeyondTyping/
   └── model/
       ├── am/
       ├── graph/
       └── ...
   ```

## Usage

### Starting the Application

```bash
python main.py
```

The application will:
1. Initialize all components
2. Greet you with a voice message
3. Start listening for voice commands

### Voice Commands

The assistant recognizes various voice commands. Speak naturally and clearly.

#### Folder Navigation
- **"Open Documents folder"** - Navigate to Documents directory
- **"Open Desktop folder"** - Navigate to Desktop
- **"Go to Downloads"** - Navigate to Downloads folder
- **"Navigate to [folder name]"** - Navigate to specified folder

#### File Operations
- **"Open file [filename]"** - Open a file with default application
- **"Create new file [filename]"** - Create a new file
- **"Read file [filename]"** - Read content of a file
- **"Save file as [filename]"** - Save current document (with content)

#### Directory Listing
- **"List directory"** - Show contents of current directory
- **"List files in [folder]"** - List contents of specified folder
- **"What files are in [folder]"** - Show directory contents

#### Screen Reading
- **"Read screen"** - Read text visible on screen using OCR
- **"What does the screen say"** - Extract and read screen content

#### Folder Creation
- **"Create folder [name]"** - Create a new folder
- **"New folder [name]"** - Create a new folder

#### Exiting
- **"Exit"** or **"Quit"** or **"Goodbye"** - Exit the application

### Example Session

```
You: "Open Documents folder"
Assistant: "Opened Documents folder"

You: "List directory"
Assistant: "Contents: file1.txt, file2.docx, folder1, folder2"

You: "Create new file notes.txt"
Assistant: "Created file notes.txt"

You: "Read screen"
Assistant: [Reads text visible on screen]

You: "Exit"
Assistant: "Goodbye! Thank you for using Beyond Typing."
```

## Configuration

### Adjusting Voice Settings

You can customize the text-to-speech settings by editing `main.py`:

```python
# In BeyondTyping.__init__()
self.tts = TextToSpeech(
    rate=150,      # Speech rate (words per minute, typical: 50-300)
    volume=0.8,    # Volume level (0.0 to 1.0)
    voice_id=None  # Specific voice ID (None for default)
)
```

### Changing Vosk Model Path

If your Vosk model is in a different location:

```python
# In main.py
self.voice_recognizer = VoiceRecognizer(model_path="path/to/your/model")
```

### Logging

Logs are written to `beyondtyping.log` and also printed to console. Adjust logging level in `main.py`:

```python
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more details
    ...
)
```

## Troubleshooting

### Voice Recognition Not Working

1. **Check microphone**: Ensure microphone is connected and working
2. **Check Vosk model**: Verify model is downloaded and in correct location
3. **Test audio**: Try recording audio with another application
4. **Check logs**: Review `beyondtyping.log` for error messages

### PyAudio Installation Issues (Windows)

```bash
# Try using pipwin
pip install pipwin
pipwin install pyaudio

# Or download wheel file manually
# Visit: https://www.lfd.uci.edu/~gohlke/pythonlibs/#pyaudio
# Download appropriate wheel for your Python version
pip install PyAudio-*.whl
```

### Tesseract OCR Not Found

1. **Install Tesseract**: Download from [UB-Mannheim Tesseract](https://github.com/UB-Mannheim/tesseract/wiki)
2. **Add to PATH**: Add Tesseract installation directory to system PATH
3. **Set environment variable** (alternative):
   ```bash
   set TESSDATA_PREFIX=C:\Program Files\Tesseract-OCR\tessdata
   ```

### Command Not Recognized

- Speak clearly and at a moderate pace
- Reduce background noise
- Check command syntax matches examples
- Review logs for recognition results
- Try rephrasing the command

## Development

### Adding New Commands

To add new voice commands, edit `core/command_processor.py`:

1. Add pattern to `self.commands` dictionary
2. Implement handler method (e.g., `_my_new_command()`)
3. Add execution case in `_execute_command()`

Example:

```python
# In __init__()
self.commands = {
    'my_command': [
        r'my\s+command\s+(.+?)',
    ],
    # ... existing commands
}

# Add handler method
def _my_command(self, args):
    # Implementation
    return True, "Command executed"
```

### Running Tests

Currently, manual testing is recommended. Future versions may include automated tests.

## Technical Details

### Dependencies

- **vosk**: Offline speech recognition
- **pyttsx3**: Cross-platform text-to-speech
- **pyaudio**: Audio input handling
- **pytesseract**: Python wrapper for Tesseract OCR
- **Pillow**: Image processing for screen capture
- **pynput**: Keyboard/mouse input handling

### Architecture

The application follows a modular architecture:

1. **Voice Recognition Module**: Captures and transcribes speech
2. **Command Processor**: Interprets commands and routes to appropriate handlers
3. **File Operations**: Handles file and folder operations
4. **Screen Reader**: Performs OCR on screen captures
5. **Text-to-Speech**: Converts responses to speech
6. **Main Application**: Coordinates all modules

## Future Enhancements

- [ ] GUI interface using tkinter/PyQt
- [ ] Support for multiple languages
- [ ] Voice command customization
- [ ] Application launching via voice
- [ ] Enhanced error handling and recovery
- [ ] Mobile platform support (Android/iOS)
- [ ] Cloud-based speech recognition option
- [ ] Integration with accessibility tools

## Contributing

Contributions are welcome! Please:

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Submit a pull request

## License

This project is developed as part of a Final Year Project (FYP). Please refer to your institution's guidelines for licensing.

## Author

Developed as part of Final Year Project (FYP)

## Support

For issues, questions, or suggestions:
- Check the troubleshooting section
- Review logs in `beyondtyping.log`
- Open an issue on GitHub

## Acknowledgments

- Vosk team for offline speech recognition
- Tesseract OCR for screen reading capabilities
- Python community for excellent libraries

---

**Note**: This application is designed for accessibility and educational purposes. Ensure proper permissions and security practices when deploying in production environments.
