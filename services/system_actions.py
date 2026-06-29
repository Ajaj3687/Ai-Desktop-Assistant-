import subprocess
import os
import webbrowser
import datetime
import re
import requests
from dotenv import load_dotenv

class SystemActionsManager:
    def __init__(self):
        # Dynamically load env keys on instance creation using absolute path
        project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        dotenv_path = os.path.join(project_root, ".env")
        load_dotenv(dotenv_path)
        self.weather_api_key = os.getenv("WEATHER_API_KEY")

    def process_command(self, command_text):
        """Parses the text command. If it matches a system or web intent, executes it and returns a response.
        If no local intent matches, returns (False, None)."""
        cmd = command_text.lower().strip()
        
        # 1. Open Notepad
        if re.search(r'\b(open|launch|start)\s+notepad\b', cmd):
            try:
                # Use Popen to run asynchronously without blocking the thread
                subprocess.Popen(["notepad.exe"])
                return True, "Opening Notepad."
            except Exception as e:
                return True, f"Failed to open Notepad: {str(e)}"

        # 2. Open Calculator
        if re.search(r'\b(open|launch|start)\s+(calculator|calc)\b', cmd):
            try:
                subprocess.Popen(["calc.exe"])
                return True, "Opening Calculator."
            except Exception as e:
                return True, f"Failed to open Calculator: {str(e)}"

        # 3. Open Command Prompt
        if re.search(r'\b(open|launch|start)\s+(cmd|command prompt|terminal)\b', cmd):
            try:
                subprocess.Popen(["cmd.exe"])
                return True, "Opening Command Prompt."
            except Exception as e:
                return True, f"Failed to open Command Prompt: {str(e)}"

        # 4. Open Google / Web Browser / Chrome
        if re.search(r'\b(open|launch|start)\s+(google|browser|chrome|chrom)\b', cmd):
            try:
                webbrowser.open("https://www.google.com")
                return True, "Opening Google in default web browser."
            except Exception as e:
                return True, f"Failed to open browser: {str(e)}"

        # 5. Search Google
        search_match = re.search(r'\b(?:search\s+(?:google|web|online)\s+for|google\s+search|search)\s+(.+)', cmd)
        if search_match and not "wikipedia" in cmd and not "youtube" in cmd:
            query = search_match.group(1).strip()
            try:
                webbrowser.open(f"https://www.google.com/search?q={query}")
                return True, f"Searching Google for '{query}'."
            except Exception as e:
                return True, f"Failed to perform Google search: {str(e)}"

        # 6. Current Time
        if re.search(r'\b(what is the time|current time|what time is it|time)\b', cmd):
            now = datetime.datetime.now()
            time_str = now.strftime("%I:%M %p")
            date_str = now.strftime("%A, %B %d, %Y")
            return True, f"The current time is {time_str} on {date_str}."

        # 7. Weather
        weather_match = re.search(r'\b(?:weather\s+in|check\s+weather\s+in|weather\s+forecast\s+for)\s+([a-zA-Z\s]+)', cmd)
        if weather_match:
            city = weather_match.group(1).strip()
            return True, self.get_weather(city)

        # 8. Wikipedia Summary
        wiki_match = re.search(r'\b(?:wikipedia|search\s+wikipedia\s+for|tell\s+me\s+about|who\s+is|what\s+is)\s+(.+)', cmd)
        if wiki_match:
            entity = wiki_match.group(1).strip()
            entity = entity.rstrip("?.!,")
            # Prevent matches for system utilities to fall here
            if entity not in [
                "notepad", "calculator", "cmd", "google", "browser", "time", 
                "settings", "openweathermap", "whatsapp", "file explorer", 
                "explorer", "task manager", "taskmgr", "paint", "camera", 
                "youtube", "vs code", "code", "battery", "lock screen", "lock computer"
            ]:
                return True, self.get_wikipedia_summary(entity)

        # 9. Open Settings
        if re.search(r'\b(open|launch|start)\s+settings\b', cmd):
            try:
                subprocess.Popen(["cmd.exe", "/c", "start ms-settings:"])
                return True, "Opening Windows Settings."
            except Exception as e:
                return True, f"Failed to open Settings: {str(e)}"

        # 10. Open OpenWeatherMap Website
        if re.search(r'\b(?:open\s+)?openweathermap\b', cmd):
            try:
                webbrowser.open("https://openweathermap.org")
                return True, "Opening OpenWeatherMap website."
            except Exception as e:
                return True, f"Failed to open website: {str(e)}"

        # 11. Open WhatsApp
        if re.search(r'\b(open|launch|start)\s+whatsapp\b', cmd):
            try:
                # Try launching Windows Store app protocol
                subprocess.Popen(["cmd.exe", "/c", "start whatsapp:"])
                return True, "Opening WhatsApp Desktop App."
            except Exception:
                try:
                    webbrowser.open("https://web.whatsapp.com")
                    return True, "Opening WhatsApp Web."
                except Exception as e:
                    return True, f"Failed to open WhatsApp: {str(e)}"

        # 12. Open File Explorer
        if re.search(r'\b(open|launch|start)\s+(file explorer|explorer|documents|my files)\b', cmd):
            try:
                subprocess.Popen(["explorer.exe"])
                return True, "Opening File Explorer."
            except Exception as e:
                return True, f"Failed to open File Explorer: {str(e)}"

        # 13. Open Task Manager
        if re.search(r'\b(open|launch|start)\s+(task manager|taskmgr)\b', cmd):
            try:
                subprocess.Popen(["taskmgr.exe"])
                return True, "Opening Task Manager."
            except Exception as e:
                return True, f"Failed to open Task Manager: {str(e)}"

        # 14. Open Paint
        if re.search(r'\b(open|launch|start)\s+(paint|mspaint)\b', cmd):
            try:
                subprocess.Popen(["mspaint.exe"])
                return True, "Opening Paint."
            except Exception as e:
                return True, f"Failed to open Paint: {str(e)}"

        # 15. Open Camera
        if re.search(r'\b(open|launch|start)\s+camera\b', cmd):
            try:
                subprocess.Popen(["cmd.exe", "/c", "start microsoft.windows.camera:"])
                return True, "Opening Camera."
            except Exception as e:
                return True, f"Failed to open Camera: {str(e)}"

        # 16. Search / Open YouTube
        youtube_search_match = re.search(r'\b(?:search\s+youtube\s+for|youtube\s+search)\s+(.+)', cmd)
        if youtube_search_match:
            query = youtube_search_match.group(1).strip()
            try:
                webbrowser.open(f"https://www.youtube.com/results?search_query={query}")
                return True, f"Searching YouTube for '{query}'."
            except Exception as e:
                return True, f"Failed to perform YouTube search: {str(e)}"

        if re.search(r'\b(open|launch|start)\s+youtube\b', cmd):
            try:
                webbrowser.open("https://www.youtube.com")
                return True, "Opening YouTube in default browser."
            except Exception as e:
                return True, f"Failed to open YouTube: {str(e)}"

        # 17. Open VS Code
        if re.search(r'\b(open|launch|start)\s+(vs\s*code|visual studio code|code)\b', cmd):
            try:
                # Use shell=True for code script to execute correctly on Windows shell paths
                subprocess.Popen("code", shell=True)
                return True, "Opening Visual Studio Code."
            except Exception as e:
                return True, f"Failed to open VS Code: {str(e)}"

        # 18. Check Battery Status
        if re.search(r'\b(battery|check battery|battery status|battery percentage|how much battery)\b', cmd):
            return True, self.get_battery_status()

        # 19. Lock Computer / Screen
        if re.search(r'\b(lock\s+(computer|screen|pc|workstation))\b', cmd):
            try:
                subprocess.Popen(["rundll32.exe", "user32.dll,LockWorkStation"])
                return True, "Locking your computer screen."
            except Exception as e:
                return True, f"Failed to lock screen: {str(e)}"

        return False, None

    def get_battery_status(self):
        """Retrieves system battery level using PowerShell/wmic."""
        try:
            # Query battery percentage via wmic
            result = subprocess.run(
                ["wmic", "path", "Win32_Battery", "get", "EstimatedChargeRemaining"],
                capture_output=True, text=True, check=True
            )
            lines = result.stdout.strip().split('\n')
            if len(lines) > 1:
                pct = lines[1].strip()
                if pct.isdigit():
                    return f"Your battery is currently at {pct}%."
            
            # Fallback to PowerShell
            result_ps = subprocess.run(
                ["powershell", "-Command", "Get-CimInstance -ClassName Win32_Battery | Select-Object -ExpandProperty EstimatedChargeRemaining"],
                capture_output=True, text=True, check=True
            )
            pct = result_ps.stdout.strip()
            if pct.isdigit():
                return f"Your battery is currently at {pct}%."
                
            return "Could not retrieve battery percentage. Your device might be a desktop or the battery driver is unavailable."
        except Exception as e:
            return f"Error retrieving battery status: {str(e)}"

    def get_weather(self, city):
        """Fetches weather from OpenWeatherMap API. If key is missing, returns simulated mock data."""
        if not self.weather_api_key or self.weather_api_key.strip() == "" or "YOUR_" in self.weather_api_key:
            # Provide mock data if key is not configured yet
            return (f"Weather API key is not configured in .env. Here is a simulated report for {city.capitalize()}: "
                    "Clear sky, 24°C, 65% humidity with a gentle breeze.")
        
        try:
            url = f"http://api.openweathermap.org/data/2.5/weather?q={city}&appid={self.weather_api_key}&units=metric"
            res = requests.get(url, timeout=5)
            if res.status_code == 200:
                data = res.json()
                temp = data['main']['temp']
                desc = data['weather'][0]['description']
                humidity = data['main']['humidity']
                return f"Currently in {city.capitalize()}: {desc.capitalize()}, Temperature {temp}°C, Humidity {humidity}%."
            elif res.status_code == 401:
                return f"Invalid OpenWeatherMap API key in .env. (Simulating search for: {city.capitalize()})"
            else:
                return f"Could not find weather data for '{city}'. Please verify the city name."
        except Exception as e:
            return f"Weather API error: {str(e)}"

    def get_wikipedia_summary(self, query):
        """Fetches a concise Wikipedia summary using OpenSearch API for spell correction first."""
        try:
            headers = {"User-Agent": "AIDesktopAssistant/1.0 (contact@example.com)"}
            
            # Step 1: Use OpenSearch API to get the correct title/spelling suggestion
            search_url = f"https://en.wikipedia.org/w/api.php?action=opensearch&search={query}&limit=1&format=json"
            search_res = requests.get(search_url, headers=headers, timeout=5)
            
            target_title = query.replace(" ", "_")
            if search_res.status_code == 200:
                search_data = search_res.json()
                if len(search_data) > 1 and len(search_data[1]) > 0:
                    target_title = search_data[1][0].replace(" ", "_")
            
            # Step 2: Fetch the summary using the corrected page title
            url = f"https://en.wikipedia.org/api/rest_v1/page/summary/{target_title}"
            res = requests.get(url, headers=headers, timeout=5)
            if res.status_code == 200:
                data = res.json()
                extract = data.get("extract", "")
                # Format to a short response (first two sentences)
                sentences = re.split(r'\.\s+', extract)
                short_summary = ". ".join(sentences[:2])
                if not short_summary.endswith("."):
                    short_summary += "."
                return f"According to Wikipedia: {short_summary}"
            else:
                return f"I couldn't find a Wikipedia page for '{query}'."
        except Exception as e:
            return f"Wikipedia search failed: {str(e)}"
