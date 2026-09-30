import os
import time
import re
import subprocess
import pyautogui
import pyperclip
from datetime import datetime

pyautogui.PAUSE = 0.8
pyautogui.FAILSAFE = True

now = datetime.now()
current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now.strftime("%Y-%m-%d")

desktop_dir = os.path.expanduser("~/Desktop")
workspace_dir = os.getcwd()

numbers_filename = f"daily_report_{today_date_str}.numbers"
full_numbers_path = os.path.join(desktop_dir, numbers_filename)

screenshot_filename = f"daily_report_screenshot_{today_date_str}.png"
screenshot_path = os.path.join(workspace_dir, screenshot_filename)

quote = '"Investing should be more like watching paint dry or watching grass grow. If you want excitement, take $800 and go to Las Vegas." — Paul Samuelson'

# Step 1: Launch Chrome, Maximize Window via Mouse, and Navigate
sensex_url = "https://www.moneycontrol.com/indian-indices/bsesensex-4.html"

applescript_launch_chrome = '''
tell application "Google Chrome"
    activate
    make new window
end tell
'''
subprocess.run(["osascript", "-e", applescript_launch_chrome])
time.sleep(1.5)

# Click macOS green zoom button to maximize window
pyautogui.click(x=53, y=53)
time.sleep(1)

# Navigate to target URL
pyautogui.hotkey('command', 'l')
time.sleep(0.5)
pyperclip.copy(sensex_url)
pyautogui.hotkey('command', 'v')
pyautogui.press('enter')

time.sleep(6)
pyautogui.hotkey('command', 'r')
time.sleep(8)

# Step 2: Extract Market Information via Clipboard
subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
time.sleep(0.5)

# Click canvas center to focus webpage body
pyautogui.click(x=500, y=500)
time.sleep(0.5)

pyautogui.hotkey('command', 'a')
time.sleep(0.5)
pyautogui.hotkey('command', 'c')
time.sleep(1)

raw_page_text = pyperclip.paste()
normalized_text = " ".join(raw_page_text.split())

def extract_full_sensex_details(text):
    pattern = r"SENSEX.*?\s*([\d,]+\.\d+)\s*([+-]?[\d,]+\.\d+)\s*\(\s*([+-]?[\d,]+\.\d+%\s*)\)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return {
            "value": match.group(1),
            "change": match.group(2),
            "p_change": match.group(3).replace(" ", "")
        }
    
    try:
        if "SENSEX" in text.upper():
            after_sensex = text.upper().split("SENSEX")[1].strip()
            tokens = after_sensex.split()
            price = next(t for t in tokens if "." in t and t.replace(",", "").replace(".", "").isdigit())
            p_change = next(t for t in tokens if "%" in t)
            change = next(t for t in tokens if t.startswith("-") or t.startswith("+"))
            return {"value": price, "change": change, "p_change": p_change}
    except Exception:
        pass

    return {"value": "N/A", "change": "N/A", "p_change": "N/A"}

market_data = extract_full_sensex_details(normalized_text)

# Step 3: Populate Apple Numbers Spreadsheet
subprocess.Popen(["open", "-a", "Numbers"])
time.sleep(1)

subprocess.run(["osascript", "-e", 'tell application "Numbers" to activate'])
time.sleep(1.5)

pyautogui.hotkey('command', 'n')
time.sleep(1.5)
pyautogui.press('enter')
time.sleep(2)

headers = ["Date & Time", "Sensex Value", "Change Value", "Percentage Change", "Investment Quote"]
row_data = [current_time_str, market_data['value'], market_data['change'], market_data['p_change'], quote]

def write_row_to_numbers(row_list):
    for item in row_list:
        pyperclip.copy(str(item))
        pyautogui.hotkey('command', 'v')
        pyautogui.press('tab')
    pyautogui.press('enter')

write_row_to_numbers(headers)
write_row_to_numbers(row_data)

# Step 4: Save Native Document (.numbers) to Desktop
pyautogui.press('escape')
pyautogui.press('escape')
time.sleep(0.5)

pyautogui.hotkey('command', 's')
time.sleep(1.5)

pyautogui.hotkey('command', 'shift', 'g')
time.sleep(1)

pyperclip.copy(full_numbers_path)
pyautogui.hotkey('command', 'v')
time.sleep(0.5)

pyautogui.press('enter')
time.sleep(1)

pyautogui.press('enter')
time.sleep(2)

# Step 5: Capture Screenshot to VS Code Workspace
screenshot = pyautogui.screenshot()
screenshot.save(screenshot_path)