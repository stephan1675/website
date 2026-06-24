import sys
import os
import json
from playwright.sync_api import sync_playwright

def main():
    users_path = r"c:\Users\Esisc\OneDrive - Berner Fachhochschule\Desktop\Website\users.json"
    if not os.path.exists(users_path):
        print(f"Error: users.json not found at {users_path}")
        sys.exit(1)
        
    with open(users_path, 'r', encoding='utf-8') as f:
        users = json.load(f)
    
    user = next((u for u in users if u["username"] == "steste"), None)
    if not user:
        print("User steste not found in users.json")
        sys.exit(1)
        
    token = user.get("sessionToken")
    if not token:
        print("Session token for steste not found")
        sys.exit(1)

    print(f"Using session token: {token[:8]}...")

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(viewport={"width": 1280, "height": 800})
        page = context.new_page()
        
        page.goto("http://localhost:8000")
        page.evaluate(f"localStorage.setItem('sessionToken', '{token}')")
        
        page.goto("http://localhost:8000")
        page.wait_for_timeout(2000)
        
        try:
            page.locator('#home-to-dash-btn').click(timeout=5000)
            page.wait_for_timeout(1000)
        except Exception as e:
            print("Warning: Could not click dashboard button.")
        
        try:
            page.locator('.project-selector-item').first.click(timeout=5000)
            page.wait_for_timeout(1000)
        except Exception as e:
            print("Warning: Could not click first project item.")
        
        output_path = r"c:\Users\Esisc\OneDrive - Berner Fachhochschule\Desktop\Website\screenshot.png"
        page.screenshot(path=output_path)
        print(f"Screenshot successfully saved to {output_path}")
        browser.close()

if __name__ == "__main__":
    main()
