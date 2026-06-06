# Antigravity IDE 汉化覆盖范围说明

本文档详细列出了 **AntigravityChinesePack** 对 Antigravity IDE 各项功能和模块的中文汉化覆盖范围。本语言包专为 Antigravity 独有 UI 和专属功能设计。

---

## 📦 1. NLS 标准本地化翻译

本插件通过标准扩展本地化机制（配置于 `package.json` 中的 `localizations` 贡献点），覆盖了以下内置核心扩展的 UI 元素：

| 扩展名称 / ID | 汉化覆盖模块与功能 | 翻译条目数 |
| :--- | :--- | :--- |
| **Antigravity 核心**<br>`google.antigravity` | AI 基础交互、谷歌账户登录与认证流程、设置导入/导出面板、通知提示 | 25+ |
| **内置浏览器**<br>`google.antigravity-browser-launcher` | 内置浏览器启动面板、无头浏览器环境切换交互 | 3 |
| **代码执行器**<br>`google.antigravity-code-executor` | 代码块在编辑器中直接运行的控制按钮及提示 | 1 |
| **开发容器**<br>`google.antigravity-dev-containers` | 开发容器 (Dev Containers) 创建、启动与关联配置项 | 8 |
| **远程连接 SSH**<br>`google.antigravity-remote-openssh` | 远程 SSH 连接管理、主机配置解析、身份认证交互 | 19 |
| **远程连接 WSL**<br>`google.antigravity-remote-wsl` | WSL 子系统连接生命周期管理、路径映射提示 | 17 |

---

## 🔍 2. 硬编码补丁汉化覆盖

由于以下模块的配置项和界面文本是 React/TypeScript 混合硬编码（未提取为 NLS 翻译），本插件通过**补丁引擎**对它们的目标代码进行了源码级的中文替换：

### 📁 Settings 配置项 (`out/jetskiAgent/main.js`)
覆盖了 IDE “设置”面板中所有关于 AI 助手、代码补全、浏览器和安全的特有配置，共包含 **150+ 处** 翻译：

*   **Agent 核心设置**：
    *   `Agent Auto-Fix Lints` $\rightarrow$ **Agent 自动修复 Lint**（自动感知编辑引入的错误并尝试修复）
    *   `Strict Mode` $\rightarrow$ **严格模式**（限制自主漏洞探测，所有高风险动作需要人工审核）
    *   `Review Policy` $\rightarrow$ **审查策略**（控制何时打断并请求用户审查）
    *   `Terminal Command Auto Execution` $\rightarrow$ **终端命令自动执行**
    *   `Agent Gitignore/Non-Workspace Access` $\rightarrow$ **Agent Gitignore/非工作区文件访问**
    *   `Auto-Continue` $\rightarrow$ **自动继续**（到达推理限制时自动开始下一轮调用）
    *   `Enable Sounds for Agent` $\rightarrow$ **Agent 声音提示**
    *   `Auto-Expand Changes Overview` $\rightarrow$ **自动展开更改概览**
*   **Editor 编辑器与 Tab 代码补全**：
    *   `Suggestions in Editor` $\rightarrow$ **编辑器中的建议**
    *   `Tab Speed` $\rightarrow$ **Tab 速度**（设置 Tab 键补全提示的呈现速度）
    *   `Tab to Jump` $\rightarrow$ **Tab 跳转**（预测并一键跳转到下一个建议的编辑位置）
    *   `Tab to Import` $\rightarrow$ **Tab 导入**（一键快速添加或更新依赖导入）
    *   `Highlight After Accept` $\rightarrow$ **接受后高亮**
*   **Browser 浏览器辅助**：
    *   `Enable Browser Tools` $\rightarrow$ **启用浏览器工具**（允许 Agent 访问外部 URL 和抓取网页）
    *   `Chrome Binary Path` $\rightarrow$ **Chrome 可执行文件路径**
    *   `Browser User Profile Path` $\rightarrow$ **浏览器用户配置路径**
    *   `Browser CDP Port` $\rightarrow$ **浏览器 CDP 端口**
    *   `Browser URL Allowlist` $\rightarrow$ **浏览器 URL 允许列表**

---

### 💬 Cascade 聊天面板 (`extensions/antigravity/out/media/chat.js`)
覆盖了右侧 Agent 聊天 Webview 视窗中的所有交互组件与状态，共包含 **800+ 处** 替换：

*   **对话模式切换（Conversation Mode）**：
    *   `Planning` $\rightarrow$ **规划模式**（执行前进行深度调研并输出 Implementation Plan）
    *   `Fast` $\rightarrow$ **快速直跑模式**（简单任务直接执行，不生成规划文档）
*   **思考过程展示（Thought Process）**：
    *   `Thinking for [time]` $\rightarrow$ **思考中 [时间]** / `Thought for [time]` $\rightarrow$ **思考了 [时间]**
    *   `Background Steps` $\rightarrow$ **后台步骤**
    *   `Auto-proceeded/Manually proceeded under review policy` $\rightarrow$ **已根据您的审查策略自动继续/手动继续**
*   **产物管理器（Artifacts Manager）**：
    *   `Artifacts` $\rightarrow$ **产物**
    *   描述文案 $\rightarrow$ **“产物是 Agent 在对话中创建的文件，用于帮助执行较长时间运行的任务并允许用户提供高级反馈。点击在编辑器中打开。”**
    *   表格属性：`Artifact Name` $\rightarrow$ **产物名称** / `Last Updated` $\rightarrow$ **最后更新**
*   **自定义与工作流管理**：
    *   `Customizations` $\rightarrow$ **自定义**
    *   `Rules` $\rightarrow$ **规则**（Edit rule $\rightarrow$ **编辑规则**，Refresh rules $\rightarrow$ **刷新规则**）
    *   `Workflows` $\rightarrow$ **工作流**（Edit workflow $\rightarrow$ **编辑工作流**）
    *   `MCP Servers` $\rightarrow$ **MCP 服务器**（Manage MCP Servers $\rightarrow$ **管理 MCP 服务器**）
*   **交互按钮与反馈**：
    *   `Accept all` $\rightarrow$ **全部接受** / `Discard changes` $\rightarrow$ **放弃更改**
    *   `Good response / Bad response` $\rightarrow$ **好的响应 / 差的响应**
    *   `Connect to an existing conversation` $\rightarrow$ **连接到现有对话**
    *   `Capture screenshot` $\rightarrow$ **截取屏幕** / `Capture console logs` $\rightarrow$ **捕获控制台日志**

---

### 🖥️ Workbench 主框架 (`out/vs/workbench/workbench.desktop.main.js`)
覆盖了全局应用框架相关的 AI 设置与快捷选项，共包含 **120+ 处** 替换：

*   **全局设置开关状态**：
    *   `On/Off` 枚举值 $\rightarrow$ **“开/关”**（影响全部二元开关的文本显示）
*   **底栏与面板信息**：
    *   `AI Shortcuts` $\rightarrow$ **AI 快捷键**
    *   `Advanced Settings` $\rightarrow$ **高级设置**
    *   `Terminal execution policy` $\rightarrow$ **终端执行策略**
    *   `Review policy` $\rightarrow$ **审查策略**
    *   `JavaScript execution policy` $\rightarrow$ **JavaScript 执行策略**
    *   `Always Proceed / Agent Decides / Request Review` $\rightarrow$ **始终继续 / Agent 决定 / 请求审查**
