import pytest
import os
import re
from unittest.mock import patch, MagicMock
from database.db_manager import DatabaseManager
from services.system_actions import SystemActionsManager
from services.ai_service import GeminiAIService
from services.stt_service import STTEngine

@pytest.fixture
def temp_db(tmp_path):
    db_file = tmp_path / "test_logs.db"
    db = DatabaseManager(db_path=str(db_file))
    yield db

def test_db_manager_operations(temp_db):
    # Verify setup
    assert os.path.exists(temp_db.db_path)
    
    # Verify insert logs
    temp_db.log_message("user", "Hello Assistant")
    temp_db.log_message("assistant", "Hello User")
    
    logs = temp_db.get_recent_logs(limit=10)
    assert len(logs) == 2
    assert logs[0][0] == "user"
    assert logs[0][1] == "Hello Assistant"
    assert logs[1][0] == "assistant"
    assert logs[1][1] == "Hello User"
    
    # Verify clear logs
    temp_db.clear_logs()
    assert len(temp_db.get_recent_logs()) == 0

@pytest.fixture
def actions_manager():
    return SystemActionsManager()

@patch('subprocess.Popen')
def test_open_notepad(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("open notepad")
    assert matched is True
    assert "Notepad" in response
    mock_popen.assert_called_once_with(["notepad.exe"])

@patch('subprocess.Popen')
def test_open_calculator(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("launch calculator")
    assert matched is True
    assert "Calculator" in response
    mock_popen.assert_called_once_with(["calc.exe"])

@patch('subprocess.Popen')
def test_open_settings(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("open settings")
    assert matched is True
    assert "Settings" in response
    mock_popen.assert_called_once_with(["cmd.exe", "/c", "start ms-settings:"])

@patch('webbrowser.open')
def test_open_google(mock_webbrowser, actions_manager):
    matched, response = actions_manager.process_command("start browser")
    assert matched is True
    assert "Google" in response
    mock_webbrowser.assert_called_once_with("https://www.google.com")

@patch('webbrowser.open')
def test_open_openweathermap(mock_webbrowser, actions_manager):
    matched, response = actions_manager.process_command("open openweathermap")
    assert matched is True
    assert "OpenWeatherMap" in response
    mock_webbrowser.assert_called_once_with("https://openweathermap.org")

@patch('subprocess.Popen')
def test_open_whatsapp(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("open whatsapp")
    assert matched is True
    assert "WhatsApp" in response
    mock_popen.assert_called_once_with(["cmd.exe", "/c", "start whatsapp:"])

@patch('webbrowser.open')
def test_search_google(mock_webbrowser, actions_manager):
    matched, response = actions_manager.process_command("search python tutorial")
    assert matched is True
    assert "Searching" in response
    mock_webbrowser.assert_called_once_with("https://www.google.com/search?q=python tutorial")

def test_current_time(actions_manager):
    matched, response = actions_manager.process_command("what is the time")
    assert matched is True
    assert "The current time is" in response

def test_unmatched_command(actions_manager):
    matched, response = actions_manager.process_command("tell me a story")
    assert matched is False
    assert response is None

@patch('requests.get')
def test_get_weather_with_api_key(mock_get, actions_manager):
    actions_manager.weather_api_key = "fake_key"
    
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "main": {"temp": 15.5, "humidity": 70},
        "weather": [{"description": "overcast clouds"}]
    }
    mock_get.return_value = mock_response
    
    response = actions_manager.get_weather("london")
    assert "London" in response
    assert "15.5" in response
    assert "Humidity 70" in response
    assert "Overcast clouds" in response

def test_get_weather_mock_fallback(actions_manager):
    actions_manager.weather_api_key = ""
    response = actions_manager.get_weather("paris")
    assert "Weather API key is not configured" in response
    assert "Paris" in response

@patch('requests.get')
def test_get_wikipedia_summary(mock_get, actions_manager):
    mock_response = MagicMock()
    mock_response.status_code = 200
    mock_response.json.return_value = {
        "extract": "Albert Einstein was a physicist. He developed the theory of general relativity."
    }
    mock_get.return_value = mock_response
    
    matched, response = actions_manager.process_command("wikipedia Albert Einstein")
    assert matched is True
    assert "According to Wikipedia" in response
    assert "Albert Einstein was a physicist" in response

def test_gemini_mock_fallback():
    with patch('os.getenv', return_value=""):
        service = GeminiAIService()
        assert service.model is None
        
        reply = service.get_response("who are you")
        assert "AI Desktop Assistant" in reply
        
        reply = service.get_response("hello")
        assert "configure your GEMINI_API_KEY" in reply

def test_stt_check_wake_word():
    engine = STTEngine()
    
    # Pure wake word
    is_match, cmd = engine.check_wake_word("hey assistant")
    assert is_match is True
    assert cmd == ""
    
    # Wake word with command
    is_match, cmd = engine.check_wake_word("hey assistant open notepad")
    assert is_match is True
    assert cmd == "open notepad"
    
    # Wake word with commas and extra whitespace
    is_match, cmd = engine.check_wake_word("Hey assistant, please search weather in london")
    assert is_match is True
    assert cmd == "search weather in london"
    
    # No wake word
    is_match, cmd = engine.check_wake_word("hey helper")
    assert is_match is False
    assert cmd == ""

@patch('subprocess.Popen')
def test_open_file_explorer(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("open file explorer")
    assert matched is True
    assert "File Explorer" in response
    mock_popen.assert_called_once_with(["explorer.exe"])

@patch('subprocess.Popen')
def test_open_task_manager(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("launch task manager")
    assert matched is True
    assert "Task Manager" in response
    mock_popen.assert_called_once_with(["taskmgr.exe"])

@patch('subprocess.Popen')
def test_open_paint(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("open paint")
    assert matched is True
    assert "Paint" in response
    mock_popen.assert_called_once_with(["mspaint.exe"])

@patch('subprocess.Popen')
def test_open_camera(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("launch camera")
    assert matched is True
    assert "Camera" in response
    mock_popen.assert_called_once_with(["cmd.exe", "/c", "start microsoft.windows.camera:"])

@patch('webbrowser.open')
def test_open_youtube(mock_webbrowser, actions_manager):
    matched, response = actions_manager.process_command("open youtube")
    assert matched is True
    assert "YouTube" in response
    mock_webbrowser.assert_called_once_with("https://www.youtube.com")

@patch('webbrowser.open')
def test_search_youtube(mock_webbrowser, actions_manager):
    matched, response = actions_manager.process_command("search youtube for cat videos")
    assert matched is True
    assert "YouTube" in response
    mock_webbrowser.assert_called_once_with("https://www.youtube.com/results?search_query=cat videos")

@patch('subprocess.Popen')
def test_open_vs_code(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("open vs code")
    assert matched is True
    assert "Visual Studio Code" in response
    mock_popen.assert_called_once_with("code", shell=True)

@patch('subprocess.run')
def test_check_battery(mock_run, actions_manager):
    # Mock battery check response
    mock_res = MagicMock()
    mock_res.stdout = "EstimatedChargeRemaining\n85\n"
    mock_run.return_value = mock_res
    
    matched, response = actions_manager.process_command("check battery percentage")
    assert matched is True
    assert "85%" in response

@patch('subprocess.Popen')
def test_lock_computer(mock_popen, actions_manager):
    matched, response = actions_manager.process_command("lock computer")
    assert matched is True
    assert "Locking" in response
    mock_popen.assert_called_once_with(["rundll32.exe", "user32.dll,LockWorkStation"])
