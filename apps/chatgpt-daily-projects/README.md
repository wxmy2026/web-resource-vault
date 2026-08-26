# ChatGPT Daily Projects

目标：每天自动创建两个**全新的 ChatGPT 聊天**，并从创建时就放在正确的 Project 里，而不是把数月内容不断追加到同一个 Scheduled Task 聊天。

- `每日全球深度简报` → Project：`每日全球深度简报`
- `世界小镇故事` → Project：`世界小镇故事`

这样 Project 保存长期主题与跨聊天连续性，每一天的聊天只保存当天局部上下文，避免单个线程无限增长。

## 为什么不用普通 Scheduled Task

ChatGPT 当前的 recurring Scheduled Task 仍有“关联聊天”，官方说明删除关联聊天会暂停任务，并且监控类任务可以记住之前运行结果。官方目前没有提供“每次运行都在指定 Project 新建一个独立聊天”的公开设置或 Projects API。

因此本工具只自动化 ChatGPT **可见网页界面**：打开目标 Project URL → 在 Project composer 新建当天聊天 → 发送当天 prompt → 等待完成。没有调用未公开 Project API，也不会读取 Chrome 密码或把 ChatGPT cookie 上传到 GitHub。

## 安全与登录

浏览器登录状态只保存在本机：

`~/.chatgpt-daily-projects/browser-profile`

第一次安装时会打开一个专用 Chromium 窗口，需要本人登录 ChatGPT 一次。之后每日运行复用这个本地 profile。不要把该目录提交到 GitHub。

## macOS 一次性安装

在已经 clone 的 `web-resource-vault` 仓库中运行：

```bash
cd apps/chatgpt-daily-projects
bash install_macos.sh
```

安装器会：

1. 创建独立 Python venv；
2. 安装 Playwright + Chromium；
3. 安装 macOS LaunchAgent；
4. 打开一次 ChatGPT 登录窗口；
5. 登录成功后立即测试两个 Project 各新建一条聊天；
6. 之后每天 08:00 自动运行。

## 日常行为

每天运行时：

1. 打开 ChatGPT；
2. 从侧栏读取 Project 的真实 `/g/g-p-.../project` 地址；
3. 直接进入 Project composer（不会打开昨天的 `/c/...` 聊天）；
4. 生成日期章节标识；
5. 发送对应 prompt；
6. 等待回答完成；
7. 在 `~/.chatgpt-daily-projects/state.json` 记录当天已完成，防止重复生成。

如果 Mac 在 08:00 关机/长期离线，LaunchAgent 的具体补跑行为由 macOS 决定。可以手动补跑：

```bash
.venv/bin/python runner.py --job all
```

强制重做当天：

```bash
.venv/bin/python runner.py --job all --force
```

重新登录：

```bash
.venv/bin/python runner.py --login
```

日志：

`~/.chatgpt-daily-projects/runner.log`

## 与现有 ChatGPT Scheduled Tasks 的切换

在本工具完成首次测试以前，保留现有两个 Scheduled Tasks，避免漏更。确认浏览器自动化成功后，再暂停原来的 `每日全球深度简报` 和 `世界小镇故事` recurring tasks，防止每天生成两份。

## 维护说明

ChatGPT 网页 UI 会变化。当前实现优先依赖相对稳定的 Project URL 形态 `/g/g-p-.../project`、`#prompt-textarea`、`data-testid=send-button` 和 conversation-turn 元素，并准备了 selector fallback。若网页结构改变，只需维护 `runner.py` 的 selector 列表，不影响 prompt、Project 内容和历史聊天。
