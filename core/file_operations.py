"""
File Operations Module
Handles file and folder operations
"""
import os
import shutil
import logging
from pathlib import Path
from datetime import datetime

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class FileOperations:
    """File and folder operations handler"""
    
    def __init__(self, base_path=None):
        """
        Initialize file operations
        
        Args:
            base_path: Base directory for operations (None uses current working directory)
        """
        self.base_path = base_path or os.getcwd()
        self.current_path = self.base_path
        
        # Ensure base path exists
        os.makedirs(self.base_path, exist_ok=True)
        logger.info(f"File operations initialized with base path: {self.base_path}")
    
    def get_current_path(self):
        """Get current working directory"""
        return self.current_path
    
    def navigate_to(self, path):
        """
        Navigate to a directory
        
        Args:
            path: Directory path (relative or absolute)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            # Handle relative paths
            if not os.path.isabs(path):
                path = os.path.join(self.current_path, path)
            
            # Normalize path
            path = os.path.normpath(path)
            
            if os.path.exists(path) and os.path.isdir(path):
                self.current_path = path
                logger.info(f"Navigated to: {self.current_path}")
                return True
            else:
                logger.warning(f"Path does not exist or is not a directory: {path}")
                return False
        except Exception as e:
            logger.error(f"Error navigating to path: {e}")
            return False
    
    def list_directory(self, path=None):
        """
        List contents of a directory
        
        Args:
            path: Directory path (None uses current path)
            
        Returns:
            list: List of file and directory names
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            target_path = os.path.normpath(target_path)
            
            if os.path.exists(target_path) and os.path.isdir(target_path):
                items = os.listdir(target_path)
                logger.info(f"Listed {len(items)} items from {target_path}")
                return items
            else:
                logger.warning(f"Path does not exist: {target_path}")
                return []
        except Exception as e:
            logger.error(f"Error listing directory: {e}")
            return []
    
    def open_file(self, filename, path=None):
        """
        Open a file with default application
        
        Args:
            filename: Name of file to open
            path: Directory path (None uses current path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            file_path = os.path.join(target_path, filename)
            file_path = os.path.normpath(file_path)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.startfile(file_path)
                logger.info(f"Opened file: {file_path}")
                return True
            else:
                logger.warning(f"File does not exist: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error opening file: {e}")
            return False
    
    def create_file(self, filename, content="", path=None):
        """
        Create a new file
        
        Args:
            filename: Name of file to create
            content: Initial content for the file
            path: Directory path (None uses current path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            file_path = os.path.join(target_path, filename)
            file_path = os.path.normpath(file_path)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Created file: {file_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating file: {e}")
            return False
    
    def read_file(self, filename, path=None):
        """
        Read content from a file
        
        Args:
            filename: Name of file to read
            path: Directory path (None uses current path)
            
        Returns:
            str: File content or None if error
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            file_path = os.path.join(target_path, filename)
            file_path = os.path.normpath(file_path)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                with open(file_path, 'r', encoding='utf-8') as f:
                    content = f.read()
                logger.info(f"Read file: {file_path} ({len(content)} chars)")
                return content
            else:
                logger.warning(f"File does not exist: {file_path}")
                return None
        except Exception as e:
            logger.error(f"Error reading file: {e}")
            return None
    
    def write_file(self, filename, content, path=None, append=False):
        """
        Write content to a file
        
        Args:
            filename: Name of file to write
            content: Content to write
            path: Directory path (None uses current path)
            append: If True, append to file; otherwise overwrite
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            file_path = os.path.join(target_path, filename)
            file_path = os.path.normpath(file_path)
            
            mode = 'a' if append else 'w'
            with open(file_path, mode, encoding='utf-8') as f:
                f.write(content)
            
            logger.info(f"Wrote to file: {file_path} ({len(content)} chars)")
            return True
        except Exception as e:
            logger.error(f"Error writing file: {e}")
            return False
    
    def save_as(self, filename, content, path=None):
        """
        Save content to a file (alias for write_file)
        
        Args:
            filename: Name of file to save
            content: Content to save
            path: Directory path (None uses current path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        return self.write_file(filename, content, path, append=False)
    
    def delete_file(self, filename, path=None):
        """
        Delete a file
        
        Args:
            filename: Name of file to delete
            path: Directory path (None uses current path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            file_path = os.path.join(target_path, filename)
            file_path = os.path.normpath(file_path)
            
            if os.path.exists(file_path) and os.path.isfile(file_path):
                os.remove(file_path)
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File does not exist: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Error deleting file: {e}")
            return False
    
    def create_folder(self, folder_name, path=None):
        """
        Create a new folder
        
        Args:
            folder_name: Name of folder to create
            path: Parent directory path (None uses current path)
            
        Returns:
            bool: True if successful, False otherwise
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            folder_path = os.path.join(target_path, folder_name)
            folder_path = os.path.normpath(folder_path)
            
            os.makedirs(folder_path, exist_ok=True)
            logger.info(f"Created folder: {folder_path}")
            return True
        except Exception as e:
            logger.error(f"Error creating folder: {e}")
            return False
    
    def get_file_info(self, filename, path=None):
        """
        Get information about a file
        
        Args:
            filename: Name of file
            path: Directory path (None uses current path)
            
        Returns:
            dict: File information or None if error
        """
        try:
            target_path = path or self.current_path
            if not os.path.isabs(target_path):
                target_path = os.path.join(self.current_path, target_path)
            
            file_path = os.path.join(target_path, filename)
            file_path = os.path.normpath(file_path)
            
            if os.path.exists(file_path):
                stat = os.stat(file_path)
                return {
                    "name": filename,
                    "path": file_path,
                    "size": stat.st_size,
                    "modified": datetime.fromtimestamp(stat.st_mtime).isoformat(),
                    "is_file": os.path.isfile(file_path),
                    "is_dir": os.path.isdir(file_path)
                }
            else:
                return None
        except Exception as e:
            logger.error(f"Error getting file info: {e}")
            return None

