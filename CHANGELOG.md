# Changelog

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
