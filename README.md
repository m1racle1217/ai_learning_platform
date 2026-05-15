# 🚀 AI 学习驾驶舱

一个本地运行的 70 天 AI 应用开发学习平台。它把学习路线、资源跳转、每日练习、随堂小测、打卡进度和行为记录放在同一个轻量 Web 应用里，用 SQLite 保存在本地。

## ✨ 亮点

- 🧭 70 天 AI 应用开发路线：Prompt、LLM 基础、Tool Calling、MCP、Agent、Memory、RAG、Dify、微调认知与毕业项目
- ✅ 每日打卡：学习状态、资源勾选、练习提交、小测记录都会保存
- 🧪 高质量随堂小测：围绕当天内容生成场景题、排错题、风险判断题和交付验收题
- 🛠️ 新手友好的练习 runbook：每一天都有目标拆解、执行步骤、验证命令、失败处理和提交证据
- 🔗 高价值资源库：视频、文档、GitHub、工具链接可直接跳转
- 💾 本地 SQLite：不依赖云服务，进度数据保存在本机
- 🧹 设置页支持清空进度：保留学习路线和资源，重置用户打卡数据

## 🖥️ 一键启动

### Windows

双击：

```text
start_windows.bat
```

### macOS

第一次运行前执行：

```bash
chmod +x start_mac.command
```

之后双击：

```text
start_mac.command
```

启动器会自动选择一个空闲本地端口，并打开浏览器。

## 📦 手动安装

```bash
git clone https://github.com/m1racle1217/ai_learning_platform.git
cd ai_learning_platform
python -m venv .venv
```

Windows PowerShell：

```powershell
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -e .[dev]
python scripts\start_app.py
```

macOS / Linux：

```bash
source .venv/bin/activate
python -m pip install --upgrade pip
pip install -e ".[dev]"
python scripts/start_app.py
```

## 🗂️ 数据初始化

项目首次启动时，如果 `data/app.db` 不存在，会自动从下面的 Excel 初始化学习路线和资源：

```text
data/source/70天AI入门到微调进阶学习(附带打卡).xlsx
```

`data/app.db` 是本地运行产物，不会提交到 Git。每个人 clone 后都会生成自己的本地数据库。

## 🔐 API 配置

复制 `.env.example` 为 `.env`，按需填写：

```env
DEEPSEEK_API_KEY=
DEEPSEEK_BASE_URL=https://api.deepseek.com
DEEPSEEK_MODEL=deepseek-v4-flash
```

没有 API Key 也可以使用学习路线、资源跳转、练习提交、小测和打卡功能。

## 🧪 开发测试

```bash
python -m pytest -q
```

## 🧹 清空进度

打开应用后进入：

```text
/settings
```

点击“清空进度”会删除资源勾选、练习提交、小测记录，并把 70 天状态恢复为未开始；学习路线、题库和资源库会保留。

## 📁 项目结构

```text
app/
  routers/       # FastAPI 路由
  services/      # 小测、练习指导、进度、行为记录等业务逻辑
  templates/     # Jinja 页面
  static/        # CSS / 背景资源
data/source/     # 初始化学习计划 Excel
scripts/         # 一键启动脚本
tests/           # 回归测试
```

## 🎯 适合谁

- 想从 Python + API 调用起步，系统学习 AI 应用开发的人
- 想把 Prompt、RAG、Agent、Dify、微调认知串成完整路线的人
- 想每天打卡，并用练习和小测检验理解质量的人

祝你每天都往前推一格。🌱
