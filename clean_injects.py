import os
import sys
import json
import hashlib
import base64

print("🚨 开始执行紧急清理程序...")

def get_app_base():
    localappdata = os.environ.get('LOCALAPPDATA', '')
    if localappdata:
        win_candidate = os.path.join(localappdata, 'Programs', 'Antigravity IDE', 'resources', 'app')
        if os.path.exists(win_candidate):
            return win_candidate
    return None

BASE = get_app_base()
if not BASE:
    print("❌ 找不到 Antigravity IDE 安装目录！")
    sys.exit(1)

TARGETS = {
    'settings': os.path.join(BASE, 'out', 'jetskiAgent', 'main.js'),
    'chat': os.path.join(BASE, 'extensions', 'antigravity', 'out', 'media', 'chat.js'),
    'workbench': os.path.join(BASE, 'out', 'vs', 'workbench', 'workbench.desktop.main.js'),
}

# 需要切除的所有残留代码标记
TAGS = [
    "// [AntigravityChinesePack PoC injected]",
    "// [AntigravityChinesePack V2 DOM Observer Injected]",
    "// [AntigravityChinesePack V3 Hybrid Observer Injected]"
]

for name, filepath in TARGETS.items():
    if not os.path.exists(filepath):
        continue
    with open(filepath, 'r', encoding='utf-8', errors='replace') as f:
        content = f.read()
    
    modified = False
    for tag in TAGS:
        if tag in content:
            # 切除该标记及其后面的所有注入代码
            content = content.split(tag)[0]
            modified = True
            print(f"🔪 发现残留代码，正在清理 {name} ...")
            
    if modified:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(content)
        print(f"✅ {name} 成功清理了所有引起卡顿的残留代码！")
    else:
        print(f"✅ {name} 很干净。")

# 重新计算哈希值以修复“安装损坏”
PRODUCT_JSON = os.path.join(BASE, 'product.json')
if os.path.exists(PRODUCT_JSON):
    with open(PRODUCT_JSON, 'r', encoding='utf-8') as f:
        product = json.load(f)
    checksums = product.get('checksums', {})
    updated = 0
    for key in checksums:
        for prefix in [os.path.join(BASE, 'out'), BASE]:
            fpath = os.path.normpath(os.path.join(prefix, key))
            if os.path.exists(fpath):
                with open(fpath, 'rb') as f:
                    data = f.read()
                new_hash = base64.b64encode(hashlib.sha256(data).digest()).decode('ascii').rstrip('=')
                if new_hash != checksums[key]:
                    checksums[key] = new_hash
                    updated += 1
                break
    if updated > 0:
        product['checksums'] = checksums
        with open(PRODUCT_JSON, 'w', encoding='utf-8') as f:
            json.dump(product, f, indent='\t', ensure_ascii=False)
        print(f"✅ 重新计算并修复了 {updated} 个文件的校验哈希值。")
    else:
         print(f"✅ 哈希值无需更新。")

print("\n🎉 紧急清理完成！请彻底关闭 IDE 窗口并重新打开。")
