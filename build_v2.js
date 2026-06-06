const fs = require('fs');
const path = require('path');
const crypto = require('crypto');

console.log("🚀 [1/4] 开始提取旧版硬编码翻译词典...");

const extCode = fs.readFileSync('extension.js', 'utf-8');
const dict = {};

function getInsideQuotes(s) {
    const match = s.match(/(?:children|label|title|placeholder|description|text|tooltip|tooltipText|aria-label|textContent):(?:`([^`]+)`|"([^"]+)"|'([^']+)')/);
    if (match) return match[1] || match[2] || match[3];
    const pureMatch = s.match(/^"([^"]+)"$/);
    if (pureMatch) return pureMatch[1];
    return null;
}

const regex = /\[\s*'([^']*)'\s*,\s*'([^']*)'\s*\]/g;
let match;
let count = 0;

while ((match = regex.exec(extCode)) !== null) {
    let engRaw = match[1].replace(/\\"/g, '"');
    let zhRaw = match[2].replace(/\\"/g, '"').replace(/\\u([0-9a-fA-F]{4})/g, (m, c) => String.fromCharCode(parseInt(c, 16)));
    
    let eng = getInsideQuotes(engRaw);
    let zh = getInsideQuotes(zhRaw);
    
    if (!eng && engRaw.startsWith('{') && engRaw.includes('label:"')) {
        eng = engRaw.match(/label:"([^"]+)"/)?.[1];
        zh = zhRaw.match(/label:"([^"]+)"/)?.[1];
    }
    if (!eng) {
        eng = engRaw.match(/"([^"]+)"/)?.[1];
        zh = zhRaw.match(/"([^"]+)"/)?.[1];
    }
    
    if (eng && zh && eng !== zh && !eng.startsWith('${') && !eng.includes('"+')) {
        dict[eng.trim()] = zh.trim();
        count++;
    }
}

// 追加难以被正则自动提取的动态词及界面专属词汇
const manualAdditions = {
    "Thinking for ": "思考中 ",
    "Thought for ": "思考了 ",
    "Changes Overview": "更改概览",
    "Settings - ": "设置 - ",
    "Customizations": "自定义",
    "Manage": "管理",
    "Snooze": "暂停",
    "Advanced Settings": "高级设置",
    "Terminal execution policy": "终端执行策略",
    "Review policy": "审查策略",
    "JavaScript execution policy": "JavaScript 执行策略",
    "Always Proceed": "始终继续",
    "Request Review": "请求审查",
    "Agent Decides": "Agent 决定",
    "Disabled": "已禁用"
};
Object.assign(dict, manualAdditions);
count += Object.keys(manualAdditions).length;

console.log("✅ 成功提取 " + count + " 个翻译对！");

console.log("🚀 [2/4] 正在生成强健且极速的 DOM TreeWalker 监听器...");

const observerCode = `
// [AntigravityChinesePack V2 DOM Observer Injected]
(function() {
    // 避免在某些纯 worker 或不含 DOM 的环境中报错
    if (typeof document === 'undefined' || !document.body) return;
    
    console.log("[AntigravityChinesePack] V2 Dynamic DOM Observer Active");
    const dict = ${JSON.stringify(dict, null, 2)};

    function translateTextNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const originalText = node.nodeValue;
            let text = originalText.trim();
            if (!text) return;
            
            if (dict[text]) {
                node.nodeValue = originalText.replace(text, dict[text]);
                return;
            }

            // 动态前缀匹配
            if (text.startsWith("Thinking for ")) {
                node.nodeValue = originalText.replace(text, "思考中 " + text.substring("Thinking for ".length));
                return;
            }
            if (text.startsWith("Thought for ")) {
                node.nodeValue = originalText.replace(text, "思考了 " + text.substring("Thought for ".length));
                return;
            }
            if (text.startsWith("Changes Overview (")) {
                node.nodeValue = originalText.replace(text, text.replace("Changes Overview", "更改概览"));
                return;
            }
            if (text.startsWith("Terminal (") && text.includes(")")) {
                node.nodeValue = originalText.replace(text, text.replace("Terminal", "终端"));
                return;
            }
        }
    }

    function translateAttributes(node) {
        if (node.nodeType === Node.ELEMENT_NODE) {
            ['aria-label', 'title', 'placeholder'].forEach(attr => {
                if (node.hasAttribute(attr)) {
                    const val = node.getAttribute(attr);
                    if (val && dict[val]) {
                        node.setAttribute(attr, dict[val]);
                    }
                }
            });
        }
    }

    // 使用 C++ 级的 TreeWalker 进行极速文本遍历，解决界面卡顿问题
    function processTree(root) {
        if (root.nodeType === Node.TEXT_NODE) {
            translateTextNode(root);
            return;
        }
        
        const walker = document.createTreeWalker(root, NodeFilter.SHOW_TEXT, null, false);
        let node;
        while (node = walker.nextNode()) {
            translateTextNode(node);
        }
        
        if (root.nodeType === Node.ELEMENT_NODE) {
            translateAttributes(root);
            const elements = root.querySelectorAll('*');
            for (let i = 0; i < elements.length; i++) {
                translateAttributes(elements[i]);
            }
        }
    }

    let isTranslating = false;
    const observer = new MutationObserver((mutations) => {
        if (isTranslating) return;
        isTranslating = true;
        
        // 批量处理 mutations 以提升性能
        const targetNodes = new Set();
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.tagName !== 'SCRIPT' && node.tagName !== 'STYLE') {
                        targetNodes.add(node);
                    }
                });
            } else if (mutation.type === 'characterData') {
                translateTextNode(mutation.target);
            } else if (mutation.type === 'attributes') {
                const node = mutation.target;
                const attr = mutation.attributeName;
                const val = node.getAttribute(attr);
                if (val && dict[val]) {
                    node.setAttribute(attr, dict[val]);
                }
            }
        });
        
        targetNodes.forEach(node => processTree(node));
        
        isTranslating = false;
    });

    function init() {
        if (document.body) {
            processTree(document.body);
            observer.observe(document.body, { childList: true, subtree: true, characterData: true, attributes: true, attributeFilter: ['aria-label', 'title', 'placeholder'] });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
`;

fs.writeFileSync('v2_observer.js', observerCode, 'utf-8');
console.log("✅ 生成 v2_observer.js 成功！");

console.log("🚀 [3/4] 开始将新代码注入 Antigravity IDE...");

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
    { name: "Workbench (全局/自定义UI)", path: path.join(base, 'out', 'vs', 'workbench', 'workbench.desktop.main.js') }
];

const TAG = "// [AntigravityChinesePack V2 DOM Observer Injected]";
const OLD_TAG = "// [AntigravityChinesePack PoC injected]";

for (const t of targets) {
    if (!fs.existsSync(t.path)) {
        console.warn("⚠️ " + t.name + " 未找到: " + t.path);
        continue;
    }
    
    // 自动恢复旧版本的备份（如果有）以确保干净
    const backupPath = t.path + ".backup";
    if (fs.existsSync(backupPath)) {
        console.log("[" + t.name + "] 检测到备份文件，自动恢复以清除旧补丁...");
        const original = fs.readFileSync(backupPath, 'utf-8');
        fs.writeFileSync(t.path, original, 'utf-8');
    } else {
        // 创建新备份
        console.log("[" + t.name + "] 创建初始备份...");
        fs.copyFileSync(t.path, backupPath);
    }
    
    let content = fs.readFileSync(t.path, 'utf-8');
    if (content.includes(TAG)) {
        console.log("[" + t.name + "] V2 已注入！");
    } else {
        content = content.replace(OLD_TAG, ""); // 移除旧 PoC 标记
        fs.writeFileSync(t.path, content + "\n\n" + observerCode, 'utf-8');
        console.log("✅ [" + t.name + "] 成功注入 V2 动态监听器！");
    }
}

console.log("🚀 [4/4] 修复 IDE 校验值 (消除安装损坏提示)...");
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
        console.log("✅ 已更新 " + updated + " 个文件校验值！");
    } else {
        console.log("✅ 校验值已经是最新。");
    }
}
updateChecksums();

console.log("\n🎉 全部优化完成！解决了卡顿、补全了UI、消除了损坏提示。请在 IDE 中按 Ctrl+Shift+P 运行 'Developer: Reload Window' 查看效果。");
