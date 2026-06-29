# AI Desktop Virtual Assistant 🎙️⚡

A modern, lightweight, and offline-first **AI-Powered Desktop Virtual Assistant** built using Python and **CustomTkinter**. This project is structured according to professional software development standards, combining local system automation, offline speech synthesis, REST API integrations, and cloud conversational AI fallback.

It captures both keyboard (text) and microphone (voice) inputs, executes local utility triggers (opening apps, checking system metrics, locking the screen), queries web services (fetching weather, searching Wikipedia, searching YouTube), and falls back on the Google Gemini API for open-ended conversation.

---

## 🚀 Key Features

### 1. Concurrency & Thread-Safe UI
* **Zero GUI Freezes:** Multi-threaded architecture runs speech recognition (STT), text-to-speech playback (TTS), and Gemini API calls on background worker threads.
* **FIFO Queue Coordination:** Communicates thread-safely with the Tkinter event loop using `queue.Queue` to prevent crashes or unstable GUI behaviors.

### 2. Hands-Free Wake Word Activation
* **Continuous Background Listener:** Toggleable **Always Listen** mode in the sidebar enables background monitoring for the word **"Assistant"** (e.g., *"Hey Assistant"*, *"Hi Assistant"*, *"Ok Assistant"*).
* **One-Time Micro Calibration:** Calibrates microphone noise levels exactly once on thread activation, eliminating 1-second delays and keeping the microphone hot.
* **Direct Execution:** Parse speech containing both wake word and command in one breath (e.g., *"Hey Assistant, open Paint"*).

### 3. Native Windows System Automation
Matches intent patterns asynchronously to execute shell commands:
* 📂 **File Explorer:** *"open file explorer"*, *"open documents"* ➔ launches `explorer.exe`
* ⚙️ **Windows Settings:** *"open settings"* ➔ launches settings panel
* 💻 **Task Manager:** *"open task manager"*, *"launch taskmgr"* ➔ launches `taskmgr.exe`
* 🎨 **MS Paint:** *"open paint"*, *"launch paint"* ➔ launches `mspaint.exe`
* 📷 **Camera:** *"open camera"*, *"launch camera"* ➔ launches default Camera app
* 🔒 **Workstation Lock:** *"lock screen"*, *"lock computer"* ➔ locks the Windows session
* 📝 **Notepad:** *"open notepad"* ➔ launches `notepad.exe`
* 🧮 **Calculator:** *"open calculator"* ➔ launches `calc.exe`
* 📟 **Command Prompt:** *"open terminal"*, *"open command prompt"* ➔ launches `cmd.exe`
* 💬 **WhatsApp:** *"open whatsapp"* ➔ launches WhatsApp Desktop or Web
* 🔋 **Diagnostics:** *"check battery"*, *"battery percentage"* ➔ retrieves real-time battery charge status via WMIC/PowerShell

### 4. Web API & Search Integrations
* **OpenWeatherMap REST API:** Fetches live temperature and humidity for any city (with interactive fallback).
* **Wikipedia Summary Search:** Retrieves concise descriptions for query topics using Wikipedia's REST API.
* **YouTube Search:** Instantly opens YouTube search queries (e.g., *"search youtube for cat videos"*).
* **Google Search:** Opens search results in the default web browser (e.g., *"search python tutorials"*).

### 5. Google Gemini Conversational Fallback
* Connects to `gemini-2.5-flash` with conversational memory context (last 4 turns) to reply to arbitrary conversational inputs.
* Uses system instructions to restrict answers to under 2 precise sentences, keeping replies concise.

---

## 📁 Directory Structure

```text
ai_desktop_assistant/
│
├── config/
│   ├── settings.json       # Visual preference settings & wake word toggle state
│   └── .env.example        # Environment configuration template
│
├── database/
│   ├── __init__.py         # Exposes DatabaseManager class
│   ├── db_manager.py       # SQLite connection, schema creation, query executors
│   └── logs.db             # Local SQLite database file (ignored in .gitignore)
│
├── gui/
│   ├── __init__.py         # Exposes MainWindow UI class
│   ├── main_window.py      # Tkinter window initialization & background threads
│   └── widgets.py          # Custom ChatBubble and StateIndicator widgets
│
├── services/
│   ├── __init__.py         # Service namespace packaging
│   ├── tts_service.py      # Pyttsx3 offline text-to-speech synthesiser
│   ├── stt_service.py      # SpeechRecognition microphone listener & wake word checker
│   ├── ai_service.py       # Gemini API caller with mock system
│   └── system_actions.py   # Intent router, system commands, weather, and wiki APIs
│
├── tests/
│   ├── __init__.py         # Test package initializer
│   └── test_services.py    # Unit tests for DB, intents, and API mocks
│
├── .env                    # Active local credentials (gitignored)
├── .gitignore              # Ignores credentials, database logs, and caches
├── requirements.txt        # PIP dependencies manifest
├── README.md               # Project setup and developer guide
└── main.py                 # Core entry point executable
```

---

## 🛠️ Installation & Setup

### 1. Prerequisites
Ensure you have **Python 3.10+** installed on your system.

### 2. Set Up the Project
Clone or copy the directory and navigate into it:
```powershell
cd C:\Users\Ajaj Ansari\.gemini\antigravity\scratch\ai_desktop_assistant
```

### 3. Create a Virtual Environment & Install Dependencies
Setting up a virtual environment isolates your packages:
```powershell
# Create virtual environment
python -m venv .venv

# Activate virtual environment
.venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt
```

#### 🎙️ Microphone Support (Python 3.14+ Note)
Standard `pyaudio` wheels might not be available on PyPI for newer Python versions. 
* On **Python 3.14+**, `requirements.txt` is configured to automatically download `pyaudiowpatch` on Windows, which acts as a drop-in replacement.
* If PyAudio is missing, you can run the app in **Text Mode**. The microphone button will gracefully report that the mic interface is offline.

---

## 🔑 Configure API Keys

1. Copy `config/.env.example` to the root folder as `.env`.
2. Open `.env` and fill in your credentials:
   * **Gemini API Key:** Get a free key from [Google AI Studio](https://aistudio.google.com/).
   * **Weather API Key:** Get a free key from [OpenWeatherMap](https://openweathermap.org/api).

```text
GEMINI_API_KEY=your_actual_gemini_api_key
WEATHER_API_KEY=your_actual_openweathermap_api_key
```
*Note: If left blank, the app runs with simulated fallback mocks without crashing.*

---

## 🎯 How to Use

Run the main application:
```powershell
python main.py
```

### 1. Wake Word Activation (Hands-Free)
* Toggle the **Always Listen (Wake Word)** switch to **ON** in the left sidebar.
* Say: *"Hey Assistant"* ➔ Assistant wakes up and asks *"Yes? I'm listening..."*, waiting for your command.
* Say: *"Hey Assistant, check battery"* ➔ Assistant wakes up and executes the command directly.

### 2. Voice Button Command
* Click the **🎙️** button, wait for the state indicator to change to **LISTENING...**, and speak your command.

### 3. Text Command
* Type your query in the input bar and press **Enter** or click **Send**.

---

## 🧪 Running Unit Tests

Automated testing is configured using Pytest. To run the test suite and confirm intent routing:
```powershell
python -m pytest tests/
```

---

## 📦 Standalone Compilation

To compile the assistant into a single standalone executable file (`.exe` on Windows):
```powershell
pip install pyinstaller
pyinstaller --noconsole --onefile main.py
```
The compiled file will be located inside the `dist/` directory.
