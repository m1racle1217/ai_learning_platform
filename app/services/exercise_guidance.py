from typing import Any

from app.models import LearningDay


def build_exercise_guidance(day: LearningDay) -> list[dict[str, Any]]:
    if day.day_number == 1:
        return _day_one_guidance(day)
    return _generic_guidance(day)


def _step(title: str, body: str, commands: list[str] | None = None, verify: str | None = None) -> dict[str, Any]:
    return {
        "title": title,
        "body": body,
        "commands": commands or [],
        "verify": verify,
    }


def _section(title: str, intro: str, steps: list[dict[str, Any]]) -> dict[str, Any]:
    return {"title": title, "intro": intro, "steps": steps}


def _day_one_guidance(day: LearningDay) -> list[dict[str, Any]]:
    return [
        _section(
            "1. 明确交付物和验收边界",
            "第 1 天的专业目标不是“装很多工具”，而是交付一个可复查的学习仓库：能运行基础验证命令、能提交第一次 commit、README 能说明目录用途。",
            [
                _step(
                    "准备固定工作目录",
                    "Windows 建议使用 PowerShell，macOS 使用 Terminal。把学习内容放到固定目录，后续所有 demo、笔记、评测和数据都从这里进入，避免路径混乱。",
                    [
                        "cd D:\\学习资料",
                        "mkdir ai-agent-learning",
                        "cd ai-agent-learning",
                        "pwd",
                    ],
                    "验证命令：pwd 或 Get-Location 显示当前位置在 ai-agent-learning。",
                ),
            ],
        ),
        _section(
            "2. 安装并验证 Python 3.11+",
            "Python 是后面调用模型 API、写 Agent、做 RAG demo 的主语言。这里要同时确认解释器、pip 和虚拟环境都可用。",
            [
                _step(
                    "Windows 安装和验证",
                    "从 python.org/downloads 安装 Python 3.11+，安装第一页勾选 Add python.exe to PATH。安装后关闭 PowerShell 重新打开，再验证版本。",
                    ["python --version", "py --version", "python -m pip --version"],
                    "验证命令：任一 Python 命令显示 3.11+，pip 能显示版本。",
                ),
                _step(
                    "macOS 安装和验证",
                    "可以从 python.org 下载 installer，也可以用 Homebrew。macOS 常用 python3 命令，后续命令里的 python 可按实际替换成 python3。",
                    ["python3 --version", "python3 -m pip --version"],
                    "验证命令：python3 显示 3.11+，pip 能显示版本。",
                ),
                _step(
                    "创建虚拟环境",
                    "虚拟环境用于隔离项目依赖，防止把全局 Python 搞乱。Windows 优先尝试 py -3.11，失败再用 python。",
                    ["py -3.11 -m venv .venv", ".\\.venv\\Scripts\\Activate.ps1", "python -m pip install --upgrade pip"],
                    "验证命令：命令行前面出现 (.venv)，python -m pip --version 能正常输出。",
                ),
                _step(
                    "失败处理",
                    "如果 PowerShell 不允许激活脚本，先执行 Set-ExecutionPolicy -Scope CurrentUser RemoteSigned；如果找不到 Python，重启终端并检查 PATH。",
                    ["Set-ExecutionPolicy -Scope CurrentUser RemoteSigned", "where python", "where py"],
                    "验证命令：重新打开 PowerShell 后能激活 .venv。",
                ),
            ],
        ),
        _section(
            "3. 安装 Git 并设置身份",
            "Git 用来保存每一天的代码和笔记。你不需要一开始就会 GitHub，先会本地 commit。",
            [
                _step(
                    "安装 Git",
                    "Windows 打开 git-scm.com 下载 Git for Windows，一路默认安装即可。macOS 可以安装 Xcode Command Line Tools 或 Homebrew Git。",
                    ["git --version", "git config --global --list"],
                    "验证命令：能看到 git version；如果 user.name/user.email 为空，继续下一步设置。",
                ),
                _step(
                    "设置提交身份",
                    "这只是本地提交显示的名字和邮箱，可以先用自己的常用昵称和邮箱。",
                    ['git config --global user.name "你的名字"', 'git config --global user.email "you@example.com"', "git config --global --list"],
                    "验证命令：输出里包含 user.name 和 user.email。",
                ),
            ],
        ),
        _section(
            "4. 安装 VS Code",
            "VS Code 用来编辑代码、README、.env.example 和后续笔记。新手先只装 Python 扩展。",
            [
                _step(
                    "安装编辑器",
                    "打开 code.visualstudio.com 下载 VS Code。安装后打开扩展面板，搜索并安装 Python 扩展。",
                    [],
                    "能在 VS Code 里打开 ai-agent-learning 文件夹。",
                ),
                _step(
                    "用命令行打开项目",
                    "如果 code 命令可用，可以在项目目录直接打开 VS Code；不可用也没关系，手动 File -> Open Folder。",
                    ["code ."],
                    "VS Code 左侧能看到当前项目目录。",
                ),
            ],
        ),
        _section(
            "5. 学会 pip 和 uv 的最小用法",
            "pip 是 Python 自带包管理，uv 是更快的现代工具。第 1 天只要求知道怎么检查、怎么安装包，不要求深入。",
            [
                _step(
                    "确认 pip 可用并安装一个轻量依赖",
                    "pip 用来安装 Python 第三方库。先安装 python-dotenv，后面读取 API Key 会用到。",
                    ["python -m pip --version", "python -m pip install python-dotenv", "python -c \"import dotenv; print('dotenv ok')\""],
                    "验证命令：输出 dotenv ok。",
                ),
                _step(
                    "安装 uv 并理解它的位置",
                    "uv 是更快的包管理工具，后续项目会逐步使用。第 1 天只要求安装和查看版本；如果网络失败，记录报错，不阻塞当天主线。",
                    ["python -m pip install uv", "uv --version"],
                    "验证命令：能看到 uv 版本；失败处理：把完整报错写入 notes/troubleshooting.md。",
                ),
            ],
        ),
        _section(
            "6. 创建学习仓库和目录",
            "仓库就是你的学习工程文件夹。今天要建立固定结构，后面所有模块都往这里加。",
            [
                _step(
                    "初始化 Git 仓库",
                    "在 ai-agent-learning 目录里执行 git init。它会生成隐藏的 .git 目录，用来记录版本。",
                    ["git init", "git status --short"],
                    "验证命令：git status --short 能显示未跟踪文件或为空，说明命令可用。",
                ),
                _step(
                    "创建四个常用目录",
                    "demos 放代码 demo，notes 放学习笔记，evals 放评测表，data 放测试数据。",
                    ["mkdir demos notes evals data"],
                    "目录里能看到 demos、notes、evals、data。",
                ),
                _step(
                    "创建 README、环境示例和忽略文件",
                    "README 写目录用途；.env.example 放环境变量名称但不放真实密钥；.gitignore 防止把 .env、缓存、虚拟环境提交进去。",
                    [
                        'echo # AI Agent Learning > README.md',
                        'echo DEEPSEEK_API_KEY=your_key_here > .env.example',
                        'echo .env> .gitignore',
                        'echo .venv/>> .gitignore',
                        'echo __pycache__/>> .gitignore',
                    ],
                    "验证命令：dir 或 ls 能看到 README.md、.env.example、.gitignore。",
                ),
                _step(
                    "补充 README 目录说明",
                    "README 至少写清 demos、notes、evals、data 的用途。不要只写一个标题，否则后面复盘和展示价值很低。",
                    [
                        'echo demos: 可运行代码 demo >> README.md',
                        'echo notes: 学习笔记和排错记录 >> README.md',
                        'echo evals: 评测样例和结果 >> README.md',
                        'echo data: 测试数据，不放敏感信息 >> README.md',
                    ],
                    "验证命令：打开 README.md 能看到四个目录说明。",
                ),
            ],
        ),
        _section(
            "7. 完成第一次 commit",
            "第一次 commit 是今天最重要的验收动作。它代表你的学习仓库已经能被版本管理追踪。",
            [
                _step(
                    "查看改动并提交",
                    "先用 git status --short 看哪些文件会被提交，确认没有 .env、.venv、__pycache__，再 add 和 commit。",
                    ["git status --short", "git add .", "git status --short", 'git commit -m "init learning repo"', "git log --oneline -1"],
                    "验证命令：git log --oneline -1 能看到 init learning repo。",
                ),
                _step(
                    "提交练习时怎么填",
                    "完成说明写：你安装了哪些工具、版本号是多少、仓库路径在哪里、commit 是否成功。输出物路径填 ai-agent-learning 文件夹的完整路径，或填 README.md 的完整路径。",
                    ["python --version", "git --version"],
                    "提交前能说清楚版本、路径、commit 记录。",
                ),
            ],
        ),
        _section(
            "8. 常见卡点和降级方案",
            "新手第 1 天最容易卡在 PATH、网络、权限和终端没重启。不要硬熬，先记录证据。",
            [
                _step(
                    "命令找不到",
                    "先关闭终端重新打开。Windows 检查安装时是否勾选 PATH；macOS 尝试 python3 而不是 python。",
                    ["where python", "where git", "python3 --version", "git --version"],
                    "失败处理：把命令、完整报错、系统版本写入 notes/troubleshooting.md。",
                ),
                _step(
                    "网络或下载失败",
                    "截图或复制完整报错，写入 notes/troubleshooting.md。今天允许先跳过 uv，只要 Python、Git、VS Code 跑通即可。",
                    ["mkdir notes", "notepad notes\\troubleshooting.md"],
                    "验证命令：notes/troubleshooting.md 存在，里面有报错和你尝试过的步骤。",
                ),
            ],
        ),
    ]


def _generic_guidance(day: LearningDay) -> list[dict[str, Any]]:
    return [
        _section(
            "1. 目标拆解与边界确认",
            "先把今天的概念、环境、输入、输出和验收标准拆开。专业学习不是照抄步骤，而是知道每一步在验证什么假设。",
            [
                _step("学习目标", day.learning_goal, verify="验证命令：能用一句话解释今天练习要证明什么能力。"),
                _step("环境依赖", day.environment, verify="验证命令：列出今天会用到的依赖，确认没有提前引入无关工具。"),
            ],
        ),
        _section(
            "2. 准备工作区与证据文件",
            "在学习仓库中为当天内容准备可追踪文件。后续提交练习时，平台会要求输出物路径，因此文件必须真实存在。",
            [
                _step(
                    "创建当天工作文件",
                    f"围绕第 {day.day_number} 天主题「{day.topic}」创建记录。代码放 demos，笔记放 notes，评测放 evals，数据放 data。",
                    [
                        "git status --short",
                        f"mkdir notes\\day-{day.day_number} demos\\day-{day.day_number} evals\\day-{day.day_number}",
                        f"echo # Day {day.day_number} - {day.topic} > notes\\day-{day.day_number}\\README.md",
                    ],
                    "验证命令：git status --short 能看到当天新增文件，且没有 .env、.venv、__pycache__。",
                )
            ],
        ),
        _section(
            "3. 执行步骤与最小闭环",
            "先按计划跑通最小闭环，再做优化。每一步都要留下输入、输出或观察结果。",
            [
                _step(
                    "执行步骤",
                    day.practice_steps,
                    commands=[
                        f"echo 目标：{day.learning_goal} >> notes\\day-{day.day_number}\\README.md",
                        f"echo 操作步骤：{day.practice_steps} >> notes\\day-{day.day_number}\\README.md",
                    ],
                    verify="验证命令：当天 README 中能看到目标、步骤、关键观察。",
                )
            ],
        ),
        _section(
            "4. 质量验证与失败处理",
            "练习不是只做完，还要证明它做对。若失败，不要改状态为已完成，先记录失败模式和排查过程。",
            [
                _step("质量验证", day.acceptance_criteria, verify="验证命令：能对照验收标准逐条说明完成/未完成。"),
                _step(
                    "失败处理",
                    day.guidance,
                    [
                        f"echo 卡点：{day.guidance} >> notes\\day-{day.day_number}\\README.md",
                        "git diff -- notes",
                    ],
                    "验证命令：失败时 notes 中有报错、输入、输出、已尝试步骤和下一步计划。",
                ),
            ],
        ),
        _section(
            "5. 提交证据与复盘口径",
            "最后把当天产物变成可追踪记录。提交说明要能让别人判断你是否真的完成，而不是只看一句感受。",
            [
                _step(
                    "提交证据",
                    f"输出物建议填写：{day.output_artifact}。完成说明写清产物路径、验证方式、遗留风险和下一步。",
                    [
                        "git status --short",
                        f"git add notes\\day-{day.day_number} demos\\day-{day.day_number} evals\\day-{day.day_number}",
                        f'git commit -m "day {day.day_number} practice: {day.topic}"',
                    ],
                    "验证命令：git log --oneline -1 能看到当天 commit；平台输出物路径能打开。",
                )
            ],
        ),
    ]
