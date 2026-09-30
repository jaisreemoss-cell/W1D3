import os
import time
import re
import subprocess
import pyautogui
import pyperclip
from datetime import datetime

# ---------------------------------------------------------
# PyAutoGUI Safety & Configuration
# ---------------------------------------------------------
pyautogui.PAUSE = 0.8
pyautogui.FAILSAFE = True  # Move mouse pointer to top-left corner to abort script

# Timestamps & File Paths (Saving directly to Desktop)
now = datetime.now()
current_time_str = now.strftime("%Y-%m-%d %H:%M:%S")
today_date_str = now.strftime("%Y-%m-%d")

desktop_dir = os.path.expanduser("~/Desktop")
numbers_filename = f"daily_report_{today_date_str}.numbers"
full_numbers_path = os.path.join(desktop_dir, numbers_filename)
screenshot_path = os.path.join(desktop_dir, f"daily_report_screenshot_{today_date_str}.png")

quote = '"Investing should be more like watching paint dry or watching grass grow. If you want excitement, take $800 and go to Las Vegas." — Paul Samuelson'

print(f"Starting automated keyboard workflow at {current_time_str}...")
print("Move mouse to top-left corner at any time to abort.")
time.sleep(2)

# ---------------------------------------------------------
# Step 1: Open Chrome, Maximize Window via AppleScript, then Navigate
# ---------------------------------------------------------
sensex_url = "https://www.moneycontrol.com/indian-indices/bsesensex-4.html"

applescript_launch_chrome = f'''
tell application "Finder"
    set desktopBounds to bounds of window of desktop
    set screenWidth to item 3 of desktopBounds
    set screenHeight to item 4 of desktopBounds
end tell

tell application "Google Chrome"
    activate
    if (count of windows) is 0 then
        make new window
    end if
    set bounds of front window to {{0, 25, screenWidth, screenHeight}}
    set URL of active tab of front window to "{sensex_url}"
end tell
'''
subprocess.run(["osascript", "-e", applescript_launch_chrome])

print("Waiting 6 seconds for initial page load...")
time.sleep(6)

print("Reloading page (Cmd + R) to ensure fresh market data...")
pyautogui.hotkey('command', 'r')

print("Waiting 8 seconds for reloaded page elements to render...")
time.sleep(8)

# ---------------------------------------------------------
# Step 2: Extract Sensex Details via Keyboard Copy
# ---------------------------------------------------------
# Explicitly focus Chrome window and click page body
subprocess.run(["osascript", "-e", 'tell application "Google Chrome" to activate'])
time.sleep(0.5)

pyautogui.click(x=500, y=500)
time.sleep(0.5)

# Copy all page content (Cmd + A, Cmd + C)
pyautogui.hotkey('command', 'a')
time.sleep(0.5)
pyautogui.hotkey('command', 'c')
time.sleep(1)

# Retrieve and clean up clipboard text
raw_page_text = pyperclip.paste()
normalized_text = " ".join(raw_page_text.split())

def extract_full_sensex_details(text):
    # Match layout: SENSEX <PRICE> <CHANGE> (<PERCENTAGE>%)
    pattern = r"SENSEX.*?\s*([\d,]+\.\d+)\s*([+-]?[\d,]+\.\d+)\s*\(\s*([+-]?[\d,]+\.\d+%\s*)\)"
    match = re.search(pattern, text, re.IGNORECASE)
    if match:
        return {
            "value": match.group(1),
            "change": match.group(2),
            "p_change": match.group(3).replace(" ", "")
        }
    
    # Fallback parsing logic
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

print("\n--- Extracted Market Data ---")
print(f"Timestamp:      {current_time_str}")
print(f"Sensex Value:   {market_data['value']}")
print(f"Change Value:   {market_data['change']}")
print(f"Percentage:     {market_data['p_change']}")
print("-----------------------------\n")

# ---------------------------------------------------------
# Step 3: Populate Apple Numbers Spreadsheet
# ---------------------------------------------------------
subprocess.Popen(["open", "-a", "Numbers"])
time.sleep(1)

subprocess.run(["osascript", "-e", 'tell application "Numbers" to activate'])
time.sleep(1.5)

# Create New Spreadsheet (Cmd + N) and select Default Blank template
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

# ---------------------------------------------------------
# Step 4: Save Native Document (.numbers) via Cmd + S
# ---------------------------------------------------------
# Press Escape twice to clear active cell editing/cursor focus
pyautogui.press('escape')
pyautogui.press('escape')
time.sleep(0.5)

# Open Save Dialog (Cmd + S)
pyautogui.hotkey('command', 's')
time.sleep(1.5)

# Open macOS "Go to Folder" modal (Cmd + Shift + G)
pyautogui.hotkey('command', 'shift', 'g')
time.sleep(1)

# Paste complete file destination path onto Desktop
pyperclip.copy(full_numbers_path)
pyautogui.hotkey('command', 'v')
time.sleep(0.5)

# Confirm "Go to Folder" path
pyautogui.press('enter')
time.sleep(1)

# Confirm Save button
pyautogui.press('enter')
time.sleep(2)

# ---------------------------------------------------------
# Step 5: Capture Screenshot
# ---------------------------------------------------------
screenshot = pyautogui.screenshot()
screenshot.save(screenshot_path)

print("==========================================")
print("WORKFLOW COMPLETED SUCCESSFULLY!")
print(f"1. Numbers File Saved To: {full_numbers_path}")
print(f"2. Screenshot Saved To:   {screenshot_path}")
print("==========================================")