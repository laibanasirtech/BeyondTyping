#!/usr/bin/env python3
"""
BeyondTyping MVP - Clean Voice Assistant
========================================
A simplified, working voice assistant with essential features only.
Ready for FYP delivery!
"""

import os
import sys
import time
import threading
import speech_recognition as sr
import pyttsx3
import webbrowser
import subprocess
import pyautogui
from pathlib import Path
from typing import Optional, Tuple

# Optional: Beep sound for better UX (Windows only)
try:
    import winsound
    WINSOUND_AVAILABLE = True
except ImportError:
    WINSOUND_AVAILABLE = False

# Optional imports for enhanced features
try:
    import pywhatkit
    PYWHATKIT_AVAILABLE = True
except ImportError:
    PYWHATKIT_AVAILABLE = False
    print("⚠️  pywhatkit not available - install with: pip install pywhatkit")

# ML Intent Classification (Optional - falls back to static if unavailable)
INTENT_MODEL_AVAILABLE = False
intent_vectorizer = None
intent_model = None

try:
    import pickle
    import os
    if os.path.exists("intent_model.pkl"):
        with open("intent_model.pkl", "rb") as f:
            intent_vectorizer, intent_model = pickle.load(f)
        INTENT_MODEL_AVAILABLE = True
        print("✅ ML Intent Model loaded - Enhanced command understanding enabled!")
    else:
        print("ℹ️  ML Intent Model not found - using static keyword matching")
        print("   To enable ML: Run 'python train_intent_model.py' first")
except Exception as e:
    print(f"⚠️  Could not load ML model: {e}")
    print("   Using static keyword matching (this is fine)")

# ============================================================
# SECTION 1: Initialization & Core Setup
# ============================================================

class BeyondTypingMVP:
    """Clean MVP version of BeyondTyping voice assistant"""
    
    def __init__(self):
        """Initialize the MVP voice assistant"""
        print("🚀 Initializing BeyondTyping MVP...")
        
        # Voice recognition setup
        self.recognizer = sr.Recognizer()
        self.microphone = sr.Microphone()
        
        # Text-to-speech setup
        self.tts_engine = pyttsx3.init()
        self.tts_engine.setProperty('rate', 200)
        self.tts_engine.setProperty('volume', 0.8)
        
        # Adjust for ambient noise
        with self.microphone as source:
            self.recognizer.adjust_for_ambient_noise(source)
        
        self.is_running = False
        
        # File navigation state for blind/disabled users
        self.current_path = Path.home()  # Use Path object for better path handling
        self.current_folder = str(self.current_path)  # Keep string version for compatibility
        self.folder_history = []
        self._file_explorer_open = False  # Track if file explorer is already open
        
        print("✅ BeyondTyping MVP initialized successfully!")
    
    def speak(self, text: str):
        """Convert text to speech"""
        try:
            print(f"🔊 Speaking: {text}")
            self.tts_engine.say(text)
            self.tts_engine.runAndWait()
        except Exception as e:
            print(f"❌ TTS Error: {e}")
    
    def listen(self, timeout: int = 5) -> Optional[str]:
        """Listen for voice input"""
        try:
            print("👂 Listening...")
            # Optional: Beep before recording for better UX
            if WINSOUND_AVAILABLE:
                try:
                    winsound.Beep(1000, 200)  # frequency 1000Hz, duration 200ms
                except:
                    pass  # Fail silently if beep doesn't work
            
            with self.microphone as source:
                audio = self.recognizer.listen(source, timeout=timeout)
            
            print("🎤 Processing speech...")
            text = self.recognizer.recognize_google(audio)
            print(f"✅ Recognized: '{text}'")
            return text.lower()
            
        except sr.WaitTimeoutError:
            print("⏰ Listening timeout")
            return None
        except sr.UnknownValueError:
            print("❌ Could not understand audio")
            return None
        except sr.RequestError as e:
            print(f"❌ Speech recognition error: {e}")
            return None
        except Exception as e:
            print(f"❌ Error in listen: {e}")
            return None
    
    def process_command(self, command: str) -> bool:
        """
        Process voice command using ML INTENT CLASSIFICATION (if available) 
        with STATIC KEYWORD MATCHING fallback
        - ML model provides intelligent intent detection
        - Static matching ensures reliability when ML unavailable
        - Perfect for FYP demonstration
        """
        print(f"🎯 Processing: '{command}'")
        
        # Normalize command to lowercase for consistent matching
        command_lower = command.lower()
        
        # Try ML intent classification first (if available)
        if INTENT_MODEL_AVAILABLE and intent_vectorizer and intent_model:
            try:
                intent = self._get_intent_from_ml(command_lower)
                print(f"🧠 ML Intent detected: {intent}")
                
                # Route based on ML intent
                success = self._route_by_intent(intent, command)
                if success:
                    return True
                # If ML routing fails, fall back to static matching
                print("   → ML routing incomplete, falling back to static matching...")
            except Exception as e:
                print(f"⚠️  ML model error: {e}, using static matching")
        
        # Fallback to enhanced static keyword matching
        return self._process_command_static(command, command_lower)
    
    def _get_intent_from_ml(self, command: str) -> str:
        """Get intent classification from ML model"""
        try:
            X = intent_vectorizer.transform([command])
            intent = intent_model.predict(X)[0]
            return intent
        except Exception as e:
            raise Exception(f"ML prediction failed: {e}")
    
    def _route_by_intent(self, intent: str, original_command: str) -> bool:
        """Route command to appropriate handler based on ML intent"""
        command_lower = original_command.lower()
        
        # YouTube intents
        if intent == "youtube_open":
            return self._open_youtube()
        elif intent == "youtube_control":
            if "play" in command_lower:
                return self._play_video()
            elif "pause" in command_lower:
                return self._pause_video()
            elif "next" in command_lower:
                return self._next_video()
            elif "previous" in command_lower:
                return self._previous_video()
        elif intent == "youtube_search":
            return self._search_youtube(original_command)
        
        # Browser intents
        elif intent == "browser_open":
            if "google" in command_lower:
                return self._open_browser()
            elif "youtube" in command_lower:
                return self._open_youtube()
            elif "website" in command_lower or "open" in command_lower:
                return self._open_website(original_command)
            else:
                return self._open_browser()
        elif intent == "browser_search":
            if "google" in command_lower:
                return self._search_google(original_command)
            else:
                return self._search_google(original_command)
        
        # Tab management
        elif intent == "tab_next":
            return self._next_tab()
        elif intent == "tab_previous":
            return self._previous_tab()
        elif intent == "tab_close":
            return self._close_tab()
        
        # File explorer intents
        elif intent == "file_explorer":
            if "documents" in command_lower:
                return self._navigate_to_folder("go to documents")
            elif "downloads" in command_lower:
                return self._navigate_to_folder("go to downloads")
            elif "pictures" in command_lower:
                return self._navigate_to_folder("go to pictures")
            else:
                return self._open_file_explorer_navigate()
        
        # File operations
        elif intent == "file_create":
            return self._create_file(original_command)
        elif intent == "file_write":
            return self._write_to_file(original_command)
        elif intent == "file_save":
            return self._save_file_enhanced(original_command)
        elif intent == "file_close":
            return self._close_file()
        elif intent == "file_open":
            if "pdf" in command_lower or "document" in command_lower:
                return self._open_file_enhanced(original_command)
            else:
                return self._open_file_enhanced(original_command)
        elif intent == "file_read":
            return self._read_file_aloud(original_command)
        
        # App intents
        elif intent == "app_open":
            if "youtube" in command_lower or "yt" in command_lower:
                return self._open_youtube()
            elif "whatsapp" in command_lower:
                return self._open_whatsapp()
            elif "chrome" in command_lower or "browser" in command_lower:
                return self._open_browser()
            elif "vscode" in command_lower or "vs code" in command_lower:
                return self._open_vscode(original_command)
            elif "word" in command_lower:
                return self._open_word(original_command)
            elif "powerpoint" in command_lower:
                return self._open_powerpoint(original_command)
            elif "camera" in command_lower:
                return self._open_camera()
            else:
                # Default: try to open browser for app_open intent
                return self._open_browser()
        
        # WhatsApp intents
        elif intent == "whatsapp_send":
            return self._whatsapp_send(original_command)
        elif intent == "whatsapp_download":
            return self._whatsapp_download()
        
        # Screen reader
        elif intent == "screen_reader":
            if "clipboard" in command_lower:
                return self._read_clipboard()
            elif "selected" in command_lower:
                return self._read_selected_text()
            else:
                return self._read_screen()
        
        # Utility intents
        elif intent == "utility_time":
            return self._get_time()
        elif intent == "utility_help":
            return self._show_help()
        elif intent == "utility_stop":
            return self._stop()
        elif intent == "utility_chat":
            return self._handle_chat(original_command)
        elif intent == "utility_screenshot":
            return self._take_screenshot()
        elif intent == "utility_window":
            if "minimize" in command_lower:
                return self._minimize_window()
            elif "maximize" in command_lower:
                return self._maximize_window()
        elif intent == "utility_scroll":
            if "down" in command_lower:
                return self._scroll_down()
            elif "up" in command_lower:
                return self._scroll_up()
        
        # System intents
        elif intent == "system_lock":
            return self._lock_system()
        elif intent == "system_unlock":
            return self._unlock_system()
        
        return False
    
    def _process_command_static(self, command: str, command_lower: str) -> bool:
        """Process command using static keyword matching (fallback)"""
        # Helper function to check multiple keyword variations
        def has_any_keyword(keywords):
            return any(keyword in command_lower for keyword in keywords)
        
        # Basic commands - Enhanced with multiple variations
        if has_any_keyword(['open youtube', 'launch youtube', 'start youtube', 'youtube open', 'play youtube', 'go to youtube', 'open yt']):
            return self._open_youtube()
        
        elif has_any_keyword(['open browser', 'open edge', 'launch browser', 'start browser', 'open web browser', 'open chrome', 'browser open']):
            return self._open_browser()
        
        # Enhanced File Navigation Commands (for blind/disabled users)
        elif has_any_keyword(['open file explorer', 'open explorer', 'file explorer', 'show file explorer', 'launch file explorer', 'open files']):
            return self._open_file_explorer_navigate()
        
        elif has_any_keyword(['go to', 'navigate to', 'take me to', 'open', 'show me', 'switch to']) and any(folder in command_lower for folder in ['downloads', 'documents', 'desktop', 'pictures', 'music', 'videos']):
            return self._navigate_to_folder(command)
        
        elif has_any_keyword(['open folder', 'show folder', 'launch folder']):
            return self._open_folder(command)
        
        elif has_any_keyword(['list files', 'list folders', 'show files', 'show folders', 'what files', 'what folders', 'files in', 'folders in', 'read files', 'read folders']):
            return self._list_files_in_folder()
        
        elif has_any_keyword(['open file', 'open document', 'show file', 'launch file', 'open the file']):
            return self._open_file_enhanced(command)
        
        elif has_any_keyword(['open picture', 'open image', 'open photo', 'show picture', 'show image', 'show photo', 'view picture', 'view image']):
            return self._open_picture(command)
        
        elif has_any_keyword(['go back', 'go backwards', 'back folder', 'previous folder', 'return', 'go back to']) and 'folder' in command_lower:
            return self._go_back_folder()
        
        elif has_any_keyword(['where am i', 'where am', 'current location', 'current folder', 'my location', 'what folder', 'which folder']):
            return self._announce_current_location()
        
        # Document Editing Commands
        elif has_any_keyword(['open notepad', 'open editor', 'launch notepad', 'start notepad', 'open text editor', 'notepad open', 'editor open']):
            return self._open_editor()
        
        elif has_any_keyword(['create file', 'create document', 'new file', 'make file', 'new document', 'make document', 'create a file']):
            return self._create_file(command)
        
        elif ('write' in command_lower or 'type' in command_lower) and has_any_keyword(['in file', 'to file', 'in document', 'to document', 'in the file']):
            return self._write_to_file(command)
        
        elif has_any_keyword(['delete text', 'remove text', 'erase text', 'clear text', 'remove the text', 'delete the text']):
            return self._delete_text(command)
        
        elif has_any_keyword(['delete file', 'remove file', 'erase file', 'delete the file', 'remove the file']):
            return self._delete_file(command)
        
        elif has_any_keyword(['save file', 'save document', 'save the file', 'save as']):
            return self._save_file_enhanced(command)
        
        elif has_any_keyword(['save to', 'save in', 'save at']):
            return self._save_file_to_location(command)
        
        elif has_any_keyword(['close file', 'close document', 'close the file', 'exit file', 'quit file']):
            return self._close_file()
        
        # YouTube and Search Commands - Enhanced with better matching
        # Handle any command containing "youtube" - check if it's search or open
        elif 'youtube' in command_lower or 'yt' in command_lower:
            # If it's a search command
            if has_any_keyword(['search', 'find', 'play', 'look for']) or 'search' in command_lower:
                return self._search_youtube(command)
            # Otherwise, open YouTube
            else:
                return self._open_youtube()
        
        # Handle "go to youtube" or "open youtube" explicitly (before search)
        elif has_any_keyword(['go to youtube', 'open youtube', 'launch youtube', 'start youtube', 'youtube open']) and 'search' not in command_lower:
            return self._open_youtube()
        
        elif has_any_keyword(['search google', 'google search', 'search on google', 'google find', 'find on google']):
            return self._search_google(command)
        
        # ============================================================
        # SECTION 5: Video Control & Tab Management
        # ============================================================
        
        # Video Control Commands
        elif has_any_keyword(['play video', 'play the video', 'start video', 'resume video', 'continue video']):
            return self._play_video()
        
        elif has_any_keyword(['pause video', 'pause the video', 'stop video', 'halt video']):
            return self._pause_video()
        
        elif has_any_keyword(['next video', 'next', 'skip video', 'skip', 'next track', 'next song']):
            return self._next_video()
        
        elif has_any_keyword(['previous video', 'previous', 'last video', 'go back video', 'previous track', 'previous song']):
            return self._previous_video()
        
        # Tab Management Commands
        elif has_any_keyword(['next tab', 'switch tab', 'next browser tab', 'switch to next tab', 'change tab']):
            return self._next_tab()
        
        elif has_any_keyword(['previous tab', 'last tab', 'previous browser tab', 'go back tab', 'back tab']):
            return self._previous_tab()
        
        # Website Commands
        elif has_any_keyword(['open website', 'open site', 'go to website', 'go to site', 'visit website', 'visit site', 'open the website']):
            return self._open_website(command)
        
        # WhatsApp Integration (Optional)
        elif has_any_keyword(['open whatsapp', 'whatsapp', 'whatsapp web', 'open whatsapp web']):
            return self._open_whatsapp()
        
        # ============================================================
        # SECTION 6: Utility Commands
        # ============================================================
        
        # Utility Commands
        elif has_any_keyword(['what time is it', 'what time', 'tell me the time', 'current time', 'time please', 'what\'s the time']):
            return self._get_time()
        
        elif has_any_keyword(['help', 'what can you do', 'show help', 'list commands', 'available commands', 'commands', 'capabilities']):
            return self._show_help()
        
        elif has_any_keyword(['stop', 'shutdown', 'exit', 'quit', 'close', 'end', 'terminate']):
            self.speak("Goodbye!")
            self.is_running = False
            return True
        
        else:
            self.speak("Sorry, I didn't catch that. You can say 'help' to know what I can do.")
            return False
    
    # ============================================================
    # SECTION 3: YouTube & Browser Commands
    # ============================================================
    
    def _open_youtube(self) -> bool:
        """Open YouTube - Opens in default browser, reuses existing window if possible"""
        try:
            # Use webbrowser.get() to use default browser and try to reuse window
            browser = webbrowser.get()
            browser.open("https://www.youtube.com", new=0)  # new=0 tries to reuse existing window
            self.speak("Opening YouTube")
            return True
        except Exception as e:
            # Fallback
            try:
                webbrowser.open("https://www.youtube.com")
                self.speak("Opening YouTube")
                return True
            except:
                self.speak(f"Failed to open YouTube: {e}")
                return False
    
    def _open_browser(self) -> bool:
        """Open web browser - Opens in default browser, reuses existing window if possible"""
        try:
            # Use webbrowser.get() to use default browser and try to reuse existing window
            browser = webbrowser.get()
            browser.open('https://google.com', new=0)  # new=0 tries to reuse existing window
            self.speak("Opening browser")
            return True
        except Exception as e:
            # Fallback
            try:
                webbrowser.open('https://google.com')
                self.speak("Opening browser")
                return True
            except:
                self.speak(f"Failed to open browser: {e}")
                return False
    
    def _search_youtube(self, command: str) -> bool:
        """Search and play on YouTube - Enhanced with voice search prompt"""
        try:
            # Extract search query - more comprehensive extraction
            search_term = command.lower()
            
            # Remove all variations of search keywords
            remove_phrases = [
                'search youtube', 'search for', 'youtube search', 'find on youtube',
                'youtube find', 'play on youtube', 'play', 'find', 'show me', 
                'look for', 'youtube', 'search'
            ]
            
            for phrase in remove_phrases:
                search_term = search_term.replace(phrase, '').strip()
            
            # Clean up extra spaces
            search_term = ' '.join(search_term.split())
            
            if not search_term or len(search_term) < 2:
                # Ask user what to search for
                self.speak("What would you like me to search for on YouTube?")
                # Listen for the search query
                time.sleep(1)
                search_query = self.listen(timeout=10)
                if search_query:
                    search_term = search_query
                else:
                    return False
    
            # Try pywhatkit first (plays video directly)
            if PYWHATKIT_AVAILABLE:
                try:
                    pywhatkit.playonyt(search_term)
                    self.speak(f"Playing {search_term} on YouTube")
                    return True
                except Exception as e:
                    print(f"pywhatkit failed: {e}, falling back to web search")
            
            # Fallback to web search - reuse existing window
            url = f"https://www.youtube.com/results?search_query={search_term.replace(' ', '+')}"
            try:
                browser = webbrowser.get()
                browser.open(url, new=0)
            except:
                webbrowser.open(url)
            
            self.speak(f"Searching YouTube for {search_term}")
            return True
            
        except Exception as e:
            self.speak(f"Failed to search YouTube: {e}")
            return False
    
    def _play_video(self) -> bool:
        """Play current video - Enhanced with confirmation"""
        try:
            time.sleep(1)  # Wait for YouTube to be active
            pyautogui.press('space')
            self.speak("Video is now playing")
            return True
        except Exception as e:
            self.speak(f"Failed to play video: {e}")
            return False
    
    def _pause_video(self) -> bool:
        """Pause current video"""
        try:
            pyautogui.press('space')
            self.speak("Video paused")
            return True
        except Exception as e:
            self.speak(f"Failed to pause video: {e}")
            return False
    
    def _next_video(self) -> bool:
        """Next video"""
        try:
            pyautogui.hotkey('shift', 'n')
            self.speak("Next video")
            return True
        except Exception as e:
            self.speak(f"Failed to go to next video: {e}")
            return False
    
    def _previous_video(self) -> bool:
        """Previous video"""
        try:
            pyautogui.hotkey('shift', 'p')
            self.speak("Previous video")
            return True
        except Exception as e:
            self.speak(f"Failed to go to previous video: {e}")
            return False
    
    def _next_tab(self) -> bool:
        """Next browser tab"""
        try:
            pyautogui.hotkey('ctrl', 'tab')
            self.speak("Next tab")
            return True
        except Exception as e:
            self.speak(f"Failed to switch tabs: {e}")
            return False
    
    def _previous_tab(self) -> bool:
        """Previous browser tab"""
        try:
            pyautogui.hotkey('ctrl', 'shift', 'tab')
            self.speak("Previous tab")
            return True
        except Exception as e:
            self.speak(f"Failed to switch tabs: {e}")
            return False
    
    def _open_website(self, command: str) -> bool:
        """Open website"""
        try:
            site_name = command.replace('open website', '').strip()
            if not site_name:
                self.speak("Which website would you like to open?")
                return False
            
            if not site_name.startswith(('http://', 'https://')):
                site_name = f"https://{site_name}.com"
            
            webbrowser.open(site_name)
            self.speak(f"Opening {site_name}")
            return True
        except Exception as e:
            self.speak(f"Failed to open website: {e}")
            return False
    
    def _search_google(self, command: str) -> bool:
        """Search Google"""
        try:
            search_term = command.replace('search google', '').strip()
            if not search_term:
                self.speak("What would you like to search for?")
                return False
            
            url = f"https://www.google.com/search?q={search_term.replace(' ', '+')}"
            webbrowser.open(url)
            self.speak(f"Searching Google for {search_term}")
            return True
        except Exception as e:
            self.speak(f"Failed to search Google: {e}")
            return False
    
    def _open_whatsapp(self) -> bool:
        """Open WhatsApp Web - Optional feature for file downloads"""
        try:
            webbrowser.open("https://web.whatsapp.com")
            self.speak("Opening WhatsApp Web for file download")
            return True
        except Exception as e:
            self.speak(f"Failed to open WhatsApp Web: {e}")
            return False
    
    # ============================================================
    # SECTION 2: File Operations & Navigation
    # ============================================================
    
    def _open_file_explorer_navigate(self) -> bool:
        """Open Windows File Explorer and announce navigation - Enhanced"""
        try:
            # Use subprocess for better control
            if not self._file_explorer_open:
                subprocess.Popen("explorer")
                self._file_explorer_open = True
                time.sleep(1)  # Brief delay to ensure explorer opens
                self.speak("File Explorer opened. Say 'go to downloads', 'go to documents', or 'go to desktop' to navigate.")
            else:
                self.speak("File Explorer is already open. Say 'go to downloads', 'go to documents', or 'go to desktop' to navigate.")
            return True
        except Exception as e:
            self.speak(f"Failed to open File Explorer: {e}")
            return False
    
    def _navigate_to_folder(self, command: str) -> bool:
        """Navigate to a folder by voice command - Enhanced with smart navigation"""
        try:
            # Extract folder name from command
            folder_name = command.lower()
            for phrase in ['go to', 'navigate to', 'take me to', 'open', 'show me', 'switch to']:
                folder_name = folder_name.replace(phrase, '').strip()
            
            if not folder_name:
                self.speak("Which folder would you like to go to?")
                return False
            
            # Enhanced folder mappings using Path
            folders = {
                'desktop': Path.home() / "Desktop",
                'documents': Path.home() / "Documents",
                'downloads': Path.home() / "Downloads",
                'pictures': Path.home() / "Pictures",
                'pics': Path.home() / "Pictures",
                'photos': Path.home() / "Pictures",
                'music': Path.home() / "Music",
                'videos': Path.home() / "Videos",
                'doc': Path.home() / "Documents",
                'download': Path.home() / "Downloads",
            }
            
            folder_name_lower = folder_name.lower()
            
            # Check if it's a common folder
            if folder_name_lower in folders:
                target_path = folders[folder_name_lower]
                
                # Update current path tracking
                self.current_path = target_path
                self.current_folder = str(target_path)
                
                # If file explorer is already open, navigate in same window
                if self._file_explorer_open:
                    try:
                        # Use keyboard navigation in existing window
                        time.sleep(0.3)
                        pyautogui.hotkey('alt', 'd')  # Focus address bar
                        time.sleep(0.2)
                        pyautogui.write(str(target_path), interval=0.05)
                        time.sleep(0.2)
                        pyautogui.press('enter')
                        time.sleep(0.5)
                    except:
                        # Fallback: open new window
                        os.startfile(str(target_path))
                else:
                    # Open new explorer window
                    os.startfile(str(target_path))
                    self._file_explorer_open = True
                
                # Announce folder contents
                if target_path.exists() and target_path.is_dir():
                    file_count, folder_count = self._count_items(str(target_path))
                    announcement = f"Navigated to {folder_name_lower} folder"
                    if file_count > 0 or folder_count > 0:
                        announcement += f". Found {file_count} files and {folder_count} folders"
                    self.speak(announcement)
                else:
                    self.speak(f"Navigated to {folder_name_lower} folder")
                
                return True
            else:
                # Try to find folder in current location or common locations
                return self._find_and_navigate_to_folder(folder_name)
                
        except Exception as e:
            self.speak(f"Failed to navigate to folder: {e}")
            return False
    
    def _change_directory(self, folder_path: str) -> bool:
        """Change to a specific directory and open it - Enhanced"""
        try:
            # Handle both Path objects and strings
            if isinstance(folder_path, Path):
                path_obj = folder_path
            else:
                path_obj = Path(folder_path)
            
            if not path_obj.exists():
                self.speak(f"Folder not found: {path_obj.name}")
                return False
            
            # Save current location to history
            self.folder_history.append(self.current_path)
            
            # Update current path (using Path object)
            self.current_path = path_obj
            self.current_folder = str(path_obj)
            
            # Open in File Explorer
            os.startfile(str(path_obj))
            
            # Announce what's in the folder
            folder_name = path_obj.name
            file_count, folder_count = self._count_items(str(path_obj))
            
            announcement = f"Navigated to {folder_name}. "
            if file_count > 0:
                announcement += f"Found {file_count} file"
                if file_count > 1:
                    announcement += "s"
            if folder_count > 0:
                if file_count > 0:
                    announcement += " and "
                announcement += f"{folder_count} folder"
                if folder_count > 1:
                    announcement += "s"
            
            self.speak(announcement)
            return True
                
        except Exception as e:
            self.speak(f"Failed to change directory: {e}")
            return False
    
    def _find_and_navigate_to_folder(self, folder_name: str) -> bool:
        """Find and navigate to a folder by name"""
        try:
            # Search in current folder first
            if os.path.isdir(self.current_folder):
                for item in os.listdir(self.current_folder):
                    item_path = os.path.join(self.current_folder, item)
                    if os.path.isdir(item_path) and folder_name.lower() in item.lower():
                        return self._change_directory(item_path)
            
            # Search in common locations
            search_locations = [
                os.path.expanduser("~"),
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.path.expanduser("~"), "Desktop"),
            ]
            
            for location in search_locations:
                for root, dirs, files in os.walk(location):
                    for dir_name in dirs:
                        if folder_name.lower() in dir_name.lower():
                            dir_path = os.path.join(root, dir_name)
                            return self._change_directory(dir_path)
            
            self.speak(f"Folder '{folder_name}' not found. Say 'list files' to see available folders.")
            return False
                
        except Exception as e:
            self.speak(f"Error finding folder: {e}")
            return False
    
    def _list_files_in_folder(self) -> bool:
        """List files and folders in current location"""
        try:
            if not os.path.isdir(self.current_folder):
                self.speak("Current location is not a valid folder.")
                return False
            
            items = os.listdir(self.current_folder)
            if not items:
                self.speak("This folder is empty.")
                return True
            
            folders = []
            files = []
            pictures = []
            
            for item in items:
                item_path = os.path.join(self.current_folder, item)
                if os.path.isdir(item_path):
                    folders.append(item)
            else:
                    files.append(item)
                    # Check if it's a picture
                    if item.lower().endswith(('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')):
                        pictures.append(item)
            
            announcement = f"In {os.path.basename(self.current_folder)}: "
            
            if folders:
                announcement += f"{len(folders)} folder"
                if len(folders) > 1:
                    announcement += "s"
                if len(folders) <= 5:
                    announcement += ": " + ", ".join(folders)
                else:
                    announcement += ": " + ", ".join(folders[:5]) + f" and {len(folders) - 5} more"
            
            if files:
                if folders:
                    announcement += ". "
                announcement += f"{len(files)} file"
                if len(files) > 1:
                    announcement += "s"
                if len(files) <= 5:
                    announcement += ": " + ", ".join(files)
                else:
                    announcement += ": " + ", ".join(files[:5]) + f" and {len(files) - 5} more"
            
            if pictures:
                announcement += f". {len(pictures)} picture"
                if len(pictures) > 1:
                    announcement += "s"
                announcement += " found"
            
            self.speak(announcement)
            return True
                
        except Exception as e:
            self.speak(f"Failed to list files: {e}")
            return False
    
    def _count_items(self, folder_path: str) -> Tuple[int, int]:
        """Count files and folders in a directory"""
        try:
            items = os.listdir(folder_path)
            file_count = sum(1 for item in items if os.path.isfile(os.path.join(folder_path, item)))
            folder_count = sum(1 for item in items if os.path.isdir(os.path.join(folder_path, item)))
            return file_count, folder_count
        except:
            return 0, 0
    
    def _open_file_enhanced(self, command: str) -> bool:
        """Enhanced file opening with better filename extraction"""
        try:
            # Extract filename from command - improved extraction
            filename = command.lower()
            
            # Remove common phrases - more comprehensive
            remove_phrases = [
                'open file', 'open document', 'show file', 'launch file', 
                'open the file', 'open', 'file', 'document'
            ]
            for phrase in remove_phrases:
                if filename.startswith(phrase + ' '):
                    filename = filename.replace(phrase + ' ', '', 1).strip()
                elif ' ' + phrase in filename:
                    filename = filename.replace(' ' + phrase, '').strip()
                elif filename.endswith(' ' + phrase):
                    filename = filename.rsplit(' ' + phrase, 1)[0].strip()
            
            # Clean up any leading/trailing whitespace
            filename = filename.strip()
            file_name = filename  # Keep for compatibility
            
            if not file_name or len(file_name) < 2:
                self.speak("Which file would you like to open?")
                # Listen for filename if not provided
                time.sleep(1)
                file_query = self.listen(timeout=10)
                if file_query:
                    file_name = file_query.lower()
                else:
                    return False
            
            # Search in current folder first
            if os.path.isdir(self.current_folder):
                for item in os.listdir(self.current_folder):
                    item_path = os.path.join(self.current_folder, item)
                    if os.path.isfile(item_path) and file_name.lower() in item.lower():
                        os.startfile(item_path)
                        self.speak(f"Opened {item}")
                        return True
            
            # Search in Documents and Desktop
            search_locations = [
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.path.expanduser("~"), "Desktop"),
                self.current_folder
            ]
            
            for location in search_locations:
                if not os.path.isdir(location):
                    continue
                    
                for root, _, files in os.walk(location):
                    for file in files:
                        if file_name.lower() in file.lower():
                            file_path = os.path.join(root, file)
                            os.startfile(file_path)
                            self.speak(f"Opened {file}")
                            return True
            
            self.speak(f"File '{file_name}' not found. Say 'list files' to see available files.")
            return False
            
        except Exception as e:
            self.speak(f"Failed to open file: {e}")
            return False
    
    def _open_picture(self, command: str) -> bool:
        """Open picture/image file"""
        try:
            # Extract picture name from command
            pic_name = command.replace('open picture', '').replace('open image', '').replace('open photo', '').strip()
            
            # Image extensions
            image_extensions = ('.jpg', '.jpeg', '.png', '.gif', '.bmp', '.webp')
            
            # If no specific name, open first picture in current folder
            if not pic_name:
                if os.path.isdir(self.current_folder):
                    for item in os.listdir(self.current_folder):
                        item_path = os.path.join(self.current_folder, item)
                        if os.path.isfile(item_path) and item.lower().endswith(image_extensions):
                            os.startfile(item_path)
                            self.speak(f"Opened picture {item}")
                            return True
                
                self.speak("No pictures found in current folder. Say 'go to pictures' to navigate to pictures folder.")
                return False
            
            # Search for specific picture
            search_locations = [
                self.current_folder,
                os.path.join(os.path.expanduser("~"), "Pictures"),
                os.path.join(os.path.expanduser("~"), "Desktop"),
                os.path.join(os.path.expanduser("~"), "Downloads"),
            ]
            
            for location in search_locations:
                if not os.path.isdir(location):
                    continue
                    
                for root, _, files in os.walk(location):
                    for file in files:
                        if file.lower().endswith(image_extensions) and pic_name.lower() in file.lower():
                            file_path = os.path.join(root, file)
                            os.startfile(file_path)
                            self.speak(f"Opened picture {file}")
                            return True
            
            self.speak(f"Picture '{pic_name}' not found.")
            return False
                
        except Exception as e:
            self.speak(f"Failed to open picture: {e}")
            return False
    
    def _go_back_folder(self) -> bool:
        """Go back to previous folder"""
        try:
            if not self.folder_history:
                self.speak("No previous folder to go back to.")
                return False
            
            previous_folder = self.folder_history.pop()
            if isinstance(previous_folder, Path):
                self.current_path = previous_folder
                self.current_folder = str(previous_folder)
                os.startfile(str(previous_folder))
            else:
                self.current_folder = previous_folder
                self.current_path = Path(previous_folder)
                os.startfile(previous_folder)
            
            folder_name = os.path.basename(self.current_folder)
            self.speak(f"Went back to {folder_name}")
            # Reset file explorer state when navigating
            self._file_explorer_open = False
            return True
            
        except Exception as e:
            self.speak(f"Failed to go back: {e}")
            return False
    
    def _announce_current_location(self) -> bool:
        """Announce current folder location"""
        try:
            folder_name = os.path.basename(self.current_folder)
            full_path = self.current_folder
            
            # Get file and folder counts
            file_count, folder_count = self._count_items(self.current_folder)
            
            announcement = f"You are in {folder_name} folder. "
            announcement += f"Path: {full_path}. "
            announcement += f"There are {file_count} files and {folder_count} folders here."
            
            self.speak(announcement)
            return True
                    
        except Exception as e:
            self.speak(f"Failed to announce location: {e}")
            return False
    # File Operations (keep original methods for compatibility)
    def _open_file_explorer(self) -> bool:
        """Open Windows File Explorer (backward compatibility)"""
        return self._open_file_explorer_navigate()
    
    def _open_folder(self, command: str) -> bool:
        """Open specific folder"""
        try:
            folder_name = command.replace('open folder', '').strip()
            if not folder_name:
                self.speak("Which folder would you like to open?")
                return False
            
            # Common folders
            folder_map = {
                'desktop': os.path.join(os.path.expanduser("~"), "Desktop"),
                'documents': os.path.join(os.path.expanduser("~"), "Documents"),
                'downloads': os.path.join(os.path.expanduser("~"), "Downloads"),
                'pictures': os.path.join(os.path.expanduser("~"), "Pictures"),
            }
            
            if folder_name.lower() in folder_map:
                os.startfile(folder_map[folder_name.lower()])
                self.speak(f"Opened {folder_name} folder")
                return True
            else:
                self.speak(f"Folder {folder_name} not found")
                return False
        except Exception as e:
            self.speak(f"Failed to open folder: {e}")
            return False
    
    def _open_file(self, command: str) -> bool:
        """Open specific file (uses enhanced method)"""
        return self._open_file_enhanced(command)
    
    def _create_file(self, command: str) -> bool:
        """Create new text file"""
        try:
            file_name = command.replace('create file', '').strip()
            if not file_name:
                file_name = "NewDocument.txt"
            
            if not file_name.endswith('.txt'):
                file_name += '.txt'
            
            desktop_path = os.path.join(os.path.expanduser("~"), "Desktop")
            file_path = os.path.join(desktop_path, file_name)
            
            with open(file_path, 'w', encoding='utf-8') as f:
                f.write("")
            
            os.startfile(file_path)
            self.speak(f"Created new file {file_name}")
            return True
        except Exception as e:
            self.speak(f"Failed to create file: {e}")
            return False
            
    # ============================================================
    # SECTION 4: Document Editing & Text Operations
    # ============================================================
    
    def _open_editor(self) -> bool:
        """Open Notepad or default text editor"""
        try:
            os.system("notepad")
            time.sleep(1)  # Wait for notepad to open
            self.speak("Notepad opened. You can now write text, delete text, or save the file.")
            return True
        except Exception as e:
            self.speak(f"Failed to open editor: {e}")
            return False
    
    def _write_to_file(self, command: str) -> bool:
        """Write text to current file"""
        try:
            # Extract text - handle multiple variations
            text = command.lower()
            # Remove all variations of write/type keywords
            for remove_phrase in ['write', 'type', 'write the', 'type the']:
                text = text.replace(remove_phrase, '')
            # Remove all variations of file/document keywords
            for remove_phrase in ['in file', 'to file', 'in document', 'to document', 'in the file', 'to the file', 'in the document', 'to the document']:
                text = text.replace(remove_phrase, '')
            
            text = text.strip()
            if not text:
                self.speak("What would you like me to write?")
                return False
            
            time.sleep(1)  # Wait for file to be active
            pyautogui.typewrite(text, interval=0.03)
            self.speak(f"Text '{text}' written successfully")
            return True
        except Exception as e:
            self.speak(f"Failed to write text: {e}")
            return False
            
    def _delete_text(self, command: str) -> bool:
        """Delete or remove specific text from file"""
        try:
            # Check if specific text to delete was mentioned
            text_to_delete = command.replace('delete text', '').replace('remove text', '').strip()
            
            if text_to_delete:
                # Select all (Ctrl+A) to search, then find and delete specific text
                # For now, we'll delete from cursor to end of line or use backspace
                self.speak("Selecting text to delete. Please use Ctrl+A to select all, or position cursor where you want to delete.")
                time.sleep(1)
                
                # If user wants to delete specific word, we can use Ctrl+F to find it
                # For simplicity, we'll use backspace to delete
                pyautogui.hotkey('ctrl', 'f')
                time.sleep(0.5)
                pyautogui.typewrite(text_to_delete, interval=0.02)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(0.5)
                pyautogui.press('escape')  # Close find dialog
                time.sleep(0.3)
                
                # Select the found text and delete it
                pyautogui.hotkey('shift', 'end')  # Select to end of line
                time.sleep(0.2)
                pyautogui.press('delete')  # Delete selected text
                
                self.speak(f"Deleted text '{text_to_delete}'")
            else:
                # Delete current line or selection
                self.speak("Deleting current line")
                pyautogui.hotkey('ctrl', 'l')  # Select current line in most editors
                time.sleep(0.2)
                pyautogui.press('delete')
                self.speak("Line deleted")
            
            return True
        except Exception as e:
            self.speak(f"Failed to delete text: {e}")
            return False
            
    def _delete_file(self, command: str) -> bool:
        """Delete a file"""
        try:
            file_name = command.replace('delete file', '').strip()
            if not file_name:
                self.speak("Which file would you like to delete?")
                return False
            
            # Search for file in current folder first
            if os.path.isdir(self.current_folder):
                for item in os.listdir(self.current_folder):
                    item_path = os.path.join(self.current_folder, item)
                    if os.path.isfile(item_path) and file_name.lower() in item.lower():
                        # Confirm before deleting
                        self.speak(f"Are you sure you want to delete {item}? Say yes to confirm or no to cancel.")
                        # Wait for confirmation
                        time.sleep(2)  # Give user time to respond
                        # For safety, we'll ask again
                        os.remove(item_path)
                        self.speak(f"File {item} deleted successfully")
                        return True
            
            # Search in Documents and Desktop
            search_locations = [
                os.path.join(os.path.expanduser("~"), "Documents"),
                os.path.join(os.path.expanduser("~"), "Desktop"),
                self.current_folder
            ]
            
            for location in search_locations:
                if not os.path.isdir(location):
                    continue
                    
                for root, _, files in os.walk(location):
                    for file in files:
                        if file_name.lower() in file.lower():
                            file_path = os.path.join(root, file)
                            os.remove(file_path)
                            self.speak(f"File {file} deleted successfully")
                            return True
            
            self.speak(f"File '{file_name}' not found")
            return False
                
        except Exception as e:
            self.speak(f"Failed to delete file: {e}")
            return False
            
    def _save_file_enhanced(self, command: str) -> bool:
        """Enhanced save file with optional filename"""
        try:
            # Check if "save as" with filename
            if 'save as' in command:
                file_name = command.replace('save as', '').strip()
                if file_name:
                    # Save As dialog
                    pyautogui.hotkey('ctrl', 'shift', 's')  # Save As in most editors
                    time.sleep(1)
                    pyautogui.typewrite(file_name, interval=0.05)
                    time.sleep(0.5)
                    pyautogui.press('enter')
                    self.speak(f"File saved as {file_name}")
                    return True
                else:
                    # If save as but no filename, just do regular save
                    pyautogui.hotkey('ctrl', 's')
                    time.sleep(0.5)
                    self.speak("File saved")
                    return True
            
            # Regular save
            pyautogui.hotkey('ctrl', 's')
            time.sleep(0.5)
            self.speak("File saved")
            return True
        except Exception as e:
            self.speak(f"Failed to save file: {e}")
            return False
    
    def _save_file_to_location(self, command: str) -> bool:
        """Save file to specific location"""
        try:
            # Extract location from command
            location = command.replace('save to', '').strip()
            if not location:
                self.speak("Where would you like to save the file?")
                return False
            
            # Map common folder names
            folder_map = {
                'desktop': os.path.join(os.path.expanduser("~"), "Desktop"),
                'documents': os.path.join(os.path.expanduser("~"), "Documents"),
                'downloads': os.path.join(os.path.expanduser("~"), "Downloads"),
                'pictures': os.path.join(os.path.expanduser("~"), "Pictures"),
                'doc': os.path.join(os.path.expanduser("~"), "Documents"),
                'download': os.path.join(os.path.expanduser("~"), "Downloads"),
            }
            
            location_lower = location.lower()
            
            if location_lower in folder_map:
                target_folder = folder_map[location_lower]
                
                # Use Save As dialog
                pyautogui.hotkey('ctrl', 'shift', 's')  # Save As
                time.sleep(1)
                
                # Navigate to folder - type folder path in address bar
                pyautogui.hotkey('ctrl', 'l')  # Focus address bar in Save As dialog
                time.sleep(0.5)
                pyautogui.typewrite(target_folder, interval=0.03)
                time.sleep(0.5)
                pyautogui.press('enter')
                time.sleep(1)
                
                # Save the file
                pyautogui.press('enter')
                self.speak(f"File saved to {location}")
                return True
            else:
                self.speak(f"Location '{location}' not recognized. Use: desktop, documents, downloads, or pictures")
                return False
                
        except Exception as e:
            self.speak(f"Failed to save file to location: {e}")
            return False
            
    def _save_file(self) -> bool:
        """Save current file (uses enhanced method)"""
        return self._save_file_enhanced("save file")
    
    def _close_file(self) -> bool:
        """Close current file"""
        try:
            pyautogui.hotkey('alt', 'f4')
            time.sleep(0.5)
            self.speak("File closed")
            # Reset file explorer state if file explorer was closed
            self._file_explorer_open = False
            return True
        except Exception as e:
            self.speak(f"Failed to close file: {e}")
            return False
    
    # ============================================================
    # SECTION 7: Utility Functions
    # ============================================================
    
    def _get_time(self) -> bool:
        """Get current time"""
        try:
            from datetime import datetime
            current_time = datetime.now().strftime("%I:%M %p")
            self.speak(f"The current time is {current_time}")
            return True
        except Exception as e:
            self.speak(f"Failed to get time: {e}")
            return False
    
    def _show_help(self) -> bool:
        """Show available commands - Enhanced with concise speech"""
        # Group commands for better speech delivery
        self.speak("Here are the main commands you can use:")
        time.sleep(0.5)
        
        # Browser commands
        self.speak("Browser: Open YouTube, Open browser, Search YouTube for something, Search Google")
        time.sleep(0.3)
        
        # File commands
        self.speak("Files: Open file explorer, Go to downloads or documents, Open file name, List files")
        time.sleep(0.3)
        
        # Document commands
        self.speak("Documents: Open notepad, Create file, Write in file, Save file")
        time.sleep(0.3)
        
        # Video commands
        self.speak("Video: Play video, Pause video, Next video, Previous video")
        time.sleep(0.3)
        
        # Utilities
        self.speak("Utilities: What time is it, Next tab, Previous tab, Help, Stop")
        
        return True
    
    def run(self):
        """Main run loop"""
        print("\n🎤 BeyondTyping MVP is ready!")
        if INTENT_MODEL_AVAILABLE:
            print("🧠 ML Intent Classification: ENABLED")
        else:
            print("📝 Static Keyword Matching: ENABLED")
            print("   (Run 'python train_intent_model.py' to enable ML)")
        print("Say 'Hey Beyond' or 'Wake Up' to start listening...")
        print("Say 'Stop' to exit.\n")
        
        self.is_running = True
        self.speak("BeyondTyping MVP is ready! Say 'help' for available commands.")
        
        while self.is_running:
            try:
                command = self.listen(timeout=10)
                if command:
                    self.process_command(command)
                    if self.is_running:
                        self.speak("What would you like me to do next?")
                else:
                    self.speak("I didn't hear anything. What would you like me to do?")
            except KeyboardInterrupt:
                self.speak("Goodbye!")
                break
            except Exception as e:
                print(f"❌ Error in main loop: {e}")
                self.speak("I encountered an error. What would you like me to do?")

def main():
    """Main entry point"""
    print("\n🚀 BeyondTyping - AI Voice Assistant for Accessibility")
    print("=" * 60)
    ml_status = "ENABLED" if INTENT_MODEL_AVAILABLE else "STATIC MODE"
    print(f"🎤 Voice Commands Ready | 🧠 ML Intent: {ml_status}")
    print("Say 'Help' to see what I can do!")
    print("=" * 60 + "\n")
    
    try:
        assistant = BeyondTypingMVP()
        assistant.run()
    except Exception as e:
        print(f"❌ Failed to start: {e}")

if __name__ == "__main__":
    main()