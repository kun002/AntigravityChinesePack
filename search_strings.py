"""
search_strings.py — 在 Antigravity IDE 目标文件中搜索指定字符串并打印上下文片段。
用法:
    python search_strings.py [目标文件路径]
如果不提供参数，脚本会尝试自动推导 Windows 默认安装路径。
"""
import re
import sys
import os


def get_default_path():
    localappdata = os.environ.get('LOCALAPPDATA', '')
    return os.path.join(localappdata, 'Programs', 'Antigravity IDE',
                        'resources', 'app', 'out', 'jetskiAgent', 'main.js')


target_path = sys.argv[1] if len(sys.argv) > 1 else get_default_path()

if not os.path.exists(target_path):
    print(f"[错误] 文件不存在: {target_path}")
    print("用法: python search_strings.py <目标文件路径>")
    sys.exit(1)

with open(target_path, 'r', encoding='utf-8') as f:
    content = f.read()

words = [
    'Account', 'Permissions', 'Appearance', 'Notifications',
    "Configure the agent's visual theme and display preferences.",
    'Controls whether terminal commands require your approval before running.'
]

for w in words:
    # Find occurrences and print surrounding context (30 chars before, 30 chars after)
    matches = list(re.finditer(re.escape(w), content))
    print(f"--- Matches for '{w}' ({len(matches)} found) ---")
    # Just show the first 3 matches to save space
    for match in matches[:3]:
        start = max(0, match.start() - 30)
        end = min(len(content), match.end() + 30)
        snippet = content[start:end]
        print("..." + snippet + "...")
