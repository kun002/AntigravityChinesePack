// [AntigravityChinesePack PoC injected]
(function() {
    console.log("[AntigravityChinesePack] MutationObserver PoC loaded!");

    const dict = {
        "Conversation mode": "对话模式",
        "Customizations": "自定义",
        "Rules": "规则",
        "Workflows": "工作流",
        "MCP Servers": "MCP 服务器",
        "History": "历史记录",
        "Delete Conversation": "删除对话",
        "Cancel": "取消",
        "Confirm": "确认",
        "Close": "关闭",
        "Open": "打开",
        "Thinking": "思考中",
        "Analyzed": "已分析",
        "Error": "错误",
        "Good": "好",
        "Bad": "差",
        "Copy": "复制",
        "Paste": "粘贴",
        "Export": "导出",
        "Enable": "启用",
        "Settings - ": "设置 - ",
        "Start conversation": "开始对话",
        "Good response": "好的响应",
        "Bad response": "差的响应",
        "Planning": "规划",
        "Fast": "快速直跑",
        "Artifacts": "产物",
        "Sources": "来源",
        "Agent Auto-Fix Lints": "Agent 自动修复 Lint",
        "Strict Mode": "严格模式",
        "Review Policy": "审查策略",
        "Terminal Command Auto Execution": "终端命令自动执行",
        "Agent Gitignore Access": "Agent Gitignore 访问",
        "Auto-Continue": "自动继续",
        "Conversation History": "对话历史记录",
        "Knowledge": "知识库",
        "Tab to Jump": "Tab 跳转",
        "Suggestions in Editor": "编辑器中的建议",
        "Browser URL Allowlist": "浏览器 URL 允许列表",
        "Account": "账户",
        "Appearance": "外观",
        "Models": "模型",
        "Editor Settings": "编辑器设置"
    };

    function translateTextNode(node) {
        if (node.nodeType === Node.TEXT_NODE) {
            const originalText = node.nodeValue;
            let text = originalText.trim();
            if (!text) return;
            
            // 精确匹配
            if (dict[text]) {
                node.nodeValue = originalText.replace(text, dict[text]);
                return;
            }

            // 正则 / 动态拼接匹配
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
            
            // 简单的包含匹配（安全起见只处理较长的短语）
            if (text === "Conversation mode") { // Double check for inner texts
                node.nodeValue = "对话模式";
            }
        }
    }

    function walkAndTranslate(node) {
        if (!node || !node.tagName) return;
        if (node.tagName === 'SCRIPT' || node.tagName === 'STYLE') return;

        // 如果是文本节点，上面的逻辑会处理，但 walk 主要是传给 element
        node.childNodes.forEach(child => {
            if (child.nodeType === Node.TEXT_NODE) {
                translateTextNode(child);
            } else if (child.nodeType === Node.ELEMENT_NODE) {
                walkAndTranslate(child);
            }
        });
    }

    let isTranslating = false;
    const observer = new MutationObserver((mutations) => {
        if (isTranslating) return;
        isTranslating = true;
        mutations.forEach((mutation) => {
            if (mutation.type === 'childList') {
                mutation.addedNodes.forEach(node => {
                    if (node.nodeType === Node.ELEMENT_NODE) {
                        walkAndTranslate(node);
                    } else if (node.nodeType === Node.TEXT_NODE) {
                        translateTextNode(node);
                    }
                });
            } else if (mutation.type === 'characterData') {
                translateTextNode(mutation.target);
            }
        });
        isTranslating = false;
    });

    function init() {
        if (document.body) {
            walkAndTranslate(document.body);
            observer.observe(document.body, { childList: true, subtree: true, characterData: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', init);
    } else {
        init();
    }
})();
