#!/usr/bin/env python3
"""
纯 Python VSIX 打包脚本 —— 不依赖 npm/vsce
VSIX 格式 = ZIP 压缩包 + [Content_Types].xml + extension/package.json 等文件
"""
import os
import json
import zipfile
import shutil
from datetime import datetime

# ============================================================
# 配置
# ============================================================
PROJECT_ROOT = os.path.dirname(os.path.abspath(__file__))
VSCODEIGNORE_PATH = os.path.join(PROJECT_ROOT, '.vscodeignore')

# 读取 package.json 获取版本号和包名
with open(os.path.join(PROJECT_ROOT, 'package.json'), 'r', encoding='utf-8') as f:
    pkg = json.load(f)

VERSION = pkg['version']
NAME = pkg['name']
PUBLISHER = pkg.get('publisher', 'unknown')
OUTPUT_FILENAME = f"{PUBLISHER}.{NAME}-{VERSION}.vsix"
OUTPUT_PATH = os.path.join(PROJECT_ROOT, OUTPUT_FILENAME)

# ============================================================
# 读取 .vscodeignore 排除规则
# ============================================================
def load_ignore_patterns():
    patterns = []
    if os.path.exists(VSCODEIGNORE_PATH):
        with open(VSCODEIGNORE_PATH, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#'):
                    patterns.append(line)
    # 默认排除
    patterns += ['.git/**', '.git', '__pycache__/**', '*.pyc', '*.vsix']
    return patterns

def should_ignore(rel_path, patterns):
    """判断文件是否应该被排除（简单版 glob 匹配）"""
    import fnmatch
    rel_path = rel_path.replace('\\', '/')
    for pattern in patterns:
        pattern = pattern.replace('\\', '/')
        # 处理 **/ 开头的模式
        if pattern.endswith('/**'):
            folder = pattern[:-3]
            if rel_path.startswith(folder + '/') or rel_path == folder:
                return True
        elif pattern.startswith('**/'):
            suffix = pattern[3:]
            if fnmatch.fnmatch(rel_path, suffix) or fnmatch.fnmatch(os.path.basename(rel_path), suffix):
                return True
            # 检查是否在任意子目录下
            parts = rel_path.split('/')
            for i in range(len(parts)):
                if fnmatch.fnmatch('/'.join(parts[i:]), suffix):
                    return True
        elif '/' in pattern:
            if fnmatch.fnmatch(rel_path, pattern) or rel_path.startswith(pattern.rstrip('*') ):
                return True
        else:
            if fnmatch.fnmatch(os.path.basename(rel_path), pattern):
                return True
    return False

# ============================================================
# Content_Types.xml（必需的 VSIX 元数据文件）
# ============================================================
CONTENT_TYPES_XML = '''<?xml version="1.0" encoding="utf-8"?>
<Types xmlns="http://schemas.openxmlformats.org/package/2006/content-types">
  <Default Extension=".vsixmanifest" ContentType="text/xml" />
  <Default Extension=".json" ContentType="application/json" />
  <Default Extension=".js" ContentType="application/javascript" />
  <Default Extension=".ts" ContentType="text/plain" />
  <Default Extension=".md" ContentType="text/plain" />
  <Default Extension=".txt" ContentType="text/plain" />
  <Default Extension=".png" ContentType="image/png" />
  <Default Extension=".jpg" ContentType="image/jpeg" />
  <Default Extension=".svg" ContentType="image/svg+xml" />
  <Default Extension=".css" ContentType="text/css" />
  <Default Extension=".html" ContentType="text/html" />
  <Default Extension=".map" ContentType="application/json" />
  <Default Extension=".py" ContentType="text/plain" />
</Types>'''

# ============================================================
# 生成 .vsixmanifest
# ============================================================
def make_vsixmanifest():
    display_name = pkg.get('displayName', NAME)
    description = pkg.get('description', '')
    icon_path = pkg.get('icon', '')
    tags = ';'.join(pkg.get('keywords', []))
    repo_url = pkg.get('repository', {}).get('url', '') if isinstance(pkg.get('repository'), dict) else ''
    license_val = pkg.get('license', 'MIT')
    
    icon_line = f'<Icon>extension/{icon_path}</Icon>' if icon_path else ''
    
    return f'''<?xml version="1.0" encoding="utf-8"?>
<PackageManifest Version="2.0.0" xmlns="http://schemas.microsoft.com/developer/vsx-schema/2011" xmlns:d="http://schemas.microsoft.com/developer/vsx-schema-design/2011">
  <Metadata>
    <Identity Language="en-US" Id="{NAME}" Version="{VERSION}" Publisher="{PUBLISHER}" />
    <DisplayName>{display_name}</DisplayName>
    <Description xml:space="preserve">{description}</Description>
    <Tags>{tags}</Tags>
    <Categories>Language Packs,Other</Categories>
    <GalleryFlags>Public</GalleryFlags>
    {icon_line}
    <Properties>
      <Property Id="Microsoft.VisualStudio.Code.Engine" Value="^1.68.0" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionDependencies" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.ExtensionPack" Value="" />
      <Property Id="Microsoft.VisualStudio.Code.LocalizedLanguages" Value="" />
      <Property Id="Microsoft.VisualStudio.Services.GitHubFlavoredMarkdown" Value="true" />
      <Property Id="Microsoft.VisualStudio.Services.Links.Source" Value="{repo_url}" />
    </Properties>
    <License>extension/LICENSE</License>
  </Metadata>
  <Installation>
    <InstallationTarget Id="Microsoft.VisualStudio.Code" />
  </Installation>
  <Dependencies />
  <Assets>
    <Asset Type="Microsoft.VisualStudio.Code.Manifest" Path="extension/package.json" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.Details" Path="extension/README.md" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.Changelog" Path="extension/CHANGELOG.md" Addressable="true" />
    <Asset Type="Microsoft.VisualStudio.Services.Content.License" Path="extension/LICENSE" Addressable="true" />
    {f'<Asset Type="Microsoft.VisualStudio.Services.Icons.Default" Path="extension/{icon_path}" Addressable="true" />' if icon_path else ''}
  </Assets>
</PackageManifest>'''

# ============================================================
# 打包主逻辑
# ============================================================
def build_vsix():
    ignore_patterns = load_ignore_patterns()
    
    print(f"[PACK] {PUBLISHER}.{NAME} v{VERSION}")
    print(f"   Output: {OUTPUT_PATH}")
    print()
    
    # 收集要打包的文件
    files_to_pack = []
    for root, dirs, files in os.walk(PROJECT_ROOT):
        # 跳过 .git 目录
        dirs[:] = [d for d in dirs if d != '.git' and d != '__pycache__']
        
        for fname in files:
            full_path = os.path.join(root, fname)
            rel_path = os.path.relpath(full_path, PROJECT_ROOT).replace('\\', '/')
            
            if should_ignore(rel_path, ignore_patterns):
                continue
            
            files_to_pack.append((full_path, rel_path))
    
    # 写入 ZIP
    with zipfile.ZipFile(OUTPUT_PATH, 'w', zipfile.ZIP_DEFLATED, compresslevel=9) as zf:
        # 1. [Content_Types].xml
        zf.writestr('[Content_Types].xml', CONTENT_TYPES_XML)
        
        # 2. extension.vsixmanifest
        zf.writestr('extension.vsixmanifest', make_vsixmanifest())
        
        # 3. 扩展文件（放在 extension/ 目录下）
        for full_path, rel_path in files_to_pack:
            arc_path = f'extension/{rel_path}'
            print(f"   + {arc_path}")
            zf.write(full_path, arc_path)
    
    size_kb = os.path.getsize(OUTPUT_PATH) / 1024
    print()
    print(f"[OK] Done!")
    print(f"   File: {OUTPUT_FILENAME}")
    print(f"   Size: {size_kb:.1f} KB")
    print(f"   Files: {len(files_to_pack) + 2}")
    print()
    print("[i] Install:")
    print(f"   Extensions: Install from VSIX...")
    print(f"   -> {OUTPUT_PATH}")

if __name__ == '__main__':
    build_vsix()

