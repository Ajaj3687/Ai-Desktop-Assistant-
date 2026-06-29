import queue
import threading
import json
import os
import time
import customtkinter as ctk
from gui.widgets import ChatBubble, StateIndicator
from services.tts_service import TTSEngine
from services.stt_service import STTEngine
from services.system_actions import SystemActionsManager
from services.ai_service import GeminiAIService
from database.db_manager import DatabaseManager

class MainWindow(ctk.CTk):
    def __init__(self):
        super().__init__()
        
        # Load user configurations
        self.config = self._load_config()
        
        # Configure root window properties
        self.title("AI Desktop Virtual Assistant")
        self.geometry("780x680")
        self.resizable(False, False)
        
        # Set themes using CustomTkinter engine
        ctk.set_appearance_mode(self.config.get("theme", "Dark"))
        ctk.set_default_color_theme(self.config.get("color_theme", "blue"))

        # Initialize thread-safe communication queue
        self.msg_queue = queue.Queue()

        # Initialize core service engines
        self.tts = TTSEngine(
            rate=self.config.get("voice_rate", 180),
            volume=self.config.get("voice_volume", 1.0),
            gender=self.config.get("voice_gender", "female")
        )
        self.stt = STTEngine()
        self.actions = SystemActionsManager()
        self.ai = GeminiAIService()
        self.db = DatabaseManager()
        
        # Wake word state variables
        self.wake_word_enabled = self.config.get("wake_word_enabled", False)
        self.wake_word_thread_active = False
        self.current_state = "IDLE"

        # Build application layout widgets
        self._build_ui()

        # Start periodic queue checking loop in main thread (runs every 100ms)
        self.after(100, self.check_queue)
        
        # Set close protocol
        self.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Load and display recent chat history
        recent_logs = self.db.get_recent_logs(limit=10)
        for sender, msg, timestamp in recent_logs:
            ChatBubble(self.chat_scroll, text=msg, sender=sender)
        
        # If no logs exist, show a welcome message
        if not recent_logs:
            self._append_message("Hello! I am your AI Desktop Assistant. How can I help you today?", "assistant")
            self.db.log_message("assistant", "Hello! I am your AI Desktop Assistant. How can I help you today?")
            
        # Refresh history sidebar
        self._refresh_history()
        
        # Start background wake word listener thread if enabled
        if self.wake_word_enabled:
            self.start_wake_word_thread()

    def _load_config(self):
        """Loads configuration from JSON file. Falls back to defaults if file missing."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")
        defaults = {
            "theme": "Dark",
            "color_theme": "blue",
            "voice_rate": 180,
            "voice_volume": 1.0,
            "voice_gender": "female",
            "wake_word_enabled": False
        }
        
        if os.path.exists(config_path):
            try:
                with open(config_path, 'r') as f:
                    return json.load(f)
            except Exception:
                pass
        return defaults

    def _build_ui(self):
        """Draws the main CustomTkinter visual hierarchy with left sidebar."""
        # Left Sidebar Frame
        self.sidebar_frame = ctk.CTkFrame(self, width=240, corner_radius=0)
        self.sidebar_frame.pack(side="left", fill="y")
        self.sidebar_frame.pack_propagate(False) # Keep fixed width

        # Sidebar Title
        self.sidebar_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="History & Settings",
            font=("Segoe UI", 16, "bold")
        )
        self.sidebar_title.pack(pady=(20, 10), padx=15, anchor="w")
        
        self.sidebar_divider = ctk.CTkFrame(self.sidebar_frame, height=2, fg_color="#3a3a3a")
        self.sidebar_divider.pack(fill="x", padx=15, pady=(0, 15))

        # Recent Commands Section
        self.history_title = ctk.CTkLabel(
            self.sidebar_frame,
            text="Recent Commands",
            font=("Segoe UI", 12, "bold"),
            text_color="#9e9e9e"
        )
        self.history_title.pack(padx=15, anchor="w")
        
        self.history_scroll = ctk.CTkScrollableFrame(
            self.sidebar_frame,
            fg_color="transparent",
            height=320
        )
        self.history_scroll.pack(fill="both", expand=True, padx=10, pady=5)

        # Clear History Button
        self.clear_btn = ctk.CTkButton(
            self.sidebar_frame,
            text="Clear History",
            height=32,
            fg_color="#c0392b",
            hover_color="#e74c3c",
            font=("Segoe UI", 12, "bold"),
            command=self.clear_history
        )
        self.clear_btn.pack(fill="x", padx=15, pady=(10, 10))

        # Theme Dropdown
        self.theme_label = ctk.CTkLabel(
            self.sidebar_frame,
            text="Appearance Theme",
            font=("Segoe UI", 12, "bold"),
            text_color="#9e9e9e"
        )
        self.theme_label.pack(padx=15, anchor="w", pady=(10, 2))
        
        self.theme_dropdown = ctk.CTkOptionMenu(
            self.sidebar_frame,
            values=["Dark", "Light", "System"],
            command=self.change_theme
        )
        self.theme_dropdown.pack(fill="x", padx=15, pady=(0, 20))
        self.theme_dropdown.set(self.config.get("theme", "Dark"))

        # Wake Word Activation Switch
        self.wake_switch = ctk.CTkSwitch(
            self.sidebar_frame,
            text="Always Listen (Wake Word)",
            font=("Segoe UI", 12, "bold"),
            command=self.toggle_wake_word
        )
        self.wake_switch.pack(padx=15, pady=(10, 20), anchor="w")
        if self.wake_word_enabled:
            self.wake_switch.select()
        else:
            self.wake_switch.deselect()

        # Right Main Container
        self.main_container = ctk.CTkFrame(self, fg_color="transparent")
        self.main_container.pack(side="right", fill="both", expand=True, padx=20, pady=15)

        # 1. Header Area
        self.header_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.header_frame.pack(fill="x", pady=(0, 10))

        self.title_label = ctk.CTkLabel(
            self.header_frame, 
            text="Desktop AI Assistant", 
            font=("Segoe UI", 18, "bold")
        )
        self.title_label.pack(side="left")

        # Visual state indicator
        self.indicator = StateIndicator(self.header_frame)
        self.indicator.pack(side="right")

        # Divider
        self.divider = ctk.CTkFrame(self.main_container, height=2, fg_color="#3a3a3a")
        self.divider.pack(fill="x", pady=(0, 15))

        # 2. Scrollable Chat Display Panel
        self.chat_scroll = ctk.CTkScrollableFrame(
            self.main_container, 
            fg_color="#1e1e1e", 
            corner_radius=12
        )
        self.chat_scroll.pack(fill="both", expand=True, pady=(0, 15))

        # 3. Input & Control Deck
        self.input_frame = ctk.CTkFrame(self.main_container, fg_color="transparent")
        self.input_frame.pack(fill="x")

        # Voice Record Toggle Button
        self.record_btn = ctk.CTkButton(
            self.input_frame, 
            text="🎙️", 
            width=45, 
            height=45, 
            corner_radius=22, 
            font=("Segoe UI", 16),
            command=self.start_voice_recognition
        )
        self.record_btn.pack(side="left", padx=(0, 10))

        # Text input field
        self.text_entry = ctk.CTkEntry(
            self.input_frame, 
            placeholder_text="Ask me to open apps, search the web, or type here...",
            height=45, 
            corner_radius=8
        )
        self.text_entry.pack(side="left", fill="x", expand=True, padx=(0, 10))
        self.text_entry.bind("<Return>", lambda e: self.send_text_message())

        # Submit message button
        self.send_btn = ctk.CTkButton(
            self.input_frame, 
            text="Send", 
            width=70, 
            height=45, 
            corner_radius=8,
            font=("Segoe UI", 13, "bold"),
            command=self.send_text_message
        )
        self.send_btn.pack(side="right")

    def send_text_message(self):
        """Event fired when sending text via entry field or submit button."""
        query = self.text_entry.get().strip()
        if not query:
            return
        
        # Clear field and block inputs temporarily to prevent parallel triggers
        self.text_entry.delete(0, "end")
        self._toggle_input_states("disabled")
        self.current_state = "PROCESSING"
        
        # Append User Message
        self._append_message(query, "user")
        self.db.log_message("user", query)
        self._refresh_history()
        
        # Start background processing thread
        threading.Thread(target=self._query_processing_worker, args=(query,), daemon=True).start()

    def start_voice_recognition(self):
        """Initiates background audio capture thread."""
        self._toggle_input_states("disabled")
        self.indicator.set_state("LISTENING")
        self.current_state = "LISTENING"
        
        # Start background recording thread
        threading.Thread(target=self._voice_record_worker, daemon=True).start()

    def _voice_record_worker(self):
        """Worker executing STT listening loops in background thread."""
        success, payload = self.stt.listen_and_transcribe()
        if success:
            self.msg_queue.put(("USER_SPEECH", payload))
        else:
            self.msg_queue.put(("SYSTEM_REPLY", payload))

    def _query_processing_worker(self, query):
        """Worker routing the user command through local intent parsing or Gemini API fallback."""
        self.msg_queue.put(("STATE", "PROCESSING"))
        
        # Step 1: Run intent processor for system integrations
        matched, response = self.actions.process_command(query)
        
        # Step 2: Fall back to conversational LLM if no local rule matches
        if not matched:
            response = self.ai.get_response(query)
            
        self.msg_queue.put(("SYSTEM_REPLY", response))

    def _tts_speak_worker(self, text):
        """Worker synthesizing speech in background."""
        self.tts.speak(text)
        self.msg_queue.put(("STATE", "IDLE"))

    def check_queue(self):
        """Checks for messages from background threads and updates the GUI on the main thread."""
        try:
            while True:
                msg_type, payload = self.msg_queue.get_nowait()
                
                if msg_type == "STATE":
                    self.indicator.set_state(payload)
                    self.current_state = payload
                    
                elif msg_type == "USER_SPEECH":
                    # Display user's spoken words
                    self._append_message(payload, "user")
                    self.db.log_message("user", payload)
                    self._refresh_history()
                    # Auto start processing of transcribed query
                    threading.Thread(target=self._query_processing_worker, args=(payload,), daemon=True).start()
                    
                elif msg_type == "USER_SPEECH_DIRECT":
                    # Prepend wake word for clarity in UI history
                    full_text = f"Hey assistant, {payload}"
                    self._append_message(full_text, "user")
                    self.db.log_message("user", full_text)
                    self._refresh_history()
                    # Directly process query
                    threading.Thread(target=self._query_processing_worker, args=(payload,), daemon=True).start()

                elif msg_type == "WAKE_WORD_DETECTED":
                    # Visual and prompt wake up
                    self._append_message("Yes? I'm listening...", "assistant")
                    self.db.log_message("assistant", "Yes? I'm listening...")
                    self._refresh_history()
                    self.start_voice_recognition()

                elif msg_type == "SYSTEM_REPLY":
                    # Display response in scroll frame
                    self._append_message(payload, "assistant")
                    self.db.log_message("assistant", payload)
                    self._refresh_history()
                    self.indicator.set_state("SPEAKING")
                    self.current_state = "SPEAKING"
                    # Start speaking voice output in background
                    threading.Thread(target=self._tts_speak_worker, args=(payload,), daemon=True).start()
                    # Re-enable inputs
                    self._toggle_input_states("normal")
                    
        except queue.Empty:
            pass

        # Re-queue callback check
        self.after(100, self.check_queue)

    def toggle_wake_word(self):
        """Enables or disables continuous background wake word listening."""
        self.wake_word_enabled = self.wake_switch.get() == 1
        self.config["wake_word_enabled"] = self.wake_word_enabled
        self._save_config()
        
        if self.wake_word_enabled:
            self._append_message("Wake Word Activation enabled. Say 'Hey Assistant' to wake me up.", "assistant")
            self.start_wake_word_thread()
        else:
            self._append_message("Wake Word Activation disabled.", "assistant")

    def start_wake_word_thread(self):
        """Starts the background wake word listening thread if not already running."""
        if not self.wake_word_thread_active:
            self.wake_word_thread_active = True
            threading.Thread(target=self._wake_word_listener_worker, daemon=True).start()

    def _wake_word_listener_worker(self):
        """Background worker thread that continuously listens for the wake word 'Hey Assistant'."""
        # Calibrate background noise level once at start to establish the threshold
        try:
            with sr.Microphone() as source:
                self.stt.recognizer.adjust_for_ambient_noise(source, duration=1.0)
        except Exception as e:
            print(f"[Wake Word Worker] Microphone calibration error: {e}")

        while self.wake_word_enabled:
            # Only listen if assistant is completely IDLE
            if self.current_state == "IDLE":
                # Generous timeout & phrase limit to keep CPU usage low and avoid cutting off user command.
                # Pass calibrate=False to keep the mic hot and avoid 1s deaf calibration delays.
                success, text = self.stt.listen_and_transcribe(timeout=3, phrase_time_limit=5, calibrate=False)
                if success:
                    is_match, command = self.stt.check_wake_word(text)
                    if is_match:
                        if command:
                            self.msg_queue.put(("USER_SPEECH_DIRECT", command))
                        else:
                            self.msg_queue.put(("WAKE_WORD_DETECTED", None))
            
            # Prevent thread from spin-locking
            time.sleep(0.5)
            
        self.wake_word_thread_active = False

    def _append_message(self, text, sender):
        """Safely appends a message bubble inside scroll view and auto-scrolls to bottom."""
        ChatBubble(self.chat_scroll, text=text, sender=sender)
        self.update_idletasks()
        try:
            # Safely scroll canvas view to bottom
            self.chat_scroll._parent_canvas.yview_moveto(1.0)
        except Exception:
            pass

    def _toggle_input_states(self, state):
        """Enables/Disables visual control widgets to prevent race conditions during query runs."""
        self.text_entry.configure(state=state)
        self.send_btn.configure(state=state)
        self.record_btn.configure(state=state)

    def _save_config(self):
        """Saves configuration to JSON file."""
        config_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), "config", "settings.json")
        try:
            os.makedirs(os.path.dirname(config_path), exist_ok=True)
            with open(config_path, 'w') as f:
                json.dump(self.config, f, indent=4)
        except Exception as e:
            print(f"Error saving configurations: {e}")

    def clear_history(self):
        """Clears SQLite history and resets chat interface."""
        self.db.clear_logs()
        self._refresh_history()
        # Clear chat view scroll panel
        for widget in self.chat_scroll.winfo_children():
            widget.destroy()
        self._append_message("History cleared. How can I help you today?", "assistant")
        self.db.log_message("assistant", "History cleared. How can I help you today?")
        self._refresh_history()

    def change_theme(self, new_theme):
        """Changes GUI styling theme dynamically and persists settings."""
        ctk.set_appearance_mode(new_theme)
        self.config["theme"] = new_theme
        self._save_config()

    def _refresh_history(self):
        """Refreshes the sidebar's recent commands list."""
        for widget in self.history_scroll.winfo_children():
            widget.destroy()
        
        logs = self.db.get_recent_logs(limit=10)
        # Display latest at the top of history
        for sender, message, timestamp in reversed(logs):
            prefix = "👤 " if sender == "user" else "🤖 "
            # Trim message content for display
            display_text = message[:20] + "..." if len(message) > 20 else message
            
            lbl = ctk.CTkLabel(
                self.history_scroll,
                text=f"{prefix}{display_text}",
                font=("Segoe UI", 11),
                anchor="w",
                justify="left"
            )
            lbl.pack(fill="x", padx=5, pady=2)

    def on_closing(self):
        """Gracefully closes app, stopping speech execution."""
        self.wake_word_enabled = False # Terminate background wake-word loop if active
        try:
            if self.tts and self.tts.engine:
                self.tts.engine.stop()
        except Exception:
            pass
        self.destroy()
