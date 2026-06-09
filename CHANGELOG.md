# Changelog

## 1.41.2 (2026-06-07)

### ✨ 新增翻译（~170 条）
- **精准扫描补全**：通过读取实际安装文件 `workbench.desktop.main.js.bak` 原始英文内容，提取 300 个 `label` + 数百个 `children` 字符串，与现有翻译对比后精准补充
- **Settings 面板**：补充 `Strict Mode`、`Verbose agent chat`、`Enable Sounds for Agent`、`Import from VS Code/Cursor/Windsurf/Cider`、`Enable Terminal Sandbox`、`Enable Remote Control`、`Enable Overages` 等 19 条新设置项
- **对话管理**：补充 `Archive this conversation`、`Mark as Read/Unread`、`Open Conversation History`、`Copy conversation markdown` 等 10 条
- **Toggle 操作**：补充 `Toggle Developer Tools`、`Toggle Fullscreen`、`Toggle Voice Recording`、`Toggle Environment Selector` 等 6 条
- **MCP / 知识库**：补充 `MCP Servers Disabled`、`Knowledge feature is not available.`、`Manage MCP Servers` 等 8 条
- **时间分组**：补充 `Today`（今天）、`Yesterday`（昨天）、`Past Conversations`（过去的对话）
- **空状态提示**：补充 `No background tasks`、`No artifacts generated.`、`No internet. Agent features may not work.` 等 6 条
- **规则/技能/工作流**：补充 `Refresh rules/workflows/skills`、`Skills are instructions...` 等 8 条
- **通用操作按钮**：补充 `Save`、`Rename`、`Restore`、`Expand`、`Filter`、`Preview`、`Install`、`Launch` 等 30+ 条

### 📊 覆盖率提升
- 汉化覆盖率从约 **65%** 提升至约 **85%**
- `patch_zh.py` 从 1069 行扩展至 1237 行

---

## 1.41.1 (2026-06-03)


### ✨ 新增翻译
- **Settings 面板**：新增 150+ 条硬编码字符串翻译，覆盖 Agent 安全模式、插件、MCP 服务器、模型配额、外观主题、通知设置、快捷键等所有子页面
- **Chat 面板**：新增 800+ 条翻译，覆盖对话模式切换（规划/快速）、思考过程展示、产物管理器、反馈按钮、调试工具、Screen Recording 等全部交互组件
- **Workbench 主框架**：新增 120+ 条翻译，覆盖底栏策略开关（终端执行/审查/JS 执行策略）、快捷键面板、AI Shortcuts 标签、反馈表单
- 新增 `切换屏蔽 Antigravity 自动更新` 命令，支持命令面板、状态栏图标和设置面板三入口
- 新增 `v2_observer.js`（V2 DOM 监听器）和 V3 混合模式，目前插件使用静态补丁引擎（零性能损耗）

### 🔧 引擎改进
- 补丁版本控制：`PATCH_MARKER = zh-hans-patched-vN`，支持跨版本增量重打补丁
- 自动 Checksum 清除：清空 `product.json` 中的 checksums 消除"安装损坏"警告
- Windows 路径探测扩展：支持 `%LOCALAPPDATA%\Programs`、`Program Files`、`Program Files(x86)` 三种安装位置
- `patchFile()` 加入去重逻辑，防止重复规则引发链式误替换
- 修复 `isAutoUpdateBlocked()` 逻辑 Bug（移除永远为 false 的 `BLOCKED_UPDATE_URL` 分支）

---

## 1.0.0 (2026-02-08)

### 🎉 初始版本

- 支持 Antigravity 核心扩展（AI 功能、登录、导入设置等）的简体中文翻译
- 支持 Browser Launcher 浏览器启动器的简体中文翻译
- 支持 Code Executor 代码执行器的简体中文翻译
- 支持 Dev Containers 开发容器的简体中文翻译
- 支持 Remote - SSH 远程连接的简体中文翻译
- 支持 Remote - WSL 子系统连接的简体中文翻译
