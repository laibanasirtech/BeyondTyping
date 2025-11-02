"""
Command Processor Module
Processes and executes voice commands
"""
import os
import re
import logging
from core.file_operations import FileOperations
from core.screen_reader import ScreenReader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class CommandProcessor:
    """Processes voice commands and executes corresponding actions"""
    
    def __init__(self, file_ops=None, screen_reader=None):
        """
        Initialize command processor
        
        Args:
            file_ops: FileOperations instance
            screen_reader: ScreenReader instance
        """
        self.file_ops = file_ops or FileOperations()
        self.screen_reader = screen_reader or ScreenReader()
        
        # Command patterns
        self.commands = {
            'open_folder': [
                r'open\s+(?:the\s+)?(.+?)\s+folder',
                r'navigate\s+to\s+(?:the\s+)?(.+?)',
                r'go\s+to\s+(?:the\s+)?(.+?)',
            ],
            'open_file': [
                r'open\s+(?:the\s+)?file\s+(.+?)',
                r'open\s+(.+?\.\w+)',
            ],
            'create_file': [
                r'create\s+(?:a\s+)?(?:new\s+)?file\s+(?:called\s+)?(.+?)',
                r'new\s+file\s+(.+?)',
            ],
            'read_file': [
                r'read\s+(?:the\s+)?(?:current\s+)?(?:document|file)\s+(.+?)',
                r'read\s+(.+?\.\w+)',
            ],
            'read_current': [
                r'read\s+(?:the\s+)?current\s+(?:document|file)',
                r'read\s+(?:this\s+)?(?:document|file)',
            ],
            'save_file': [
                r'save\s+(?:the\s+)?(?:current\s+)?(?:document|file)\s+as\s+(.+?)',
                r'save\s+as\s+(.+?)',
            ],
            'read_screen': [
                r'read\s+(?:the\s+)?screen',
                r'read\s+(?:what|is)\s+(?:on|in)\s+(?:the\s+)?screen',
                r'what\s+does\s+(?:the\s+)?screen\s+say',
            ],
            'list_directory': [
                r'list\s+(?:the\s+)?(?:contents|files|items)?\s*(?:of\s+)?(.+?)?',
                r'show\s+(?:me\s+)?(?:the\s+)?(?:files|contents)?\s*(?:in\s+)?(.+?)?',
                r'what\s+(?:files|items)\s+(?:are\s+)?(?:in|in\s+the)?\s*(.+?)?',
            ],
            'create_folder': [
                r'create\s+(?:a\s+)?(?:new\s+)?folder\s+(?:called\s+)?(.+?)',
                r'new\s+folder\s+(.+?)',
            ],
        }
        
        # Special folder mappings
        self.folder_mappings = {
            'documents': os.path.expanduser('~/Documents'),
            'desktop': os.path.expanduser('~/Desktop'),
            'downloads': os.path.expanduser('~/Downloads'),
            'pictures': os.path.expanduser('~/Pictures'),
            'music': os.path.expanduser('~/Music'),
            'videos': os.path.expanduser('~/Videos'),
        }
    
    def process_command(self, command_text):
        """
        Process a voice command and execute corresponding action
        
        Args:
            command_text: Text from voice recognition
            
        Returns:
            tuple: (success: bool, response: str)
        """
        if not command_text:
            return False, "No command received"
        
        command_text = command_text.lower().strip()
        logger.info(f"Processing command: {command_text}")
        
        # Try to match command patterns
        for command_type, patterns in self.commands.items():
            for pattern in patterns:
                match = re.search(pattern, command_text)
                if match:
                    try:
                        return self._execute_command(command_type, match, command_text)
                    except Exception as e:
                        logger.error(f"Error executing command: {e}")
                        return False, f"Error: {str(e)}"
        
        # No match found
        return False, "I didn't understand that command. Please try again."
    
    def _execute_command(self, command_type, match, full_command):
        """Execute a matched command"""
        groups = match.groups()
        
        if command_type == 'open_folder':
            folder_name = groups[0] if groups else None
            return self._open_folder(folder_name)
        
        elif command_type == 'open_file':
            filename = groups[0] if groups else None
            return self._open_file(filename)
        
        elif command_type == 'create_file':
            filename = groups[0] if groups else None
            return self._create_file(filename)
        
        elif command_type == 'read_file':
            filename = groups[0] if groups else None
            return self._read_file(filename)
        
        elif command_type == 'read_current':
            return self._read_current_file()
        
        elif command_type == 'save_file':
            filename = groups[0] if groups else None
            return self._save_file(filename)
        
        elif command_type == 'read_screen':
            return self._read_screen()
        
        elif command_type == 'list_directory':
            folder_name = groups[0] if groups and groups[0] else None
            return self._list_directory(folder_name)
        
        elif command_type == 'create_folder':
            folder_name = groups[0] if groups else None
            return self._create_folder(folder_name)
        
        return False, "Command execution failed"
    
    def _open_folder(self, folder_name):
        """Open/navigate to a folder"""
        if not folder_name:
            return False, "Please specify a folder name"
        
        # Check folder mappings
        folder_name_lower = folder_name.lower().strip()
        if folder_name_lower in self.folder_mappings:
            path = self.folder_mappings[folder_name_lower]
        else:
            path = folder_name
        
        if self.file_ops.navigate_to(path):
            return True, f"Opened {folder_name} folder"
        else:
            return False, f"Could not open {folder_name} folder"
    
    def _open_file(self, filename):
        """Open a file"""
        if not filename:
            return False, "Please specify a file name"
        
        if self.file_ops.open_file(filename):
            return True, f"Opened {filename}"
        else:
            return False, f"Could not open {filename}"
    
    def _create_file(self, filename):
        """Create a new file"""
        if not filename:
            return False, "Please specify a file name"
        
        # Clean filename
        filename = filename.strip().strip('"').strip("'")
        
        if self.file_ops.create_file(filename):
            return True, f"Created file {filename}"
        else:
            return False, f"Could not create {filename}"
    
    def _read_file(self, filename):
        """Read a file"""
        if not filename:
            return False, "Please specify a file name"
        
        content = self.file_ops.read_file(filename)
        if content is not None:
            return True, content[:500]  # Limit response length
        else:
            return False, f"Could not read {filename}"
    
    def _read_current_file(self):
        """Read current document (placeholder - needs context)"""
        return False, "Please specify which file to read"
    
    def _save_file(self, filename):
        """Save current file (placeholder - needs content context)"""
        if not filename:
            return False, "Please specify a file name"
        
        filename = filename.strip().strip('"').strip("'")
        return False, f"Save functionality requires file content. Please use 'write file {filename}' with content."
    
    def _read_screen(self):
        """Read content from screen"""
        text = self.screen_reader.read_screen()
        if text:
            return True, text[:500]  # Limit response length
        else:
            return False, "Could not read screen content"
    
    def _list_directory(self, folder_name):
        """List directory contents"""
        items = self.file_ops.list_directory(folder_name) if folder_name else self.file_ops.list_directory()
        
        if items:
            items_str = ", ".join(items[:20])  # Limit to 20 items
            if len(items) > 20:
                items_str += f" and {len(items) - 20} more"
            return True, f"Contents: {items_str}"
        else:
            return False, "Directory is empty or not found"
    
    def _create_folder(self, folder_name):
        """Create a new folder"""
        if not folder_name:
            return False, "Please specify a folder name"
        
        folder_name = folder_name.strip().strip('"').strip("'")
        
        if self.file_ops.create_folder(folder_name):
            return True, f"Created folder {folder_name}"
        else:
            return False, f"Could not create {folder_name}"

