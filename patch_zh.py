#!/usr/bin/env python3
"""
Antigravity IDE 中文汉化补丁脚本
同时修改三个关键文件：
  - jetskiAgent/main.js               → Settings 面板（Agent/Tab/Browser/Editor/Account 设置项）
  - out/media/chat.js                  → Agent 聊天面板（对话模式、Customizations、导航栏等）
  - workbench.desktop.main.js          → 快速设置面板（状态栏弹窗）

用法:
  python3 patch_zh.py          # 应用汉化
  python3 patch_zh.py --revert # 恢复原文件
"""

import shutil
import os
import sys
import json
import hashlib
import base64

def get_app_base():
    # macOS Candidates
    mac_candidates = [
        '/Applications/Antigravity.app/Contents/Resources/app',
        os.path.expanduser('~/Applications/Antigravity.app/Contents/Resources/app')
    ]
    for c in mac_candidates:
        if os.path.exists(c):
            return c

    # Windows Candidates
    localappdata = os.environ.get('LOCALAPPDATA', '')
    if localappdata:
        win_candidate = os.path.join(localappdata, 'Programs', 'Antigravity IDE', 'resources', 'app')
        if os.path.exists(win_candidate):
            return win_candidate

    return None

BASE = get_app_base()
if not BASE:
    BASE = '/Applications/Antigravity.app/Contents/Resources/app'

TARGETS = {
    'settings': os.path.join(BASE, 'out', 'jetskiAgent', 'main.js'),
    'chat': os.path.join(BASE, 'extensions', 'antigravity', 'out', 'media', 'chat.js'),
    'workbench': os.path.join(BASE, 'out', 'vs', 'workbench', 'workbench.desktop.main.js'),
}
PRODUCT_JSON = os.path.join(BASE, 'product.json')

STUBBORN_RAW_STRINGS = [
    ('"For Unix shells, an allow list entry matches a command if its space-separated tokens form a prefix of the command\'s tokens. For PowerShell, the entry tokens may match any contiguous subsequence of the command tokens."', '"对于 Unix shell，如果允许列表条目的空格分隔 token 构成了命令 token 的前缀，则该条目匹配该命令。对于 PowerShell，条目 token 可以匹配命令 token 的任何连续子序列。"'),
    ('"For Unix shells, an allow list entry matches a command if its space-separated tokens form a prefix of the command\'s tokens."', '"对于 Unix shell，如果允许列表条目的空格分隔 token 构成了命令 token 的前缀，则该条目匹配该命令。"'),
    ('"For PowerShell, the entry tokens may match any contiguous subsequence of the command tokens."', '"对于 PowerShell，条目 token 可以匹配命令 token 的任何连续子序列。"'),
    ('"When enabled, Agent can use browser tools to open URLs, read web pages, and interact with browser content. This allows the Agent access to important (and often critical) knowledge and methods of validation, but any browser integration does increase exposure to external malicious parties for security exploits."', '"启用后，Agent 可以使用浏览器工具打开 URL、读取网页并与浏览器内容交互。这允许 Agent 访问重要的（通常是关键的）知识和验证方法，但任何浏览器集成确实会增加对外部恶意方的暴露，从而带来安全风险。"'),
    ('"When enabled, Agent can use browser tools to open URLs, read web pages, and interact with browser content."', '"启用后，Agent 可以使用浏览器工具打开 URL、读取网页并与浏览器内容交互。"'),
    ('"This allows the Agent access to important (and often critical) knowledge and methods of validation, but any browser integration does increase exposure to external malicious parties for security exploits."', '"这允许 Agent 访问重要的（通常是关键的）知识和验证方法，但任何浏览器集成确实会增加对外部恶意方的暴露，从而带来安全风险。"'),
    ('"Controls whether the agent can run custom JavaScript to automate complex browser actions."', '"控制 Agent 是否可以运行自定义 JavaScript 来自动化复杂的浏览器操作。"'),
    ('"Manage your plan, credentials, and general preferences."', '"管理您的方案、凭据和常规偏好设置。"'),
    ('"When toggled on, Antigravity IDE will use your AI credits to fulfill model requests once you\'re out of model quota."', '"开启后，当您的模型配额用尽时，Antigravity IDE 将使用您的 AI 积分来完成模型请求。"'),
    ('"Antigravity IDE will always use your model quota first before using AI credits."', '"Antigravity IDE 将始终优先使用您的模型配额，然后再使用 AI 积分。"'),
    ('"Controls whether terminal commands require your approval before running."', '"控制终端命令在运行前是否需要您的批准。"'),
    ('"Note: A change to this setting will only apply to new messages sent to Agent. In-progress responses will use the previous setting value."', '"注意：对此设置的更改仅适用于发送给 Agent 的新消息。正在进行的响应将使用以前的设置值。"'),
    ('"When toggled on, Antigravity IDE will use your AI credits to fulfill model requests once you\'re out of model quota. Antigravity IDE will always use your model quota first before using AI credits."', '"开启后，当您的模型配额用尽时，Antigravity IDE 将使用您的 AI 积分来完成模型请求。Antigravity IDE 将始终优先使用您的模型配额，然后再使用 AI 积分。"'),
    ('"Configure default behaviors, skills, and MCP servers."', '"配置默认行为、技能和 MCP 服务器。"'),
    ('"Token Usage"', '"Token 使用量"'),
    ('"The breakdown below shows token usage from customizations like skills, rules, and MCP. If the budget is exceeded, large customizations will be truncated automatically."', '"下方细分显示了来自技能、规则和 MCP 等自定义项的 Token 使用情况。如果超出预算，大型自定义项将被自动截断。"'),
    ('"Keyboard shortcuts for quick navigation and control."', '"用于快速导航和控制的键盘快捷键。"'),
    ('"Recommended"', '"推荐"'),
    ('"Open Conversation Picker"', '"打开对话选择器"'),
    ('"Open File Search"', '"打开文件搜索"'),
    ('"Focus Input"', '"聚焦输入框"'),
    ('"New Conversation"', '"新建对话"'),
    ('"Open Workspace Selector"', '"打开工作区选择器"'),
    ('"Navigation"', '"导航"'),
    ('"Go Back"', '"后退"'),
    ('"Go Forward"', '"前进"'),
    ('"File Picker"', '"文件选择器"'),
    ('"Toggle Editor"', '"切换编辑器"'),
    ('"Select Previous Conversation"', '"选择上一个对话"'),
    ('"Select Next Conversation"', '"选择下一个对话"'),
    ('"Open Settings"', '"打开设置"'),
    ('"Conversation"', '"对话"'),
    ('"Toggle Model Selector"', '"切换模型选择器"'),
    ('"Start Voice Recording"', '"开始语音录制"'),
    ('"Stop Voice Recording"', '"停止语音录制"'),
    ('"Find in Pane"', '"在窗格中查找"'),
    ('"Layout Controls"', '"布局控制"'),
    ('"Toggle Sidebar"', '"切换侧边栏"'),
    ('"Toggle Auxiliary Pane"', '"切换辅助窗格"'),
    ('"Toggle Terminal"', '"切换终端"'),
    ('"Zoom In"', '"放大"'),
    ('"Zoom Out"', '"缩小"'),
    ('"Reset Zoom"', '"重置缩放"'),
    ('"Agent never asks for confirmation before executing terminal commands (except those in the Deny list). This provides the Agent with the maximum ability to operate over long periods without intervention, but also has the highest risk of an Agent executing an unsafe terminal command."', '"Agent 从不请求确认前执行终端命令（拒绝列表除外）。这为 Agent 提供了最大能力，但也具有最高风险。"'),
    ('"Proceed In Sandbox"', '"在沙盒中继续"'),
    ('"Terminal command automatically proceeds if the command runs inside the sandbox. Otherwise, it requests review."', '"如果命令在沙盒内运行，则自动继续。否则，请求审查。"'),
    ('"Agent always asks for confirmation before executing terminal commands (except those in the Allow list)."', '"Agent 始终请求确认前执行终端命令（允许列表除外）。"'),
]

def get_settings_replacements():
    """Settings 面板 (jetskiAgent/main.js) 的替换对"""
    return [
        # === Agent Screen ===
        ('label:"Agent Auto-Fix Lints",description:"When enabled, Agent is given awareness of lint errors created by its edits and may fix them without explicit user prompt',
         'label:"Agent 自动修复 Lint",description:"启用后，Agent 会自动感知其编辑产生的 lint 错误，并可在无需用户明确提示的情况下修复它们'),
        ('label:"Strict Mode",description:"When enabled, enforces settings that prevent the agent from autonomously running targeted exploits and requires human review for all agent actions. Visit antigravity.google/docs/strict-mode for details.',
         'label:"严格模式",description:"启用后，将强制执行防止 Agent 自动运行目标漏洞利用的设置，并要求人工审核所有 Agent 操作。详见 antigravity.google/docs/strict-mode。'),
        ('label:"Review Policy",description:', 'label:"审查策略",description:'),
        ('label:"Terminal Command Auto Execution",description:', 'label:"终端命令自动执行",description:'),
        ('label:"Agent Gitignore Access",description:"Allow Agent to view and edit the files in .gitignore automatically. Use with caution if your .gitignore lists files cont',
         'label:"Agent Gitignore 访问",description:"允许 Agent 自动查看和编辑 .gitignore 中的文件。如果 .gitignore 中包含敏感凭据文件请谨慎使用'),
        ('label:"Agent Non-Workspace File Access",description:"Allow Agent to view and edit files outside of the current workspace automatically. Use with caution: this provides the A',
         'label:"Agent 非工作区文件访问",description:"允许 Agent 自动查看和编辑当前工作区之外的文件。请谨慎使用：这为 A'),
        ('label:"Auto-Continue",description:"When enabled, Agent will automatically continue its response when it reaches its per-response invocation limit.',
         'label:"自动继续",description:"启用后，当 Agent 达到每次响应的调用限制时，将自动继续其响应。'),
        ('label:"Enable Sounds for Agent",description:"When enabled, Antigravity will play a sound when Agent finishes generating a response.',
         'label:"Agent 声音提示",description:"启用后，Antigravity 会在 Agent 完成响应生成时播放声音。'),
        ('label:"Auto-Expand Changes Overview",description:"When enabled, the Changes Overview toolbar will automatically expand when Agent finishes generating a response.',
         'label:"自动展开更改概览",description:"启用后，当 Agent 完成响应生成时，更改概览工具栏将自动展开。'),
        ('label:"Conversation History",description:"When enabled, the agent will be able to access past conversations to inform its responses.',
         'label:"对话历史",description:"启用后，Agent 将能够访问过去的对话来辅助其响应。'),
        ('label:"Knowledge",description:"When enabled, the agent will be able to access its knowledge base to inform its responses and automatically generate kno',
         'label:"知识库",description:"启用后，Agent 将能够访问其知识库来辅助其响应并自动生成知'),
        ('label:"Auto-Open Edited Files",description:"Open files in the background if Agent creates or edits them"',
         'label:"自动打开已编辑文件",description:"当 Agent 创建或编辑文件时在后台打开它们"'),
        ('label:"Open Agent on Reload",description:"Open Agent panel on window reload"',
         'label:"重新加载时打开 Agent",description:"窗口重新加载时打开 Agent 面板"'),
        ('label:"Enable Terminal Sandbox",description:', 'label:"启用终端沙盒",description:'),
        ('label:"Sandbox Allow Network",description:', 'label:"沙盒允许网络",description:'),
        # === Editor Screen ===
        ('label:"Suggestions in Editor",description:"Show suggestions when typing in the editor"',
         'label:"编辑器中的建议",description:"在编辑器中输入时显示建议"'),
        ('label:"Show Selection Actions",description:', 'label:"显示选中操作",description:'),
        # === Tab Screen ===
        ('label:"Tab Speed",description:"Set the speed of tab suggestions"', 'label:"Tab 速度",description:"设置 Tab 建议的速度"'),
        ('label:"Tab to Jump",description:"Predict the location of your next edit and navigates you there with a tab keypress.',
         'label:"Tab 跳转",description:"预测下一个编辑位置，按 Tab 键即可跳转到该位置。'),
        ('label:"Tab to Import",description:"Quickly add and update imports with a tab keypress.',
         'label:"Tab 导入",description:"按 Tab 键快速添加和更新导入语句。'),
        ('label:"Highlight After Accept",description:"Highlight newly inserted text after accepting a Tab completion.',
         'label:"接受后高亮",description:"接受 Tab 补全后高亮新插入的文本。'),
        ('label:"Tab Gitignore Access",description:"Allow Tab to view and edit the files in .gitignore. Use with caution if your .gitignore lists files containing credentia',
         'label:"Tab Gitignore 访问",description:"允许 Tab 查看和编辑 .gitignore 中的文件。如果 .gitignore 中包含敏感凭据文件请谨慎使用'),
        # === Browser Screen ===
        # (Browser Tools truncated string removed to prevent partial matches)
        ('label:"Browser Javascript Execution Policy",description:', 'label:"浏览器 JavaScript 执行策略",description:'),
        ('label:"Chrome Binary Path",description:"Path to the Chrome/Chromium executable. Leave empty for auto-detection.',
         'label:"Chrome 可执行文件路径",description:"Chrome/Chromium 可执行文件的路径。留空则自动检测。'),
        ('label:"Browser User Profile Path",description:"Custom path for the browser user profile directory. Leave empty for default (~/.gemini/antigravity-browser-profile).',
         'label:"浏览器用户配置路径",description:"浏览器用户配置文件目录的自定义路径。留空使用默认值（~/.gemini/antigravity-browser-profile）。'),
        ('label:"Browser CDP Port",description:"Port number for Chrome DevTools Protocol remote debugging. Leave empty for default (9222).',
         'label:"浏览器 CDP 端口",description:"Chrome DevTools Protocol 远程调试的端口号。留空使用默认值（9222）。'),
        ('label:"Browser URL Allowlist",description:"Control which URLs the browser can access. Add domains or full URLs to the allowlist.',
         'label:"浏览器 URL 允许列表",description:"控制浏览器可以访问的 URL。将域名或完整 URL 添加到允许列表。'),
        ('label:"Marketplace Item URL",description:', 'label:"市场扩展页面 URL",description:'),
        ('label:"Marketplace Gallery URL",description:', 'label:"市场搜索 URL",description:'),
        # === Allow/Deny List ===
        ('label:"Allow List Terminal Commands",description:"Agent auto-executes commands matched by an allow list entry.',
         'label:"终端命令允许列表",description:"Agent 自动执行与允许列表条目匹配的命令。'),
        ('label:"Deny List Terminal Commands",description:"Agent asks for permission before executing commands matched by a deny list entry.',
         'label:"终端命令拒绝列表",description:"Agent 在执行与拒绝列表条目匹配的命令之前会请求许可。'),
        # === Account Screen ===
        ('label:"Enable Telemetry",description:', 'label:"启用遥测",description:'),
        # === Review Policy Options ===
        ('{value:j0.TURBO,label:"Always Proceed",description:"Agent never asks for review. This maximizes the autonomy of the Agent, but also has the highest risk of the Agent operat',
         '{value:j0.TURBO,label:"始终继续",description:"Agent 从不请求审查。这最大化了 Agent 的自主性，但也具有 Agent 最高操作风'),
        ('{value:j0.AUTO,label:"Agent Decides",description:"Agent will decide when to ask for review based on task complexity and user preference.',
         '{value:j0.AUTO,label:"Agent 决定",description:"Agent 将根据任务复杂性和用户偏好决定何时请求审查。'),
        ('{value:j0.ALWAYS,label:"Request Review",description:"Agent always asks for review.',
         '{value:j0.ALWAYS,label:"请求审查",description:"Agent 始终请求审查。'),
        ('value:Zd.TURBO,children:"Always Proceed"', 'value:Zd.TURBO,children:"始终继续"'),
        ('value:Zd.AUTO,children:"Agent Decides"', 'value:Zd.AUTO,children:"Agent 决定"'),
        ('value:Zd.ALWAYS,children:"Request Review"', 'value:Zd.ALWAYS,children:"请求审查"'),
        # === Dev ===
        ('label:"[Dev] GCP Project ID",description:"GCP Project ID for enterprise features."',
         'label:"[开发] GCP 项目 ID",description:"企业功能的 GCP 项目 ID。"'),
        # === Settings Title (pure display JSX) ===
        ('children:["Settings - ",t]', 'children:["设置 - ",t]'),
        # === Conversation Mode (in main.js copy) ===
        ('children:"Conversation mode"', 'children:"对话模式"'),
        ('{mode:"Planning",description:"Agent can plan before executing tasks. Use for deep research, complex tasks, or collaborative work"}',
         '{mode:"Planning",description:"Agent 可以在执行任务前进行规划。适用于深度研究、复杂任务或协作工作"}'),
        ('{mode:"Fast",description:"Agent will execute tasks directly. Use for simple tasks that can be completed faster"}',
         '{mode:"Fast",description:"Agent 将直接执行任务。适用于可以更快完成的简单任务"}'),
        ('text:"Provide Feedback"', 'text:"提供反馈"'),
        # === Accept / Undo / Skip / Add / Edit / Loading ===
        ('children:"Accept"', 'children:"接受"'),
        ('children:"Accept all"', 'children:"全部接受"'),
        ('children:"Skip"', 'children:"跳过"'),
        ('children:"Add"', 'children:"添加"'),
        ('children:"Add Model"', 'children:"添加模型"'),
        ('children:"Add context"', 'children:"添加上下文"'),
        ('children:"Add them to allow future interactions"', 'children:"将它们添加到允许列表以允许未来的交互"'),
        ('children:"Edit"', 'children:"编辑"'),
        ('children:"Edit Model"', 'children:"编辑模型"'),
        ('children:"Editor"', 'children:"编辑器"'),
        ('children:"Editor Settings"', 'children:"编辑器设置"'),
        ('children:"Editor Window"', 'children:"编辑器窗口"'),
        ('children:"Loading..."', 'children:"加载中..."'),
        ('children:"Loading models..."', 'children:"正在加载模型..."'),
        ('children:"Loading Browser recording..."', 'children:"正在加载浏览器录制..."'),
        ('children:"Loading knowledge items..."', 'children:"正在加载知识项..."'),
        ('children:"Loading metrics..."', 'children:"正在加载指标..."'),
        ('label:"Undo"', 'label:"撤销"'),
        ('label:"Discard all changes"', 'label:"放弃所有更改"'),
        ('label:"Discard changes"', 'label:"放弃更改"'),
        ('label:"Run"', 'label:"运行"'),
        ('label:"Running"', 'label:"运行中"'),
        ('label:"Close"', 'label:"关闭"'),
        ('label:"Close Workspace"', 'label:"关闭工作区"'),
        ('label:"Delete Conversation"', 'label:"删除对话"'),
        ('label:"Start Conversation"', 'label:"开始对话"'),
        ('label:"Open Workspace"', 'label:"打开工作区"'),
        ('label:"Open New Workspace"', 'label:"打开新工作区"'),
        ('label:"Open New Remote Workspace"', 'label:"打开新远程工作区"'),
        # === v1.107.0 Settings updates ===
        ('{value:e0.TURBO,label:"Always Proceed",description:"Agent never asks for review. This maximizes the autonomy of the Agent, but also has the highest risk of the Agent operating over unsafe or injected Artifact content.",disabledInSecureMode:!0}',
         '{value:e0.TURBO,label:"始终继续",description:"Agent 从不请求审查。这最大化了 Agent 的自主性，但也具有 Agent 操作不安全或注入的 Artifact 内容的最高风险。",disabledInSecureMode:!0}'),
        ('{value:e0.ALWAYS,label:"Always Ask",description:"Agent always asks for review.",disabledInSecureMode:!1}',
         '{value:e0.ALWAYS,label:"总是询问",description:"Agent 总是请求审查。",disabledInSecureMode:!1}'),
        ('children:["Settings - ",e]', 'children:["设置 - ",e]'),
        ('"aria-label":"Add context"', '"aria-label":"添加上下文"'),
        ('tooltipText:"Edit Model"', 'tooltipText:"编辑模型"'),
        # === Remaining settings translations ===
        ('children:["Select one of the ",t?"two":"three"," options. Agent settings and permissions can be further customized below."',
         'children:["从",t?"两个":"三个","个选项中选择一个。Agent 设置和权限可在下方进一步自定义。"'),
        ('children:"Agent security mode"', 'children:"Agent 安全模式"'),
        ('children:"Full access"', 'children:"完全访问"'),
        ('children:"Agents have full access to your machine and external resources."', 'children:"Agent 可以完全访问您的计算机和外部资源。"'),
        ('children:"Sandboxed"', 'children:"沙盒化"'),
        ('children:"Agents run in a secure sandbox that restricts access to external resources outside of your trusted folders."', 'children:"Agent 运行在安全的沙盒中，限制访问信任文件夹以外的外部资源。"'),
        ('children:"Strict"', 'children:"严格"'),
        ('children:"Terminal commands always require review and the agent cannot access files outside of its given workspaces."', 'children:"终端命令始终需要审查，且 Agent 无法访问指定工作区以外的文件。"'),
        ('require your approval before running.\\n\\nNote: A change to this setting will only apply to new messages sent to Agent. In-progress responses will use the previous setting value.',
         '在运行前需要您的批准。\\n\\n注意：对此设置的更改仅适用于发送给 Agent 的新消息。正在进行的响应将使用以前的设置值。'),
        ('label:"Enable Shell Integration"', 'label:"启用 Shell 集成"'),
        ('description:"When enabled, Agent will use IDE\'s shell integration to detect and report terminal command execution."',
         'description:"启用后，Agent 将使用 IDE 的 Shell 集成来检测并报告终端命令的执行。"'),
        ('children:"File Access"', 'children:"文件访问"'),
        ('description:"Allows the agent to access files outside of your current workspace."',
         'description:"允许 Agent 访问当前工作区以外的文件。"'),
        ('children:"Planning"', 'children:"规划"'),
        ('description:"Specifies Agent\'s behavior when asking for review on artifacts, which are documents it creates to enable a richer conversation experience."',
         'description:"指定 Agent 在请求审查 Artifact（即为了提供更丰富的对话体验而创建的文档）时的行为。"'),
        ('children:"Automation"', 'children:"自动化"'),
        ('children:"History"', 'children:"历史记录"'),
        ('children:"General"', 'children:"常规"'),
        ('label:"Explain and Fix in Current Conversation"', 'label:"在当前对话中解释和修复"'),
        ('description:"When enabled, \'Explain and Fix\' actions will continue in the current conversation instead of starting a new one."',
         'description:"启用后，“解释并修复”操作将在当前对话中继续，而不是开始新对话。"'),
        ('children:"Advanced"', 'children:"高级"'),
        ('children:"Advanced File Access"', 'children:"高级文件访问"'),
        ('label:"Read Files",description:"Paths the agent can read."', 'label:"读取文件",description:"Agent 可以读取的路径。"'),
        ('label:"Read Files",description:"Paths the agent can read inside this workspace."', 'label:"读取文件",description:"Agent 在此工作区中可以读取的路径。"'),
        ('label:"Write Files",description:"Paths the agent can modify."', 'label:"写入文件",description:"Agent 可以修改的路径。"'),
        ('label:"Write Files",description:"Paths the agent can modify inside this workspace."', 'label:"写入文件",description:"Agent 在此工作区中可以修改的路径。"'),
        ('children:"Advanced Command Access"', 'children:"高级命令访问"'),
        ('label:"Terminal Commands",description:"Terminal commands the agent can execute."', 'label:"终端命令",description:"Agent 可以执行的终端命令。"'),
        ('label:"Terminal Commands",description:"Terminal commands the agent can execute in this workspace."', 'label:"终端命令",description:"Agent 在此工作区中可以执行的终端命令。"'),
        ('label:"Commands Outside Sandbox",description:"Allow/deny agent command execution outside the sandbox."',
         'label:"沙盒外的命令",description:"允许/拒绝 Agent 在沙盒外执行命令。"'),
        ('label:"Commands Outside Sandbox",description:"Commands the agent can run outside the sandbox."',
         'label:"沙盒外的命令",description:"Agent 可以在沙盒外运行的命令。"'),
        ('label:"Commands Outside Sandbox",description:"Commands the agent can run outside the sandbox in this workspace."',
         'label:"沙盒外的命令",description:"Agent 在此工作区的沙盒外可以运行的命令。"'),
        ('label:"MCP Tools",description:"Configure external tools via Model Context Protocol."',
         'label:"MCP 工具",description:"通过 Model Context Protocol 配置外部工具。"'),
        ('label:"MCP Tools",description:"External tools the agent can call via Model Context Protocol."',
         'label:"MCP 工具",description:"Agent 可通过 Model Context Protocol 调用的外部工具。"'),
        ('children:"Advanced Web Access"', 'children:"高级网络访问"'),
        ('label:"Read URLs",description:"Allow/deny agent read access to specific URLs or domains."',
         'label:"读取 URL",description:"允许/拒绝 Agent 对特定 URL 或域名的读取访问。"'),
        ('label:"Read URLs",description:"URLs the agent can read or open in the browser."',
         'label:"读取 URL",description:"Agent 可以在浏览器中读取或打开的 URL。"'),
        ('label:"Read URLs",description:"URLs the agent can read or open in this workspace."',
         'label:"读取 URL",description:"Agent 在此工作区中可以读取或打开的 URL。"'),
        ('label:"Execute URLs",description:"URLs the agent can actuate on using the browser."',
         'label:"执行 URL",description:"Agent 可以使用浏览器操作 the URL。"'),
        ('label:"Execute URLs",description:"Allow/deny agent browser actuation access to specific URLs."',
         'label:"执行 URL",description:"允许/拒绝 Agent 对特定 URL 的浏览器操作访问。"'),
        ('label:"Execute URLs",description:"URLs the agent can actuate on in this workspace."',
         'label:"执行 URL",description:"Agent 在此工作区中可以操作的 URL。"'),
        ('label:t="Advanced Settings"', 'label:t="高级设置"'),
        ('label:"Enable Demo Mode (Beta)"', 'label:"启用演示模式 (Beta)"'),
        ('description:\'When enabled, your UI will be slightly modified to ensure more consistent demos. This is only recommended for demo purposes. In most cases, you can run "Antigravity: Start Demo Mode" and "Antigravity: Stop Demo Mode" to control this switch and update your ~/.gemini/antigravity data directory.\'',
         'description:\'启用后，您的 UI 将被稍微修改以确保演示的一致性。仅建议用于演示目的。在大多数情况下，您可以运行 "Antigravity: Start Demo Mode" 和 "Antigravity: Stop Demo Mode" 来控制此开关并更新您的 ~/.gemini/antigravity 数据目录。\''),
        ('description:`When toggled on, ${r.product.nameShort} collects usage data to help Google enhance performance and features.`',
         'description:`开启后，${r.product.nameShort} 将收集使用数据，以帮助 Google 提升性能和功能。`'),
        ('label:"Marketing Emails",description:`Receive product updates, tips, and promotions from Google ${r.product.nameShort} via email.`',
         'label:"营销邮件",description:`通过电子邮件接收来自 Google ${r.product.nameShort} 的产品更新、提示和促销信息。`'),
        ('children:["By using this app, you agree to its",', 'children:["使用此应用即表示您同意其",'),
        ('className:"text-primary hover:underline",children:"Terms of Service"', 'className:"text-primary hover:underline",children:"服务条款"'),
        ('className:"text-lg font-medium mb-4",children:"Terms of Service & Data Use"', 'className:"text-lg font-medium mb-4",children:"服务条款与数据使用"'),
        ('description:p(jt,{children:["Configure the browser subagent. It requires",', 'description:p(jt,{children:["配置浏览器子 Agent。它需要安装",'),
        ('`Refreshes in ${n} day${n>1?"s":""}, ${a} hour${a>1?"s":""}`', '`将在 ${n} 天 ${a} 小时后刷新`'),
        ('`Refreshes in ${a} hour${a>1?"s":""}, ${i} minute${i>1?"s":""}`', '`将在 ${a} 小时 ${i} 分钟后刷新`'),
        ('`Refreshes in ${i} minute${i>1?"s":""}`', '`将在 ${i} 分钟后刷新`'),
        ('description:"View your available model quota. Quota refreshes periodically based on your plan."',
         'description:"查看您可用的模型配额。配额会根据您的方案定期刷新。"'),
        ('"% of the customization budget is available."', '"% 的定制预算当前可用。"'),
        ('children:V?"Hide breakdown":`Show ${I.length} breakdown${I.length===1?"":"s"}`',
         'children:V?"隐藏明细":`显示 ${I.length} 项明细`'),
        ('"Plugin: "', '"插件: "'),
        ('children:["Plugins are packaged collections of skills and MCPs to help the Agent"," ",a?`in ${a} `:"","work with Google developer products. You can always change your choices in Settings."]',
         'children:["插件是技能和 MCP 的打包集合，用于帮助 Agent"," ",a?`在 ${a} `:"","中协同谷歌开发产品工作。您随时可以在设置中更改您的选择。"]'),
        ('children:["Plugins are packaged collections of skills and MCPs to help the Agent in ",e," work with Google developer products. You can always change your choices in Settings."]',
         'children:["插件是技能和 MCP 的打包集合，用于帮助 Agent 在 ",e," 中协同谷歌开发产品工作。您随时可以在设置中更改您的选择。"]'),
        ('children:"No MCP Servers"', 'children:"没有 MCP 服务器"'),
        ('children:"You currently don\'t have any MCP Servers installed. Add an MCP server above or add a custom one via the MCP Config."',
         'children:"您当前未安装任何 MCP 服务器。请在上方添加 MCP 服务器，或通过 MCP 配置添加自定义服务器。"'),
        ('label:"Account",description:"Manage your plan, credentials, and general preferences."',
         'label:"账户",description:"管理您的方案、凭据和常规偏好设置。"'),
        ('label:"Appearance",description:"Configure the agent\'s visual theme and display preferences."',
         'label:"外观",description:"配置 Agent 的视觉主题和显示偏好设置。"'),
        ('label:"Notifications",description:"Manage your notification preferences."',
         'label:"通知",description:"管理您的通知偏好设置。"'),
        ('label:"Models",description:"Configure AI models and view your quota."',
         'label:"模型",description:"配置 AI 模型并查看您的配额。"'),
        ('label:"Customizations",description:"Configure default behaviors, skills, and MCP servers."',
         'label:"自定义",description:"配置默认行为、技能和 MCP 服务器。"'),
        ('label:"Browser Settings",description:"Configure the browser subagent. It requires Google Chrome to be installed."',
         'label:"浏览器设置",description:"配置浏览器子 Agent。它需要安装 Google Chrome。"'),
        ('label:"Editor Settings",description:"Configure editor-specific behaviors and shortcuts."',
         'label:"编辑器设置",description:"配置编辑器特定的行为和快捷键。"'),
        ('children:"Account & Plan"', 'children:"账户与方案"'),
        ('label:"Email",description:a?"Peter Pan":n.email', 'label:"电子邮件",description:a?"Peter Pan":n.email'),
        ('children:"Theme"', 'children:"主题"'),
        ('children:"Chat Settings"', 'children:"聊天设置"'),
        ('label:"Verbose agent chat",description:"Display and preserve intermediate thinking steps"',
         'label:"详细 Agent 聊天",description:"显示并保留中间思考步骤"'),
        ('label:"Notification Settings",description:"To modify notification settings, open your operating system\'s system preferences."',
         'label:"通知设置",description:"要修改通知设置，请打开您操作系统的系统偏好设置。"'),
        ('label:"Model Quota"', 'label:"模型配额"'),
        ('children:"Actuation Permissions"', 'children:"执行操作权限"'),
        ('label:"Browser Actuation Rules",description:"Configure allowed and denied URLs for browser actuation."',
         'label:"浏览器执行规则",description:"配置允许和拒绝的浏览器执行 URL。"'),
        ('children:"Marketplace"', 'children:"市场"'),
        ('description:"Changes the base URL on each extension page. You must restart Antigravity IDE to use the new marketplace after changing this value."',
         'description:"更改每个扩展页面的基础 URL。更改此值后，您必须重启 Antigravity IDE 才能使用新的市场。"'),
        ('description:"Changes the base URL for marketplace search results. You must restart Antigravity IDE to use the new marketplace after changing this value."',
         'description:"更改市场搜索结果的基础 URL。更改此值后，您必须重启 Antigravity IDE 才能使用新的市场。"'),
        ('children:"Selection Actions"', 'children:"选中操作"'),
        ('label:"Editor Settings",description:"To modify editor settings, open Settings within the editor window."',
         'label:"编辑器设置",description:"要修改编辑器设置，请在编辑器窗口中打开设置。"'),
         
        # --- Sidebar ---
        ('children:"Account"', 'children:"账户"'),
        ('children:"Permissions"', 'children:"权限"'),
        ('children:"Appearance"', 'children:"外观"'),
        ('children:"Notifications"', 'children:"通知"'),
        ('children:"Models"', 'children:"模型"'),
        ('children:"Customizations"', 'children:"自定义"'),
        ('children:"Browser"', 'children:"浏览器"'),
        ('children:"Tab"', 'children:"Tab"'),
        ('children:"Editor"', 'children:"编辑器"'),
        ('children:"Workspaces"', 'children:"工作区"'),
        ('children:"Shortcuts"', 'children:"快捷键"'),

        # --- Terminal Settings ---
        ('children:"Controls whether terminal commands require your approval before running."', 'children:"控制终端命令在运行前是否需要您的批准。"'),
        ('description:"Controls whether terminal commands require your approval before running."', 'description:"控制终端命令在运行前是否需要您的批准。"'),
        ('"Note: A change to this setting will only apply to new messages sent to Agent. In-progress responses will use the previous setting value."', '"注意：对此设置的更改仅适用于发送给 Agent 的新消息。正在进行的响应将使用以前的设置值。"'),
        
        # --- Appearance Settings ---
        ('children:"Configure the agent\'s visual theme and display preferences."', 'children:"配置 Agent 的视觉主题和显示偏好设置。"'),
        ('description:"Configure the agent\'s visual theme and display preferences."', 'description:"配置 Agent 的视觉主题和显示偏好设置。"'),
        
        # --- Notifications Settings ---
        ('children:"Manage your notification preferences."', 'children:"管理您的通知偏好设置。"'),
        ('description:"Manage your notification preferences."', 'description:"管理您的通知偏好设置。"'),
        ('children:"Notification Settings"', 'children:"通知设置"'),
        ('children:"To modify notification settings, open your operating system\'s system preferences."', 'children:"要修改通知设置，请打开您操作系统的系统偏好设置。"'),
        ('children:"Open System Preferences"', 'children:"打开系统偏好设置"'),
        
        # --- Models Settings ---
        ('children:"Configure AI models and view your quota."', 'children:"配置 AI 模型并查看您的配额。"'),
        ('description:"Configure AI models and view your quota."', 'description:"配置 AI 模型并查看您的配额。"'),
        ('children:"Model Credits"', 'children:"模型积分"'),
        ('children:"Enable AI Credit Overages"', 'children:"启用 AI 积分超额使用"'),
        ('children:"When toggled on, Antigravity IDE will use your AI credits to fulfill model requests once you\'re out of model quota. Antigravity IDE will always use your model quota first before using AI credits."', 'children:"开启后，当您的模型配额用尽时，Antigravity IDE 将使用您的 AI 积分来完成模型请求。Antigravity IDE 将始终优先使用您的模型配额，然后再使用 AI 积分。"'),
        ('children:"Available AI Credits: "', 'children:"可用 AI 积分: "'),
        ('"Available AI Credits: "', '"可用 AI 积分: "'),
        ('children:"See Activity"', 'children:"查看活动"'),
        ('children:"Get More AI Credits"', 'children:"获取更多 AI 积分"'),
        ('children:"Model Quota"', 'children:"模型配额"'),
        ('children:"Refresh"', 'children:"刷新"'),
        
        # --- General Settings Dropdowns ---
        ('children:"Request Review"', 'children:"请求审查"'),
        ('children:"Agent Decides"', 'children:"Agent 决定"'),
        ('children:"Always Proceed"', 'children:"始终继续"'),
        
        # --- Raw Strings Fallback ---
        ('"Account"', '"账户"'),
        ('"Permissions"', '"权限"'),
        ('"Appearance"', '"外观"'),
        ('"Notifications"', '"通知"'),
        ('"Models"', '"模型"'),
        ('"Customizations"', '"自定义"'),
        ('"Browser"', '"浏览器"'),
        ('"Tab"', '"Tab"'),
        ('"Editor"', '"编辑器"'),
        ('"Workspaces"', '"工作区"'),
        ('"Shortcuts"', '"快捷键"'),
        ('"Controls whether terminal commands require your approval before running."', '"控制终端命令在运行前是否需要您的批准。"'),
        ('"Configure the agent\'s visual theme and display preferences."', '"配置 Agent 的视觉主题和显示偏好设置。"'),
        ('"Manage your notification preferences."', '"管理您的通知偏好设置。"'),
        ('"Notification Settings"', '"通知设置"'),
        ('"To modify notification settings, open your operating system\'s system preferences."', '"要修改通知设置，请打开您操作系统的系统偏好设置。"'),
        ('"Open System Preferences"', '"打开系统偏好设置"'),
        ('"Configure AI models and view your quota."', '"配置 AI 模型并查看您的配额。"'),
        ('"Model Credits"', '"模型积分"'),
        ('"Enable AI Credit Overages"', '"启用 AI 积分超额使用"'),
        ('"When toggled on, Antigravity IDE will use your AI credits to fulfill model requests once you\'re out of model quota. Antigravity IDE will always use your model quota first before using AI credits."', '"开启后，当您的模型配额用尽时，Antigravity IDE 将使用您的 AI 积分来完成模型请求。Antigravity IDE 将始终优先使用您的模型配额，然后再使用 AI 积分。"'),
        ('"Available AI Credits: "', '"可用 AI 积分: "'),
        ('"See Activity"', '"查看活动"'),
        ('"Get More AI Credits"', '"获取更多 AI 积分"'),
        ('"Model Quota"', '"模型配额"'),
        ('"Refresh"', '"刷新"'),
        ('"Request Review"', '"请求审查"'),
        ('"Agent Decides"', '"Agent 决定"'),
        ('"Always Proceed"', '"始终继续"'),
    ] + STUBBORN_RAW_STRINGS


def get_chat_replacements():
    """Agent 聊天面板 (chat.js) 的替换对 - 全面覆盖"""
    return [
        # ============================================================
        # 1. Conversation Mode Dropdown
        # ============================================================
        ('children:"Conversation mode"', 'children:"对话模式"'),
        ('{mode:"Planning",description:"Agent can plan before executing tasks. Use for deep research, complex tasks, or collaborative work"}',
         '{mode:"Planning",description:"Agent 可以在执行任务前进行规划。适用于深度研究、复杂任务或协作工作"}'),
        ('{mode:"Fast",description:"Agent will execute tasks directly. Use for simple tasks that can be completed faster"}',
         '{mode:"Fast",description:"Agent 将直接执行任务。适用于可以更快完成的简单任务"}'),

        # ============================================================
        # 2. Customizations / Rules / Workflows Page
        # ============================================================
        ('children:"Customizations"', 'children:"自定义"'),
        ('Customize Agent to get a better, more personalized experience.',
         '自定义 Agent 以获得更好、更个性化的体验。'),
        ('label:"Customizations"', 'label:"自定义"'),
        ('label:"MCP Servers"', 'label:"MCP 服务器"'),
        ('children:"Manage MCP Servers"', 'children:"管理 MCP 服务器"'),
        ('children:"Rules"', 'children:"规则"'),
        ('children:"Workflows"', 'children:"工作流"'),
        ('children:"Rules help guide the behavior of Agent."', 'children:"规则可以帮助引导 Agent 的行为。"'),
        ('children:"Edit rule"', 'children:"编辑规则"'),
        ('children:"Edit workflow"', 'children:"编辑工作流"'),
        ('children:"Refresh rules"', 'children:"刷新规则"'),
        ('children:"Refresh workflows"', 'children:"刷新工作流"'),
        ('label:"Rules"', 'label:"规则"'),
        ('label:"Workflows"', 'label:"工作流"'),
        ('label:"Mentions"', 'label:"提及"'),
        ('label:"Screen Recording"', 'label:"屏幕录制"'),

        # ============================================================
        # 3. Back / Navigation
        # ============================================================
        ('"Back to Agent"', '"返回 Agent"'),
        ('children:"Close Agent View"', 'children:"关闭 Agent 视图"'),
        ('children:"Past Conversations"', 'children:"历史对话"'),
        ('children:"History"', 'children:"历史记录"'),
        ('children:"Delete Conversation"', 'children:"删除对话"'),
        ('children:"Connect to an existing conversation"', 'children:"连接到现有对话"'),

        # ============================================================
        # 4. Common Buttons / Actions
        # ============================================================
        ('children:"Cancel"', 'children:"取消"'),
        ('children:"Cancel command"', 'children:"取消命令"'),
        ('children:"Cancel step"', 'children:"取消步骤"'),
        ('children:"Confirm"', 'children:"确认"'),
        ('children:"Confirm Undo"', 'children:"确认撤销"'),
        ('children:"Close"', 'children:"关闭"'),
        ('children:"Create"', 'children:"创建"'),
        ('children:"Delete"', 'children:"删除"'),
        ('children:"Dismiss"', 'children:"忽略"'),
        ('children:"Expand"', 'children:"展开"'),
        ('children:"Install"', 'children:"安装"'),
        ('children:"Launch"', 'children:"启动"'),
        ('children:"Open"', 'children:"打开"'),
        ('children:"Preview"', 'children:"预览"'),
        ('children:"Refresh"', 'children:"刷新"'),
        ('children:"Retry"', 'children:"重试"'),
        ('children:"Review"', 'children:"审查"'),
        ('children:"Review Changes"', 'children:"审查更改"'),
        ('children:"Save"', 'children:"保存"'),
        ('children:"Send"', 'children:"发送"'),
        ('children:"Send Feedback"', 'children:"发送反馈"'),
        ('children:"See all"', 'children:"查看全部"'),
        ('children:"Show more"', 'children:"显示更多"'),
        ('children:"Continue response"', 'children:"继续响应"'),
        ('children:"Configure"', 'children:"配置"'),
        ('children:"Configure Auto-Continue"', 'children:"配置自动继续"'),
        ('children:"Next"', 'children:"下一步"'),
        ('children:"Previous"', 'children:"上一步"'),
        ('children:"Reload IDE"', 'children:"重新加载 IDE"'),
        ('children:"Clear"', 'children:"清除"'),
        ('children:"Setup"', 'children:"设置"'),
        ('children:"New"', 'children:"新建"'),
        ('children:"Default"', 'children:"默认"'),
        ('children:"Custom"', 'children:"自定义"'),
        ('children:"Copy command"', 'children:"复制命令"'),
        ('children:"Copy diff"', 'children:"复制差异"'),
        ('children:"Copy the trajectory ID"', 'children:"复制轨迹 ID"'),
        ('children:"Open diff"', 'children:"打开差异"'),
        ('children:"Open in New Window"', 'children:"在新窗口中打开"'),
        ('children:"Open allowlist"', 'children:"打开允许列表"'),
        ('children:"Start Screen Recording"', 'children:"开始屏幕录制"'),
        ('children:"Set Browser Config"', 'children:"设置浏览器配置"'),
        ('children:"View Diff"', 'children:"查看差异"'),
        ('children:"View Page"', 'children:"查看页面"'),
        ('children:"View network request"', 'children:"查看网络请求"'),
        ('children:"View network requests"', 'children:"查看网络请求"'),
        ('children:"View plans"', 'children:"查看计划"'),
        ('children:"View Annotation"', 'children:"查看注释"'),
        ('children:"View Created Links"', 'children:"查看已创建链接"'),
        ('children:"View snapshot"', 'children:"查看快照"'),

        # ============================================================
        # 5. Status / State Messages
        # ============================================================
        ('"Thinking for "', '"思考中 "'),
        ('"Thought for "', '"思考了 "'),
        ('"Changes Overview"', '"更改概览"'),
        ('"Terminal ("', '"终端 ("'),
        ('children:"Thinking"', 'children:"思考中"'),
        ('children:"Analyzed"', 'children:"已分析"'),
        ('children:"Installed"', 'children:"已安装"'),
        ('children:"Error"', 'children:"错误"'),
        ('children:"Something went wrong"', 'children:"出了点问题"'),
        ('children:"An error was thrown."', 'children:"发生了一个错误。"'),
        ('children:"Failed to send"', 'children:"发送失败"'),
        ('children:"Launching the browser..."', 'children:"正在启动浏览器..."'),
        ('children:"Playback available"', 'children:"可以回放"'),
        ('children:"Preview unavailable"', 'children:"预览不可用"'),
        ('children:"No matching results"', 'children:"没有匹配的结果"'),
        ('children:"No results"', 'children:"无结果"'),
        ('children:"No results found"', 'children:"未找到结果"'),
        ('children:"No results found."', 'children:"未找到结果。"'),
        ('children:"No browser pages open"', 'children:"没有打开的浏览器页面"'),
        ('children:"Loading MCP servers"', 'children:"正在加载 MCP 服务器"'),
        ('children:"Loading models..."', 'children:"正在加载模型..."'),
        ('children:"Reconnecting to remote authority."', 'children:"正在重新连接到远程服务器。"'),
        ('children:"Disabled in strict mode"', 'children:"在严格模式下已禁用"'),
        ('children:"Full output written to"', 'children:"完整输出已写入"'),
        ('children:"Read URL rejected"', 'children:"读取 URL 被拒绝"'),
        ('children:"Rejected MCP tool"', 'children:"已拒绝 MCP 工具"'),
        ('children:"Proceeded with"', 'children:"已继续执行"'),
        ('children:"Unknown edit"', 'children:"未知编辑"'),
        ('children:"Unknown file edit"', 'children:"未知文件编辑"'),
        ('children:"Built-In"', 'children:"内置"'),

        # ============================================================
        # 6. Prompts / Confirmation Messages
        # ============================================================
        ('children:"Authentication Required"', 'children:"需要身份验证"'),
        ('children:"Confirmation required to execute this step"', 'children:"执行此步骤需要确认"'),
        ('children:"Antigravity would like to use the browser."', 'children:"Antigravity 希望使用浏览器。"'),
        ('children:"The Agent attempted to interact with some sites that are not allowlisted"',
         'children:"Agent 尝试与一些不在允许列表中的网站交互"'),
        ('children:"The agent was prevented from accessing some sites"',
         'children:"Agent 已被阻止访问某些网站"'),
        ('children:"The agent will wait for you to install the browser extension."',
         'children:"Agent 将等待你安装浏览器扩展。"'),
        ('children:"This plugin has been built by a verified reference publisher."',
         'children:"此插件由经过验证的参考发布者构建。"'),
        ('children:"This plugin has been built by the official publisher."',
         'children:"此插件由官方发布者构建。"'),
        ('children:"Read URL content?"', 'children:"读取 URL 内容？"'),
        ('children:"Run MCP tool call?"', 'children:"运行 MCP 工具调用？"'),
        ('children:"Modify the config used for browser interactions. Saved automatically."',
         'children:"修改用于浏览器交互的配置。自动保存。"'),
        ('children:"After reporting the issue, reload your window to resume Agent use."',
         'children:"报告问题后，重新加载窗口以恢复 Agent 使用。"'),
        ('children:"Files results show if their associated language extension is installed."',
         'children:"文件结果会在安装了关联的语言扩展后显示。"'),
        ('children:"Select a trajectory"', 'children:"选择一个轨迹"'),

        # ============================================================
        # 7. Headers / Sections
        # ============================================================
        ('children:"Sources"', 'children:"来源"'),
        ('children:"Details"', 'children:"详细信息"'),
        ('children:"Features"', 'children:"功能"'),
        ('children:"Comments"', 'children:"评论"'),
        ('children:"Images"', 'children:"图片"'),
        ('children:"Files Edited"', 'children:"已编辑文件"'),
        ('children:"Background Steps"', 'children:"后台步骤"'),
        ('children:"Suggested Actions"', 'children:"建议操作"'),
        ('children:"Progress Updates"', 'children:"进度更新"'),
        ('children:"Thought Process"', 'children:"思考过程"'),
        ('children:"Pending messages"', 'children:"待处理消息"'),
        ('children:"Knowledge Generation"', 'children:"知识生成"'),
        ('children:"Recent actions"', 'children:"最近操作"'),
        ('children:"Report Issue"', 'children:"报告问题"'),
        ('children:"Conversation"', 'children:"对话"'),
        ('children:"Additional options"', 'children:"其他选项"'),
        ('children:"Feedback"', 'children:"反馈"'),
        ('children:"Denied Sites"', 'children:"被拒绝的网站"'),
        ('children:"Global"', 'children:"全局"'),
        ('children:"MCP Store"', 'children:"MCP 商店"'),

        # ============================================================
        # 8. Feedback
        # ============================================================
        ('children:"Good"', 'children:"好"'),
        ('children:"Bad"', 'children:"差"'),
        ('children:"Good response"', 'children:"好的响应"'),
        ('children:"Bad response"', 'children:"差的响应"'),

        # ============================================================
        # 9. Browser Features
        # ============================================================
        ('children:"Open System Browser"', 'children:"打开系统浏览器"'),
        ('children:"Fetched network request for page."', 'children:"已获取页面的网络请求。"'),
        ('children:"Fetched network requests for page."', 'children:"已获取页面的网络请求。"'),

        # ============================================================
        # 10. Labels (buttons/tabs/selectors)
        # ============================================================
        ('label:"Complete verification"', 'label:"完成验证"'),
        ('label:"Copy"', 'label:"复制"'),
        ('label:"Paste"', 'label:"粘贴"'),
        ('label:"Export"', 'label:"导出"'),
        ('label:"Enable"', 'label:"启用"'),
        ('label:"Retry"', 'label:"重试"'),
        ('label:"Try again"', 'label:"再试一次"'),
        ('label:"Deny"', 'label:"拒绝"'),
        ('label:"Allow Once"', 'label:"允许一次"'),
        ('label:"Always Allow"', 'label:"始终允许"'),
        ('label:"Always run"', 'label:"始终运行"'),
        ('label:"Ask every time"', 'label:"每次询问"'),
        ('label:"Ask first"', 'label:"先询问"'),
        ('label:"Always Proceed"', 'label:"始终继续"'),
        ('label:"Request Review"', 'label:"请求审查"'),
        ('label:"Agent Decides"', 'label:"Agent 决定"'),
        ('label:"Download Diagnostics"', 'label:"下载诊断信息"'),
        ('label:"Copy debug info"', 'label:"复制调试信息"'),
        ('label:"Select Model"', 'label:"选择模型"'),
        ('label:"Select another model"', 'label:"选择其他模型"'),
        ('label:"Terminal"', 'label:"终端"'),
        ('label:"Media"', 'label:"媒体"'),
        ('label:"Errors"', 'label:"错误"'),
        ('label:"Conversation"', 'label:"对话"'),
        ('label:"Reject"', 'label:"拒绝"'),
        ('label:"Global"', 'label:"全局"'),
        ('label:"Workspace"', 'label:"工作区"'),
        ('label:"Free"', 'label:"免费"'),

        # ============================================================
        # 11. Titles (tooltips / dialog headers)
        # ============================================================
        ('title:"Verification required"', 'title:"需要验证"'),
        ('title:"Share Conversation"', 'title:"分享对话"'),
        ('title:"Enable Notifications"', 'title:"启用通知"'),
        ('title:"Select Model to Send Message"', 'title:"选择模型以发送消息"'),
        ('title:"Model quota limit exceeded"', 'title:"模型配额已超限"'),
        ('title:"Capture screenshot"', 'title:"截取屏幕"'),
        ('title:"Capture console logs"', 'title:"捕获控制台日志"'),
        ('title:"Confirm dismiss?"', 'title:"确认忽略？"'),
        ('title:"Could not send message"', 'title:"无法发送消息"'),
        ('title:"Your modified files:"', 'title:"你修改的文件："'),
        ('title:"Your recent Browser activity:"', 'title:"你最近的浏览器活动："'),
        ('title:"Your recent terminal commands:"', 'title:"你最近的终端命令："'),
        ('title:"View Page"', 'title:"查看页面"'),
        ('title:"Mention Page"', 'title:"提及页面"'),
        ('title:"Full Error"', 'title:"完整错误"'),
        ('title:"Comments"', 'title:"评论"'),
        ('title:"First page"', 'title:"第一页"'),
        ('title:"Last page"', 'title:"最后一页"'),
        ('title:"Next page"', 'title:"下一页"'),
        ('title:"Previous page"', 'title:"上一页"'),
        ('title:"Copy full URL to clipboard"', 'title:"复制完整 URL 到剪贴板"'),
        ('title:"Click to copy full command"', 'title:"点击复制完整命令"'),
        ('title:"Copy trajectory ID"', 'title:"复制轨迹 ID"'),

        # ============================================================
        # 12. Placeholders
        # ============================================================
        ('placeholder:"Search MCP servers"', 'placeholder:"搜索 MCP 服务器"'),

        # ============================================================
        # 13. Text props
        # ============================================================
        ('text:"Go to Terminal"', 'text:"前往终端"'),
        ('text:"Open"', 'text:"打开"'),
        ('text:"Relocate"', 'text:"重新定位"'),

        # ============================================================
        # 14. Other children strings
        # ============================================================
        ('children:"Allow Once"', 'children:"允许一次"'),
        ('children:"Allow This Conversation"', 'children:"本次对话允许"'),
        ('children:"Deny"', 'children:"拒绝"'),
        ('children:"Reject"', 'children:"拒绝"'),
        ('children:"Reject all"', 'children:"全部拒绝"'),
        ('children:"Learn more"', 'children:"了解更多"'),
        ('children:"file an issue"', 'children:"提交问题"'),
        ('children:"reload the window"', 'children:"重新加载窗口"'),
        ('children:"troubleshooting guide"', 'children:"故障排除指南"'),
        ('children:"Show items analyzed"', 'children:"显示已分析项目"'),
        # === Accept / Add / Edit / Loading ===
        ('children:"Accept"', 'children:"接受"'),
        ('children:"Accept all"', 'children:"全部接受"'),
        ('children:"Add Model"', 'children:"添加模型"'),
        ('children:"Add context"', 'children:"添加上下文"'),
        ('children:"Add them to allow future interactions"', 'children:"将它们添加到允许列表以允许未来的交互"'),
        ('children:"Added Annotation"', 'children:"已添加注释"'),
        ('children:"Edit Model"', 'children:"编辑模型"'),
        ('label:"Run"', 'label:"运行"'),
        # === v1.107.0 Chat updates ===
        ('children:"Open Diff"', 'children:"打开差异"'),
        ('label:"Allow Once"', 'label:"允许一次"'),
        ('label:"Deny"', 'label:"拒绝"'),
        ('children:"Additional Options"', 'children:"其他选项"'),
        ('label:"Try Again"', 'label:"再试一次"'),
        ('title:"Add Context"', 'title:"添加上下文"'),
    ] + STUBBORN_RAW_STRINGS


def patch_file(filepath, replacements, name):
    """对单个文件应用替换"""
    backup = filepath + '.bak'

    if not os.path.exists(filepath):
        print(f'  ❌ 文件不存在: {filepath}')
        return 0

    # Backup
    if not os.path.exists(backup):
        shutil.copy2(filepath, backup)
        print(f'  ✅ 已备份: {os.path.basename(backup)}')
    else:
        print(f'  ⏭️  备份已存在: {os.path.basename(backup)}')

    with open(filepath, 'r', encoding='utf-8', errors='replace', newline='') as f:
        content = f.read()

    count = 0
    failed = []
    
    import re

    for old, new in replacements:
        if old in content:
            content = content.replace(old, new)
            count += 1
        else:
            # Regex Fallback for raw strings
            if old.startswith('"') and old.endswith('"'):
                raw_eng = old[1:-1]
                raw_chn = new[1:-1]
                # Allow flexible whitespace and single/double quote escaping
                escaped = re.escape(raw_eng).replace(r'\ ', r'\s+').replace(r"'", r"[\'\\]+").replace(r'"', r'[\"\\]+')
                pattern = r'([\'"`>]|^)' + escaped + r'([\'"`<]|$)'
                def repl(m):
                    return m.group(1) + raw_chn + m.group(2)
                new_content, n = re.subn(pattern, repl, content)
                if n > 0:
                    content = new_content
                    count += 1
                    continue

            failed.append(old[:50])

    with open(filepath, 'w', encoding='utf-8', newline='') as f:
        f.write(content)

    print(f'  🎉 {name}: 成功替换 {count}/{len(replacements)} 处')
    if failed:
        print(f'  ⚠️  未匹配 {len(failed)} 处:')
        for f_str in failed:
            print(f'    - {f_str}...')
    return count


def update_checksums():
    """更新 product.json 中的文件校验值，消除'安装似乎损坏'提示"""
    if not os.path.exists(PRODUCT_JSON):
        print('  ⚠️  product.json 不存在，跳过 checksum 更新')
        return

    # Backup
    backup = PRODUCT_JSON + '.bak'
    if not os.path.exists(backup):
        shutil.copy2(PRODUCT_JSON, backup)

    with open(PRODUCT_JSON, 'r', encoding='utf-8') as f:
        product = json.load(f)

    checksums = product.get('checksums', {})
    updated = 0
    for key in checksums:
        for prefix in [os.path.join(BASE, 'out'), BASE]:
            filepath = os.path.normpath(os.path.join(prefix, key))
            if os.path.exists(filepath):
                with open(filepath, 'rb') as f:
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
        print(f'  ✅ 已更新 {updated} 个文件校验值')
    else:
        print('  ⏭️  校验值无需更新')


def get_workbench_replacements():
    """快速设置面板 (workbench.desktop.main.js) 的替换对"""
    return [
        # ============================================================
        # 1. On/Off 枚举（全局生效，影响所有设置项的 On/Off 显示）
        # ============================================================
        ('i.ON="On",i.OFF="Off"', 'i.ON="开",i.OFF="关"'),

        # ============================================================
        # 2. 面板底部标签页
        # ============================================================
        # NOTE: label:"Settings" 是面板 tab 的路由 key，不翻译
        ('label:"AI Shortcuts"', 'label:"AI 快捷键"'),

        # ============================================================
        # 3. 面板内 textContent 文本
        # ============================================================
        ('textContent="Advanced Settings"', 'textContent="高级设置"'),
        ('textContent="Customizations"', 'textContent="自定义"'),
        ('textContent="Manage"', 'textContent="管理"'),
        ('textContent="Snooze"', 'textContent="暂停"'),
        ('textContent=o?"Cancel":"Start"', 'textContent=o?"取消":"开始"'),
        ('textContent="Manage MCP servers"', 'textContent="管理 MCP 服务器"'),
        ('textContent="View raw config"', 'textContent="查看原始配置"'),

        # ============================================================
        # 4. 安全面板 textContent（Terminal/Review/JS execution policy）
        # ============================================================
        ('textContent="Terminal execution policy"', 'textContent="终端执行策略"'),
        ('textContent="Review policy"', 'textContent="审查策略"'),
        ('textContent="JavaScript execution policy"', 'textContent="JavaScript 执行策略"'),
        # 下拉选项 textContent
        ('textContent="Always Proceed"', 'textContent="始终继续"'),
        ('textContent="Request Review"', 'textContent="请求审查"'),
        ('textContent="Agent Decides"', 'textContent="Agent 决定"'),
        ('textContent="Disabled"', 'textContent="已禁用"'),

        # ============================================================
        # 5. Settings 项的 label（显示名称）
        # ============================================================
        ('label:"Agent Auto-Fix Lints"', 'label:"Agent 自动修复 Lint"'),
        ('label:"Auto Execution"', 'label:"自动执行"'),
        ('label:"Review Policy"', 'label:"审查策略"'),
        ('label:"Agent Gitignore Access"', 'label:"Agent Gitignore 访问"'),
        ('label:"Tab Gitignore Access"', 'label:"Tab Gitignore 访问"'),
        ('label:"Tab Speed"', 'label:"Tab 速度"'),
        ('label:"Tab to Jump"', 'label:"Tab 跳转"'),
        ('label:"Tab to Import"', 'label:"Tab 导入"'),
        ('label:"Auto-Open Edited Files"', 'label:"自动打开已编辑文件"'),
        ('label:"Open Agent on Reload"', 'label:"重新加载时打开 Agent"'),
        ('label:"Clipboard Context"', 'label:"剪贴板上下文"'),
        ('label:"Highlight After Accept"', 'label:"接受后高亮"'),
        ('label:"Suggestions in Editor"', 'label:"编辑器中的建议"'),
        ('label:"Enable Tab Sounds (Beta)"', 'label:"启用 Tab 声音 (Beta)"'),

        # ============================================================
        # 6. Settings 项的 description
        # ============================================================
        ('description:["Set the speed of tab suggestions"]',
         'description:["设置 Tab 建议的速度"]'),
        ('description:["Open files in the background if the agent creates or edits them"]',
         'description:["当 Agent 创建或编辑文件时在后台打开它们"]'),
        ('description:["Open Agent panel on window reload"]',
         'description:["窗口重新加载时打开 Agent 面板"]'),
        ('description:["Predict the location of your next edit and navigates you there with a tab keypress"]',
         'description:["预测下一个编辑位置，按 Tab 键即可跳转到该位置"]'),
        ('description:["Quickly add and update imports with a tab keypress."]',
         'description:["按 Tab 键快速添加和更新导入语句。"]'),
        ('description:["Highlight newly inserted text after accepting a Tab completion."]',
         'description:["接受 Tab 补全后高亮新插入的文本。"]'),

        # ============================================================
        # 7. Review Policy 下拉选项（label + description）
        # ============================================================
        ('{value:B5.TURBO,label:"Always Proceed",description:"Agent never asks for review. This maximizes the autonomy of the Agent, but also has the highest risk of the Agent operating over unsafe or injected Artifact content.",disabledInSecureMode:!0}',
         '{value:B5.TURBO,label:"始终继续",description:"Agent 从不请求审查。这最大化了 Agent 的自主性，但也具有 Agent 操作不安全或注入的 Artifact 内容的最高风险。",disabledInSecureMode:!0}'),
        ('{value:B5.AUTO,label:"Agent Decides",description:"Agent will decide when to ask for review based on task complexity and user preference."}',
         '{value:B5.AUTO,label:"Agent 决定",description:"Agent 将根据任务复杂性和用户偏好决定何时请求审查。"}'),
        ('{value:B5.ALWAYS,label:"Request Review",description:"Agent always asks for review.",disabledInSecureMode:!1}',
         '{value:B5.ALWAYS,label:"请求审查",description:"Agent 始终请求审查。",disabledInSecureMode:!1}'),

        # ============================================================
        # 8. Auto Execution 下拉选项
        # ============================================================
        ('{label:"Always Proceed",value:W1.EAGER,description:"Always auto-execute commands unless they are in your deny list. This also allows Agent to auto-execute Browser controls."}',
         '{label:"始终继续",value:W1.EAGER,description:"始终自动执行命令，除非它们在您的拒绝列表中。这也允许 Agent 自动执行浏览器控制。"}'),

        # ============================================================
        # 9. Tab Speed 下拉选项
        # ============================================================
        ('{label:"Slow",value:RV.SLOW}', '{label:"慢速",value:RV.SLOW}'),
        ('{label:"Fast",value:RV.FAST,isDefaultWhenAvailable:!0}', '{label:"快速",value:RV.FAST,isDefaultWhenAvailable:!0}'),

        # ============================================================
        # 10. Hover 提示文本
        # ============================================================
        ('"View and manage Agent memories, workflows, and rules"',
         '"查看和管理 Agent 记忆、工作流和规则"'),
        # === Accept / Add / Edit / Loading ===
        ('children:"Accept"', 'children:"接受"'),
        ('children:"Accept all"', 'children:"全部接受"'),
        ('children:"Add Model"', 'children:"添加模型"'),
        ('children:"Add context"', 'children:"添加上下文"'),
        ('children:"Add them to allow future interactions"', 'children:"将它们添加到允许列表以允许未来的交互"'),
        ('children:"Edit Model"', 'children:"编辑模型"'),
        ('children:"Edit rule"', 'children:"编辑规则"'),
        ('children:"Edit workflow"', 'children:"编辑工作流"'),
        ('children:"Edit your SSH configuration"', 'children:"编辑你的 SSH 配置"'),
        ('children:"Loading..."', 'children:"加载中..."'),
        ('children:"Loading MCP servers"', 'children:"正在加载 MCP 服务器"'),
        ('children:"Loading models..."', 'children:"正在加载模型..."'),
        ('children:"Loading Browser recording..."', 'children:"正在加载浏览器录制..."'),
        ('label:"Accept hunk"', 'label:"接受代码块"'),
        ('label:"Run"', 'label:"运行"'),
        ('label:"Running"', 'label:"运行中"'),
        ('label:"Open Agent"', 'label:"打开 Agent"'),
        ('label:"Reset to default"', 'label:"重置为默认"'),
        ('label:"Submit"', 'label:"提交"'),
        # === v1.107.0 Workbench updates ===
        ('t.ON="On",t.OFF="Off"', 't.ON="开",t.OFF="关"'),
        ('children:"Terminal execution policy"', 'children:"终端执行策略"'),
        ('children:"Review policy"', 'children:"审查策略"'),
        ('children:"JavaScript execution policy"', 'children:"JavaScript 执行策略"'),
        ('children:"Always Proceed"', 'children:"始终继续"'),
        ('children:"Request Review"', 'children:"请求审查"'),
        ('children:"Always Ask"', 'children:"始终询问"'),
        ('children:"Disabled"', 'children:"已禁用"'),
        ('{value:Vz.TURBO,label:"Always Proceed",description:"Agent never asks for review. This maximizes the autonomy of the Agent, but also has the highest risk of the Agent operating over unsafe or injected Artifact content.",disabledInSecureMode:!0}',
         '{value:Vz.TURBO,label:"始终继续",description:"Agent 从不请求审查。这最大化了 Agent 的自主性，但也具有 Agent 操作不安全或注入的 Artifact 内容的最高风险。",disabledInSecureMode:!0}'),
        ('{value:Vz.ALWAYS,label:"Always Ask",description:"Agent always asks for review.",disabledInSecureMode:!1}',
         '{value:Vz.ALWAYS,label:"始终询问",description:"Agent 始终请求审查。",disabledInSecureMode:!1}'),
        ('{label:"Always Proceed",value:$9.TURBO,description:"Trust the agent to do tasks end-to-end",isDefaultWhenAvailable:!0}',
         '{label:"始终继续",value:$9.TURBO,description:"信任 Agent 端到端地执行任务",isDefaultWhenAvailable:!0}'),
        ('{label:"Agent Decides",value:$9.AUTO,description:"Assist the agent to complete tasks"}',
         '{label:"Agent 决定",value:$9.AUTO,description:"辅助 Agent 完成任务"}'),
        ('{label:"Request Review",value:$9.ALWAYS,description:"Collaborate with the agent to complete tasks"}',
         '{label:"请求审查",value:$9.ALWAYS,description:"与 Agent 协作完成任务"}'),
        ('{label:"Always Proceed",value:$U.EAGER,description:"Always auto-execute commands unless they are in your deny list. This also allows Agent to auto-execute Browser controls."}',
         '{label:"始终继续",value:$U.EAGER,description:"始终自动执行命令，除非它们在您的拒绝列表中。这也允许 Agent 自动执行浏览器控制。"}'),
        ('{label:"Request Review",value:$U.OFF,description:"Never auto-execute commands unless they are in your allow list.",isDefaultWhenAvailable:!0}',
         '{label:"请求审查",value:$U.OFF,description:"从不自动执行命令，除非它们在您的允许列表中。",isDefaultWhenAvailable:!0}'),
        ('{label:"Slow",value:Fwe.SLOW}', '{label:"慢速",value:Fwe.SLOW}'),
        ('{label:"Fast",value:Fwe.FAST,isDefaultWhenAvailable:!0}', '{label:"快速",value:Fwe.FAST,isDefaultWhenAvailable:!0}'),
        # === Remaining workbench/feedback/shortcuts translations ===
        ('label:"Open Conversation Picker"', 'label:"打开对话选择器"'),
        ('label:"Open File Search"', 'label:"打开文件搜索"'),
        ('label:"Focus Input"', 'label:"聚焦输入框"'),
        ('label:"New Conversation"', 'label:"新建对话"'),
        ('label:"Open Workspace Selector"', 'label:"打开工作区选择器"'),
        ('label:"Go Back"', 'label:"后退"'),
        ('label:"Go Forward"', 'label:"前进"'),
        ('label:"File Picker"', 'label:"文件选择器"'),
        ('label:"Toggle Editor"', 'label:"切换编辑器"'),
        ('label:"Select Previous Conversation"', 'label:"选择上一个对话"'),
        ('label:"Select Next Conversation"', 'label:"选择下一个对话"'),
        ('label:"Toggle Model Selector"', 'label:"切换模型选择器"'),
        ('label:"Start Voice Recording"', 'label:"开始语音录制"'),
        ('label:"Stop Voice Recording"', 'label:"停止语音录制"'),
        ('label:"Find in Pane"', 'label:"在窗格中查找"'),
        ('label:"Toggle Sidebar"', 'label:"切换侧边栏"'),
        ('label:"Toggle Auxiliary Pane"', 'label:"切换辅助窗格"'),
        ('label:"Toggle Terminal"', 'label:"切换终端"'),
        ('label:"Open Settings"', 'label:"打开设置"'),
        ('label:"Zoom In"', 'label:"放大"'),
        ('label:"Zoom Out"', 'label:"缩小"'),
        ('label:"Reset Zoom"', 'label:"重置缩放"'),
        ('children:"Recommended"', 'children:"推荐"'),
        ('children:"Navigation"', 'children:"导航"'),
        ('children:"Conversation"', 'children:"对话"'),
        ('children:"Layout Controls"', 'children:"布局控制"'),
        ('children:"Shortcuts"', 'children:"快捷键"'),
        ('description:"Keyboard shortcuts for quick navigation and control."', 'description:"用于快速导航和控制的键盘快捷键。"'),
        ('children:"Feedback Type"', 'children:"反馈类型"'),
        ('"bug-report":"Bug Report"', '"bug-report":"Bug 报告"'),
        ('"feature-request":"Feature Request"', '"feature-request":"功能请求"'),
        ('"auth-and-billing":"Auth and Billing"', '"auth-and-billing":"认证与计费"'),
        ('"general-feedback":"General Feedback"', '"general-feedback":"常规反馈"'),
        ('children:"Please describe the issue in detail. The more actionable your feedback, the quicker our team can address your request. Some helpful information includes:"',
         'children:"请详细描述该问题。您的反馈越具可操作性，我们的团队就能越快处理您的请求。一些有帮助的信息包括："'),
        ('children:"Steps to reproduce the issue"', 'children:"重现问题的步骤"'),
        ('children:"Expected behavior"', 'children:"预期行为"'),
        ('children:"Actual behavior"', 'children:"实际行为"'),
        ('children:"Any error messages"', 'children:"任何错误消息"'),
        ('children:"Any relevant information"', 'children:"任何相关信息"'),
        ('"bug-report":"Describe the bug you encountered..."', '"bug-report":"请描述您遇到的 Bug..."'),
        ('children:"Steps to Reproduce"', 'children:"重现步骤"'),
        ('placeholder:"Please list the steps to reproduce the issue"', 'placeholder:"请列出重现该问题的步骤"'),
        ('children:"Attach a screenshot (optional)"', 'children:"附加屏幕截图 (可选)"'),
        ('label:"Attach Antigravity server logs"', 'label:"附加 Antigravity 服务器日志"'),
        ('label:"Send feedback as "+e.email', 'label:"发送反馈，身份为："+e.email'),
        ('children:"We recommend attaching logs. Attaching logs will help the Antigravity team act on and prioritize your feedback."',
         'children:"我们建议附加日志。附加日志将帮助 Antigravity 团队针对您的反馈进行处理并排定优先级。"'),
        ('title:"Model quota reached"', 'title:"已达到模型配额限制"'),
        ("` Your plan's baseline quota will refresh on ${o}.`", "` 您方案的基准配额将在 ${o} 刷新。`"),
        ('label:d||"Upgrade"', 'label:d||"升级"'),
        ('children:n.userTier?.upgradeButtonText||"Upgrade"', 'children:n.userTier?.upgradeButtonText||"升级"'),
    ] + STUBBORN_RAW_STRINGS


def apply_patch():
    """应用汉化补丁"""
    total = 0

    print('📦 [1/4] 汉化 Settings 面板 (jetskiAgent/main.js)...')
    total += patch_file(TARGETS['settings'], get_settings_replacements(), 'Settings')

    print()
    print('📦 [2/4] 汉化 Agent 聊天面板 (chat.js / workbench)...')
    if os.path.exists(TARGETS['chat']):
        total += patch_file(TARGETS['chat'], get_chat_replacements(), 'Chat')
    else:
        print('  ℹ️  chat.js 不存在，应用 Chat 替换到 workbench.desktop.main.js')
        total += patch_file(TARGETS['workbench'], get_chat_replacements(), 'Chat in Workbench')

    print()
    print('📦 [3/4] 汉化快速设置面板 (workbench.desktop.main.js)...')
    total += patch_file(TARGETS['workbench'], get_workbench_replacements(), 'Workbench')

    print()
    print('📦 [4/4] 更新文件校验值 (消除"安装损坏"提示)...')
    update_checksums()

    print(f'\n🎉 全部完成！共替换 {total} 处')
    print('📌 请重启 Antigravity 以生效')


def revert_patch():
    """恢复所有原文件"""
    for name, filepath in TARGETS.items():
        backup = filepath + '.bak'
        if os.path.exists(backup):
            shutil.copy2(backup, filepath)
            print(f'  ✅ 已恢复: {name} ({os.path.basename(filepath)})')
        else:
            print(f'  ⏭️  无需恢复 (无备份): {name}')

    # Restore product.json
    pj_backup = PRODUCT_JSON + '.bak'
    if os.path.exists(pj_backup):
        shutil.copy2(pj_backup, PRODUCT_JSON)
        print(f'  ✅ 已恢复: product.json')

    print('📌 请重启 Antigravity 以生效')


if __name__ == '__main__':
    if '--revert' in sys.argv:
        revert_patch()
    else:
        apply_patch()
