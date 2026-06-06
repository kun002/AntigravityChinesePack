const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

console.log("🚀 [1/3] 开始构建 V3 混合模式 (静态全覆盖 + 动态轻量捕获)...");

// 1. 获取原有的所有静态替换对
const extCode = fs.readFileSync('extension.js', 'utf-8');
const replacements = [];
const regex = /\[\s*'([^']*)'\s*,\s*'([^']*)'\s*\]/g;
let match;
while ((match = regex.exec(extCode)) !== null) {
    let engRaw = match[1].replace(/\\"/g, '"');
    let zhRaw = match[2].replace(/\\"/g, '"').replace(/\\u([0-9a-fA-F]{4})/g, (m, c) => String.fromCharCode(parseInt(c, 16)));
    replacements.push({ old: engRaw, new: zhRaw });
}

console.log("✅ 成功提取 " + replacements.length + " 个底层静态替换规则。");

// 2. 轻量级动态监听器 (仅针对静态替换无法处理的动态拼接字符串)
const tinyObserverCode = `
// [AntigravityChinesePack V3 Hybrid Observer Injected]
(function() {
    if (typeof document === 'undefined' || !document.body) return;
    
    function translateDynamicText(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            let text = node.nodeValue;
            if (!text) return;
            
            if (text.startsWith("Thinking for ")) {
                node.nodeValue = text.replace("Thinking for ", "思考中 ");
            } else if (text.startsWith("Thought for ")) {
                node.nodeValue = text.replace("Thought for ", "思考了 ");
            } else if (text.startsWith("Changes Overview (")) {
                node.nodeValue = text.replace("Changes Overview", "更改概览");
            } else if (text.startsWith("Terminal (") && text.includes(")")) {
                node.nodeValue = text.replace("Terminal", "终端");
            }
        }
    }

    const observer = new MutationObserver(mutations => {
        mutations.forEach(m => {
            if (m.type === 'characterData') {
                translateDynamicText(m.target);
            } else if (m.type === 'childList') {
                m.addedNodes.forEach(node => {
                    if (node.nodeType === Node.TEXT_NODE) {
                        translateDynamicText(node);
                    } else if (node.nodeType === Node.ELEMENT_NODE && node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
                        const walker = document.createTreeWalker(node, NodeFilter.SHOW_TEXT, null, false);
                        let n;
                        while (n = walker.nextNode()) translateDynamicText(n);
                    }
                });
            }
        });
    });

    observer.observe(document.body, { childList: true, subtree: true, characterData: true });
})();
`;

console.log("🚀 [2/3] 开始应用底层静态替换并注入动态监听器...");

function getAppBase() {
    const localappdata = process.env.LOCALAPPDATA;
    if (localappdata) {
        const winCandidate = path.join(localappdata, 'Programs', 'Antigravity IDE', 'resources', 'app');
        if (fs.existsSync(winCandidate)) return winCandidate;
    }
    return null;
}

const base = getAppBase();
if (!base) {
    console.error("❌ 找不到 Antigravity IDE 安装目录！");
    process.exit(1);
}

const targets = [
    { name: "Chat Panel", path: path.join(base, 'extensions', 'antigravity', 'out', 'media', 'chat.js') },
    { name: "Settings Panel", path: path.join(base, 'out', 'jetskiAgent', 'main.js') },
    { name: "Workbench Panel", path: path.join(base, 'out', 'vs', 'workbench', 'workbench.desktop.main.js') }
];

const V3_TAG = "// [AntigravityChinesePack V3 Hybrid Observer Injected]";
const V2_TAG = "// [AntigravityChinesePack V2 DOM Observer Injected]";
const POC_TAG = "// [AntigravityChinesePack PoC injected]";

for (const t of targets) {
    if (!fs.existsSync(t.path)) {
        console.warn("⚠️ " + t.name + " 未找到: " + t.path);
        continue;
    }
    
    const backupPath = t.path + ".backup";
    if (fs.existsSync(backupPath)) {
        // 恢复原始文件，确保不叠加执行
        const original = fs.readFileSync(backupPath, 'utf-8');
        fs.writeFileSync(t.path, original, 'utf-8');
    } else {
        fs.copyFileSync(t.path, backupPath);
    }
    
    let content = fs.readFileSync(t.path, 'utf-8');
    
    // 执行底层的静态硬编码替换 (解决自定义UI、ShadowDOM 和 WebComponent 等不暴露给DOM的问题，且零性能损耗)
    let replaceCount = 0;
    for (const rule of replacements) {
        if (content.includes(rule.old)) {
            content = content.split(rule.old).join(rule.new);
            replaceCount++;
        }
    }
    
    // 注入轻量动态监听器
    content = content + "\n\n" + tinyObserverCode;
    fs.writeFileSync(t.path, content, 'utf-8');
    
    console.log("✅ [" + t.name + "] 底层静态替换完成 (" + replaceCount + " 处)，并成功注入极速 V3 动态监听器！");
}

console.log("🚀 [3/3] 更新 IDE 文件校验值...");
function updateChecksums() {
    const productJsonPath = path.join(base, 'product.json');
    if (!fs.existsSync(productJsonPath)) return;
    
    let product = JSON.parse(fs.readFileSync(productJsonPath, 'utf-8'));
    let checksums = product.checksums || {};
    let updated = 0;
    
    for (let key in checksums) {
        let filePath = path.join(base, 'out', key);
        if (!fs.existsSync(filePath)) {
            filePath = path.join(base, key);
        }
        if (fs.existsSync(filePath)) {
            let data = fs.readFileSync(filePath);
            let hash = crypto.createHash('sha256').update(data).digest('base64').replace(/=+$/, '');
            if (hash !== checksums[key]) {
                checksums[key] = hash;
                updated++;
            }
        }
    }
    
    if (updated > 0) {
        fs.writeFileSync(productJsonPath, JSON.stringify(product, null, '\t'), 'utf-8');
        console.log("✅ 已更新 " + updated + " 个文件校验值，消除“安装损坏”提示！");
    } else {
        console.log("✅ 校验值已经是最新。");
    }
}
updateChecksums();

console.log("\n🎉 V3 终极版构建完成！结合了“静态替换的零卡顿/全覆盖”与“动态监听的无遗漏”，请在 IDE 中按 Ctrl+Shift+P 运行 'Developer: Reload Window' 查看效果！");
