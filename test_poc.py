import os
import sys

def get_app_base():
    localappdata = os.environ.get('LOCALAPPDATA', '')
    if localappdata:
        win_candidate = os.path.join(localappdata, 'Programs', 'Antigravity IDE', 'resources', 'app')
        if os.path.exists(win_candidate):
            return win_candidate
    return None

BASE = get_app_base()
if not BASE:
    print("Could not find Antigravity IDE installation.")
    sys.exit(1)

chat_js_path = os.path.join(BASE, 'extensions', 'antigravity', 'out', 'media', 'chat.js')
settings_js_path = os.path.join(BASE, 'out', 'jetskiAgent', 'main.js')

targets = [
    ("Chat Panel", chat_js_path),
    ("Settings Panel", settings_js_path)
]

with open('poc_observer.js', 'r', encoding='utf-8') as f:
    poc_code = f.read()

TAG = "// [AntigravityChinesePack PoC injected]"

for name, path in targets:
    if not os.path.exists(path):
        print(f"[{name}] Not found at {path}")
        continue
    
    backup_path = path + ".backup"
    if not os.path.exists(backup_path):
        print(f"[{name}] Creating backup...")
        with open(path, 'r', encoding='utf-8') as f:
            original = f.read()
        with open(backup_path, 'w', encoding='utf-8') as f:
            f.write(original)
            
    with open(path, 'r', encoding='utf-8') as f:
        content = f.read()
        
    if TAG in content:
        print(f"[{name}] PoC already injected! If you updated poc_observer.js, you must restore the backup first or manually remove the old injection.")
    else:
        new_content = content + "\n\n" + poc_code
        with open(path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        print(f"[{name}] Successfully injected PoC!")
