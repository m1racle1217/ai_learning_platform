from typing import Any

from app.models import LearningDay


def build_exercise_guidance(day: LearningDay) -> list[dict[str, Any]]:
    if day.day_number == 1:
        return _day_one_guidance(day)
    if _is_domain(day, "mcp"):
        if "文件" in (day.topic or "") or "read_file" in _context(day):
            return _mcp_file_guidance(day)
        if "编排" in (day.topic or "") or "orchestration" in _context(day):
            return _mcp_orchestration_guidance(day)
        return _mcp_guidance(day)
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


def _context(day: LearningDay) -> str:
    module_name = day.module.name if day.module else ""
    return "\n".join(
        [
            module_name,
            day.topic or "",
            day.environment or "",
            day.learning_goal or "",
            day.practice_steps or "",
            day.output_artifact or "",
            day.guidance or "",
        ]
    ).lower()


def _is_domain(day: LearningDay, domain: str) -> bool:
    text = _context(day)
    if domain == "mcp":
        return "mcp" in text
    if domain == "rag":
        return any(keyword in text for keyword in ["rag", "向量", "检索", "知识库", "chunk"])
    if domain == "prompt":
        return any(keyword in text for keyword in ["prompt", "structured output", "few-shot", "react"])
    if domain == "tool":
        return any(keyword in text for keyword in ["function", "tool calling", "文件工具", "sql 工具", "工具安全"])
    if domain == "langgraph":
        return any(keyword in text for keyword in ["langgraph", "state", "planner", "executor", "human-in-the-loop", "multi-agent"])
    if domain == "memory":
        return any(keyword in text for keyword in ["memory", "记忆", "recall"])
    if domain == "dify":
        return "dify" in text
    if domain == "finetune":
        return any(keyword in text for keyword in ["微调", "lora", "qlora", "sft", "finetune", "adapter"])
    if domain == "agent":
        return any(keyword in text for keyword in ["agent", "openclaw", "ai coding", "capstone", "毕业项目", "mvp"])
    return False


def _domain_profile(day: LearningDay) -> dict[str, str]:
    if _is_domain(day, "rag"):
        return {
            "ability": "把知识库问题拆成 ingestion、chunking、embedding、retrieval、rerank、answer、citation、eval 七层，并能判断错误来自哪一层。",
            "implementation": "先用 3 篇 txt/markdown 建最小 corpus，固定 5 个问题，记录 chunk 参数、top_k、召回片段、引用来源和最终答案。",
            "commands": "python -m pip install chromadb sentence-transformers\nNew-Item -ItemType Directory -Force data\\rag evals demos | Out-Null\necho question,expected_source,actual_source,answer_ok > evals\\rag_eval.csv",
            "validation": "至少 5 个固定问题能复现；每个答案带引用片段；错误样本能归因到切分、召回、排序或生成。",
            "risk": "不要只看回答是否顺眼；重点检查无引用回答、错引来源、chunk 过大/过小、检索词不匹配和 PDF 噪声。",
            "product": "产品上要说明知识更新频率、答案可追溯性、用户能否接受引用展示；架构上要说明为什么先 RAG 而不是微调。",
        }
    if _is_domain(day, "prompt"):
        return {
            "ability": "把 prompt 当成可测试的接口契约，而不是灵感文案；明确输入、输出 schema、边界样例、失败类型和评分标准。",
            "implementation": "准备 10-20 条测试输入，对比两个 prompt 版本，记录正确率、格式错误、遗漏、幻觉和人工评分备注。",
            "commands": "python -m pip install pydantic python-dotenv\nNew-Item -ItemType Directory -Force evals demos notes | Out-Null\necho id,input,expected,actual,score,error_type > evals\\prompt_eval.csv",
            "validation": "同一测试集重复跑两版 prompt；结论必须来自 eval 表，而不是只挑一个好看的样例。",
            "risk": "不要为了通过一个样例把 prompt 写死；检查边界条件、输出格式漂移、过度解释和缺少拒答策略。",
            "product": "产品上要定义用户真正关心的质量指标；架构上要判断 prompt、结构化输出、工具调用分别承担什么边界。",
        }
    if _is_domain(day, "tool"):
        return {
            "ability": "理解模型只决定是否请求工具，真实执行必须由程序控制；工具 schema、allowlist、错误返回和日志是安全边界。",
            "implementation": "先写纯 Python 函数并用固定输入验证，再暴露 schema，最后让模型选择工具并记录调用入参、出参和异常。",
            "commands": "python -m pip install pydantic jsonschema\nNew-Item -ItemType Directory -Force demos data logs | Out-Null\necho trace_id,tool_name,arguments,result,error > logs\\tool_calls.csv",
            "validation": "正常路径、异常路径、越权路径都要有测试；日志能复现一次完整工具调用。",
            "risk": "不要把任意文件路径、任意 SQL 或 shell 命令直接暴露给模型；先用 allowlist 和只读能力。",
            "product": "产品上要确认工具失败时用户看到什么；架构上要区分可自动执行、需确认执行和禁止执行三类动作。",
        }
    if _is_domain(day, "langgraph"):
        return {
            "ability": "把 Agent 拆成状态、节点、边、终止条件和人工确认点，避免把所有逻辑塞进一个超长 prompt。",
            "implementation": "先画 state schema，再写最小 graph：输入节点、模型节点、工具节点、审核节点、结束节点，每条边都写触发条件。",
            "commands": "python -m pip install langgraph pydantic python-dotenv\nNew-Item -ItemType Directory -Force demos notes logs | Out-Null\necho step,node,state_delta,next_node,error > logs\\langgraph_trace.csv",
            "validation": "固定输入能稳定走到预期节点；异常输入不会无限循环；每一步 state diff 可观察。",
            "risk": "重点检查状态字段膨胀、循环无终止、工具错误吞掉、人工确认点缺失和日志不可复现。",
            "product": "产品上要定义哪些节点需要用户确认；架构上要说明为什么状态机比单轮聊天更可靠。",
        }
    if _is_domain(day, "memory"):
        return {
            "ability": "区分短期上下文、长期事实、语义召回和用户偏好；写入记忆前必须有策略，不能把所有对话都存起来。",
            "implementation": "先定义 memory schema 和写入规则，再用 JSONL/SQLite 存储，最后用固定问题验证召回是否真的改善答案。",
            "commands": "New-Item -ItemType Directory -Force data notes evals | Out-Null\necho '{\"user_id\":\"demo\",\"memory_type\":\"preference\",\"content\":\"sample\",\"source\":\"manual\"}' > data\\memory_samples.jsonl\necho query,expected_memory,actual_memory,answer_ok > evals\\memory_recall.csv",
            "validation": "同一用户跨轮次能召回必要事实；无关或敏感内容不会被错误写入；召回证据可查看。",
            "risk": "检查隐私、过期策略、错误记忆污染、相似但不相关的召回和模型把记忆当事实硬编。",
            "product": "产品上要让用户理解系统记住了什么；架构上要说明记忆写入、读取、删除和审计的边界。",
        }
    if _is_domain(day, "dify"):
        return {
            "ability": "用 Dify 对照代码实现，理解工作流编排、知识库、变量、节点失败和可视化调试之间的取舍。",
            "implementation": "只在当天需要时启动 Docker Compose；用同一批文档和问题对照 Dify 与代码版 RAG/Agent 的质量。",
            "commands": "docker --version\ndocker compose version\nNew-Item -ItemType Directory -Force notes\\dify evals | Out-Null",
            "validation": "Dify 应用能完成同一条测试任务；节点输入输出可截图/导出；与代码版的差异能被解释。",
            "risk": "不要把 Dify 当黑盒成品；检查模型配置、知识库切分、节点失败、密钥管理和导出迁移成本。",
            "product": "产品上评估交付速度和可维护性；架构上判断 Dify 适合原型、内部工具还是长期核心链路。",
        }
    if _is_domain(day, "finetune"):
        return {
            "ability": "先判断是否需要微调，再谈训练；用数据集、评估集、baseline、成本和风险证明微调价值。",
            "implementation": "先整理 JSONL 样本和 eval 集，不急着训练；训练前后必须用同一 rubric 比较提升和退化样本。",
            "commands": "New-Item -ItemType Directory -Force data evals notes | Out-Null\necho '{\"instruction\":\"sample\",\"input\":\"\",\"output\":\"sample\"}' > data\\finetune_samples.jsonl\npython -m json.tool data\\finetune_samples.jsonl",
            "validation": "数据格式合法、样本覆盖目标行为、baseline 有记录、训练后对比不只看一个漂亮样例。",
            "risk": "重点检查数据泄露、许可、灾难性遗忘、格式学会但事实变差、GPU 成本和线上推理成本。",
            "product": "产品上要说明 Prompt/RAG/微调三选一的依据；架构上要说明 adapter、base model、版本和回滚策略。",
        }
    if _is_domain(day, "agent"):
        return {
            "ability": "把 Agent 项目当成产品和工程系统：需求、用户路径、工具边界、评估、安全、演示和 README 都要闭环。",
            "implementation": "先收敛一个 happy path，再加工具、RAG/Memory、评估和演示材料；每次扩展都保留可运行版本。",
            "commands": "New-Item -ItemType Directory -Force capstone evals notes | Out-Null\necho # Capstone MVP > capstone\\README.md\necho scenario,input,expected,actual,pass > evals\\capstone_eval.csv",
            "validation": "核心任务可复现；失败路径有提示；README 能让别人拉下来运行；评估表能说明质量。",
            "risk": "避免范围过大、只做炫酷 UI、没有 eval、工具越权、日志缺失和环境无法复现。",
            "product": "产品上定义目标用户、核心场景和不可做清单；架构上定义哪些能力用 API、MCP、LangGraph、RAG 或 Dify。",
        }
    return {
        "ability": "把当天概念转成可复查的工程交付：目标、依赖、最小实现、验证证据、失败处理和复盘结论都要闭环。",
        "implementation": "先完成最小可运行版本，再围绕当天步骤补充记录、评估和异常处理。",
        "commands": f"mkdir notes\\day-{day.day_number} demos\\day-{day.day_number} evals\\day-{day.day_number}\npython --version\ngit status --short",
        "validation": "产物真实存在，能按验收标准复查，失败时有输入、输出、版本和已尝试步骤。",
        "risk": "不要只留下学习感受；检查版本、路径、密钥、网络、数据样本和复现命令。",
        "product": "从产品角度说明这个能力解决什么用户问题；从架构角度说明它放在系统哪一层。",
    }


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


def _mcp_guidance(day: LearningDay) -> list[dict[str, Any]]:
    output = day.output_artifact or "demos/06_mcp_hello.py"
    return [
        _section(
            "1. 先建立 MCP 的工程心智模型",
            "今天不是“又装一个 SDK”，而是把本地函数升级为可被 AI 客户端发现、理解、调用的 MCP server。你要能说清 server、client、tool schema、transport 和权限边界各自负责什么。",
            [
                _step(
                    "画清协议边界",
                    "MCP server 负责暴露 tools/resources/prompts；client/host 负责启动 server、做工具发现、把 tool schema 提供给模型，并在用户/策略允许时调用工具。模型不应该直接绕过 client 执行本地能力。",
                    [
                        f"mkdir notes\\day-{day.day_number} demos",
                        f"echo # Day {day.day_number} MCP runbook > notes\\day-{day.day_number}\\README.md",
                        f"echo server/client/tool schema/stdio transport >> notes\\day-{day.day_number}\\README.md",
                    ],
                    "验收：你能在笔记里用 5 句话说明 MCP server、client、工具发现、tool schema、stdio transport 的关系。",
                ),
                _step(
                    "明确今天的最小交付",
                    f"今天先做 hello MCP server，不急着接复杂客户端。最小产物是 {output}，验收标准是 server 能启动，并能在 Inspector 或客户端里看到工具列表。",
                    [],
                    f"验收：输出物路径写 {output}，并记录启动命令、工具名、输入 schema 和一次成功调用结果。",
                ),
            ],
        ),
        _section(
            "2. 只安装当天需要的 MCP SDK",
            "保持依赖最小化。先在学习仓库的虚拟环境里安装 MCP Python SDK，避免污染全局 Python；安装失败时记录版本、命令和完整错误。",
            [
                _step(
                    "创建或激活虚拟环境",
                    "Windows 使用 PowerShell；macOS 把激活命令换成 source .venv/bin/activate。若前面已经有 .venv，直接激活即可。",
                    [
                        "py -3.11 -m venv .venv",
                        ".\\.venv\\Scripts\\Activate.ps1",
                        "python -m pip install --upgrade pip",
                    ],
                    "验收：命令行前缀出现 (.venv)，且 python --version 显示 3.11+。",
                ),
                _step(
                    "安装 MCP Python SDK 和 CLI",
                    "安装官方 Python SDK 的 CLI extras。`mcp[cli]` 会提供开发调试命令，后面用 `mcp dev` 打开 MCP Inspector 做工具发现和调用验证。",
                    [
                        'python -m pip install "mcp[cli]"',
                        "python -c \"from mcp.server.fastmcp import FastMCP; print('FastMCP ok')\"",
                        "mcp --help",
                    ],
                    "验收：能导入 FastMCP，且 mcp --help 能输出命令帮助。",
                ),
            ],
        ),
        _section(
            "3. 写出最小 FastMCP server",
            "先暴露无副作用工具，证明协议和工具发现跑通。hello 工具不要读写真实文件，降低安全变量；文件工具放到第 16 天再做 allowlist。",
            [
                _step(
                    "创建 demos/06_mcp_hello.py",
                    "在文件中创建 FastMCP 实例，并用 `@mcp.tool` 暴露两个确定性工具：echo 用来验证输入输出，add 用来验证参数 schema。下面命令用 heredoc 写入文件，Windows PowerShell 可直接运行。",
                    [
                        "New-Item -ItemType Directory -Force demos | Out-Null",
                        "@'\nfrom mcp.server.fastmcp import FastMCP\n\nmcp = FastMCP(\"learning-tools\")\n\n@mcp.tool()\ndef echo(text: str) -> str:\n    \"\"\"Return the same text for MCP connectivity testing.\"\"\"\n    return text\n\n@mcp.tool()\ndef add(a: int, b: int) -> int:\n    \"\"\"Add two integers to verify tool schema and invocation.\"\"\"\n    return a + b\n\nif __name__ == \"__main__\":\n    mcp.run()\n'@ | Set-Content -Encoding UTF8 demos\\06_mcp_hello.py",
                        "python -m py_compile demos\\06_mcp_hello.py",
                    ],
                    "验收：文件存在，且 py_compile 无报错；代码里能看到 FastMCP、@mcp.tool、echo、add。",
                ),
                _step(
                    "先做静态自检",
                    "检查工具 docstring 是否能被 client 展示，参数类型是否明确，返回值是否可 JSON 序列化。MCP 的 tool schema 很依赖类型标注和说明文字。",
                    [
                        "Select-String -Path demos\\06_mcp_hello.py -Pattern \"FastMCP|@mcp.tool|def echo|def add\"",
                    ],
                    "验收：四个关键模式都能搜到；没有把文件系统、shell、真实 API Key 直接暴露成工具。",
                ),
            ],
        ),
        _section(
            "4. 用 Inspector 验证工具发现和调用",
            "真正的达标不是文件写完，而是 client 能通过 stdio transport 启动 MCP server、完成工具发现、看到 list_tools 结果，并成功调用工具。",
            [
                _step(
                    "启动 MCP Inspector",
                    "`mcp dev demos/06_mcp_hello.py` 会以开发模式启动 Inspector。浏览器打开后，连接本地 server，查看 Tools 列表。",
                    [
                        "mcp dev demos/06_mcp_hello.py",
                    ],
                    "验收：Inspector 中能看到 echo 和 add；这一步就是客户端工具发现，也可以在记录里写 list_tools 结果。",
                ),
                _step(
                    "执行一次工具调用",
                    "在 Inspector 里调用 echo(text='hello mcp')，再调用 add(a=1,b=2)。记录 request、response、工具名和 schema。若 Inspector 没打开，优先检查终端日志和端口提示。",
                    [
                        "echo Inspector 手动验证：echo('hello mcp') -> 'hello mcp' >> notes\\day-15\\README.md",
                        "echo Inspector 手动验证：add(1, 2) -> 3 >> notes\\day-15\\README.md",
                    ],
                    "验收：笔记中有两个工具调用结果，且说明 client discovery/list_tools 看到了哪些工具。",
                ),
            ],
        ),
        _section(
            "5. 补上客户端配置、安全边界和失败处理",
            "专业工程不是只让 demo 跑起来，还要让未来的你知道如何接入、如何限制权限、如何排查。第 15 天先记录边界，第 16 天再做文件工具。",
            [
                _step(
                    "写客户端配置草案",
                    "记录未来接入 MCP client 时需要的 server command、args、工作目录、transport。今天默认是本地 stdio transport，不需要 HTTP 服务，也不需要公网暴露。",
                    [
                        "echo client command: python demos/06_mcp_hello.py >> notes\\day-15\\README.md",
                        "echo transport: stdio >> notes\\day-15\\README.md",
                        "echo tools: echo, add >> notes\\day-15\\README.md",
                    ],
                    "验收：笔记里有客户端配置草案，至少包含 command、args/脚本路径、transport、工具名。",
                ),
                _step(
                    "定义安全边界",
                    "hello server 只允许无副作用工具。后续 read_file/write_file 必须使用 allowlist、路径归一化、只读优先、错误返回和日志，不能把任意文件系统或 shell 命令暴露给模型。",
                    [
                        "echo 安全边界：第15天只暴露 echo/add；文件读取等第16天再做 allowlist >> notes\\day-15\\README.md",
                    ],
                    "验收：能解释为什么第 15 天不直接做任意文件读取工具。",
                ),
                _step(
                    "失败处理清单",
                    "如果失败，按层定位：SDK 是否安装、FastMCP 是否能导入、server 是否 py_compile、`mcp dev` 是否启动、Inspector 是否连上、工具是否出现在 list_tools、调用参数是否符合 tool schema。",
                    [
                        "python -m pip show mcp",
                        "python -c \"from mcp.server.fastmcp import FastMCP; print('import ok')\"",
                        "python -m py_compile demos\\06_mcp_hello.py",
                        "mcp dev demos/06_mcp_hello.py",
                    ],
                    "验收：失败时提交完整命令、错误日志、Python 版本、mcp 版本、server 代码和 Inspector 状态，而不是只写“打不开”。",
                ),
            ],
        ),
        _section(
            "6. 提交证据和专业复盘",
            "最后把可运行证据留下来。完成说明要让别人判断：你是否真的理解 MCP 的协议边界，而不只是复制了一段 server 代码。",
            [
                _step(
                    "提交当天产物",
                    "提交 demos/06_mcp_hello.py 和 notes/day-15/README.md。复盘里写清：MCP 相比普通 function calling 的价值、client 如何发现工具、stdio transport 的含义、下一天文件工具需要的安全策略。",
                    [
                        "git status --short",
                        "git add demos\\06_mcp_hello.py notes\\day-15\\README.md",
                        'git commit -m "day 15 practice: mcp hello server"',
                    ],
                    "验收：git log --oneline -1 能看到当天 commit；平台输出物路径填写 demos/06_mcp_hello.py。",
                )
            ],
        ),
    ]


def _mcp_file_guidance(day: LearningDay) -> list[dict[str, Any]]:
    output = day.output_artifact or "demos/07_file_mcp_server.py"
    return [
        _section(
            "1. 把第 15 天 hello server 升级成受控文件工具",
            "今天的目标不是简单把 read_file 搬进 MCP，而是设计一个可被 client 发现、可被审计、不会越权读取的文件 MCP tool。重点是 tool schema、allowlist、路径归一化、错误返回和日志。",
            [
                _step(
                    "确认复用基础",
                    "先确认第 15 天 MCP SDK、FastMCP、mcp dev 和 Inspector 能工作。如果 hello server 没跑通，先回到第 15 天修协议基础，再做文件能力。",
                    [
                        'python -m pip install "mcp[cli]"',
                        "python -c \"from mcp.server.fastmcp import FastMCP; print('FastMCP ok')\"",
                        "mcp --help",
                    ],
                    "验收：FastMCP 能导入，mcp CLI 可用；你知道今天是在 hello server 基础上增加文件 tool。",
                ),
                _step(
                    "准备 allowlist 测试文件",
                    "只允许读取 data/day-16/ 下的样例文件。真实项目中，路径必须先 resolve，再确认仍在 allowlist 根目录内，不能相信模型传入的路径。",
                    [
                        "New-Item -ItemType Directory -Force data\\day-16 demos notes\\day-16 | Out-Null",
                        "Set-Content -Encoding UTF8 data\\day-16\\sample.txt 'MCP file tool safe sample'",
                        "echo 文件 MCP 工具安全设计 > notes\\day-16\\README.md",
                    ],
                    "验收：data/day-16/sample.txt 存在，笔记中写明只读 allowlist 根目录。",
                ),
            ],
        ),
        _section(
            "2. 编写 read_file MCP tool",
            "工具 schema 要让 client 和模型知道参数含义；实现要把相对路径归一化到 allowlist 根目录内，越权路径返回清晰错误，而不是抛出不可读堆栈。",
            [
                _step(
                    "创建文件 MCP server",
                    "下面示例只读 data/day-16。它演示 FastMCP、@mcp.tool、路径 resolve、allowlist 检查和结构化错误文本。",
                    [
                        "New-Item -ItemType Directory -Force demos | Out-Null",
                        "@'\nfrom pathlib import Path\nfrom mcp.server.fastmcp import FastMCP\n\nmcp = FastMCP(\"file-tools\")\nROOT = (Path(__file__).resolve().parents[1] / \"data\" / \"day-16\").resolve()\n\n@mcp.tool()\ndef read_file(relative_path: str) -> str:\n    \"\"\"Read a UTF-8 text file under the allowlisted data/day-16 directory.\"\"\"\n    target = (ROOT / relative_path).resolve()\n    if not str(target).startswith(str(ROOT)):\n        return \"ERROR: path is outside allowlist\"\n    if not target.exists() or not target.is_file():\n        return \"ERROR: file not found\"\n    return target.read_text(encoding=\"utf-8\")\n\nif __name__ == \"__main__\":\n    mcp.run()\n'@ | Set-Content -Encoding UTF8 demos\\07_file_mcp_server.py",
                        "python -m py_compile demos\\07_file_mcp_server.py",
                    ],
                    "验收：输出物 demos/07_file_mcp_server.py 存在，包含 read_file、allowlist、resolve 和 @mcp.tool。",
                )
            ],
        ),
        _section(
            "3. 用 Inspector 验证正常与异常路径",
            "只测 happy path 不够。文件工具必须同时验证正常文件、缺失文件和越权路径，证明安全边界不是口头设计。",
            [
                _step(
                    "启动并发现工具",
                    "用 `mcp dev` 打开 Inspector，确认 read_file 出现在 list_tools 中，查看参数 schema 是否只需要 relative_path。",
                    ["mcp dev demos/07_file_mcp_server.py"],
                    "验收：Inspector/list_tools 能看到 read_file，schema 中 relative_path 是字符串参数。",
                ),
                _step(
                    "执行三类调用",
                    "在 Inspector 中分别调用 sample.txt、missing.txt、../secrets.txt。记录每次 request/response，用来证明正常、缺失和越权都可解释。",
                    [
                        "echo read_file('sample.txt') 应返回样例文本 >> notes\\day-16\\README.md",
                        "echo read_file('missing.txt') 应返回 file not found >> notes\\day-16\\README.md",
                        "echo read_file('../secrets.txt') 应返回 outside allowlist >> notes\\day-16\\README.md",
                    ],
                    "验收：笔记里有三类测试结果；越权路径不会读取 allowlist 外文件。",
                ),
            ],
        ),
        _section(
            "4. 交付安全复盘",
            "文件 MCP tool 是安全敏感能力。完成说明里要写清为什么只读、为什么使用 allowlist、哪些错误会返回给 client、后续是否需要审计日志。",
            [
                _step(
                    "提交证据",
                    f"输出物填写 {output}。复盘中写明 client discovery、tool schema、allowlist 根目录、正常/异常/越权三类测试和遗留风险。",
                    [
                        "git status --short",
                        "git add demos\\07_file_mcp_server.py data\\day-16\\sample.txt notes\\day-16\\README.md",
                        'git commit -m "day 16 practice: file mcp tool"',
                    ],
                    "验收：git log --oneline -1 能看到当天 commit；平台输出物路径能打开。",
                )
            ],
        ),
    ]


def _mcp_orchestration_guidance(day: LearningDay) -> list[dict[str, Any]]:
    output = day.output_artifact or "demos/08_tool_orchestration.py"
    return [
        _section(
            "1. 明确多工具编排的决策模型",
            "今天不是堆更多工具，而是让 agent 在 File、SQL、MCP 等工具之间做可解释选择。核心是任务拆解、tool schema、调用顺序、失败重试和日志。",
            [
                _step(
                    "定义两步任务",
                    "设计一个必须先读文件再查 SQLite，或先查 SQL 再读文件的任务。任务必须能证明工具选择和顺序是必要的，而不是随便调用。",
                    [
                        "New-Item -ItemType Directory -Force demos notes\\day-17 data\\day-17 | Out-Null",
                        "echo 多工具编排任务设计 > notes\\day-17\\README.md",
                    ],
                    "验收：笔记中写清用户问题、预期工具顺序、每一步输入输出和失败时重试策略。",
                ),
                _step(
                    "定义可观察日志字段",
                    "每次工具调用至少记录 trace_id、tool_name、arguments、result_summary、error、duration_ms。没有日志，多工具系统无法排障。",
                    [
                        "echo trace_id/tool_name/arguments/result_summary/error/duration_ms >> notes\\day-17\\README.md",
                    ],
                    "验收：日志字段写进笔记，并解释每个字段排查什么问题。",
                ),
            ],
        ),
        _section(
            "2. 实现最小编排器",
            "先不用复杂 LangGraph，写一个确定性 planner：根据任务选择 file -> sql 或 sql -> file，调用后记录日志。模型决策可以后续替换，今天先证明编排边界。",
            [
                _step(
                    "创建 orchestration demo",
                    "最小实现可以用普通 Python 函数模拟工具调用，重点是工具选择、调用日志和失败重试，而不是一次性做完整平台。",
                    [
                        "@'\nfrom dataclasses import dataclass, asdict\nfrom time import perf_counter\n\n@dataclass\nclass ToolLog:\n    trace_id: str\n    tool_name: str\n    arguments: dict\n    result_summary: str\n    error: str | None\n    duration_ms: int\n\ndef call_tool(trace_id: str, tool_name: str, arguments: dict) -> ToolLog:\n    start = perf_counter()\n    try:\n        result = f\"{tool_name} ok\"\n        return ToolLog(trace_id, tool_name, arguments, result, None, int((perf_counter() - start) * 1000))\n    except Exception as exc:\n        return ToolLog(trace_id, tool_name, arguments, \"failed\", str(exc), int((perf_counter() - start) * 1000))\n\ndef run_task(question: str) -> list[ToolLog]:\n    trace_id = \"day17-demo\"\n    plan = [(\"file.read\", {\"path\": \"data/day-17/request.txt\"}), (\"sql.query\", {\"query\": \"select * from facts limit 3\"})]\n    return [call_tool(trace_id, name, args) for name, args in plan]\n\nif __name__ == \"__main__\":\n    for log in run_task(\"需要文件和数据库共同回答的问题\"):\n        print(asdict(log))\n'@ | Set-Content -Encoding UTF8 demos\\08_tool_orchestration.py",
                        "python demos\\08_tool_orchestration.py",
                    ],
                    "验收：输出物 demos/08_tool_orchestration.py 能运行，输出至少两条工具调用日志。",
                )
            ],
        ),
        _section(
            "3. 验证选择合理性和失败处理",
            "多工具 Agent 的专业性在于可复现、可解释、可回放。你要能回答：为什么选这个工具、为什么这个顺序、失败后怎么恢复。",
            [
                _step(
                    "做三组测试",
                    "测试 happy path、file 失败、sql 失败。失败时不要吞掉错误，要把错误写入日志并决定是否重试或降级。",
                    [
                        "python demos\\08_tool_orchestration.py > notes\\day-17\\tool_trace.log",
                        "Get-Content notes\\day-17\\tool_trace.log",
                    ],
                    "验收：日志可回放；每次调用都能看到 tool_name、arguments、result_summary、error。",
                ),
                _step(
                    "产品/架构复盘",
                    "从产品角度写清用户是否需要看到工具调用过程；从架构角度写清什么时候引入 LangGraph、什么时候保持简单编排器。",
                    [
                        "echo 产品复盘：用户需要看到哪些工具证据？ >> notes\\day-17\\README.md",
                        "echo 架构复盘：什么时候引入 LangGraph？ >> notes\\day-17\\README.md",
                    ],
                    "验收：复盘不是流水账，而是能解释多工具编排的取舍。",
                ),
            ],
        ),
        _section(
            "4. 提交证据",
            "交付时必须能证明任务可复现、日志可观察、失败可解释。只展示最终答案不算多工具编排合格。",
            [
                _step(
                    "提交当天产物",
                    f"输出物填写 {output}。完成说明包含运行命令、日志路径、两步工具调用、失败处理和下一步如何接入 LangGraph 或 MCP client。",
                    [
                        "git status --short",
                        "git add demos\\08_tool_orchestration.py notes\\day-17",
                        'git commit -m "day 17 practice: tool orchestration"',
                    ],
                    "验收：git log --oneline -1 能看到当天 commit；notes/day-17/tool_trace.log 可打开。",
                )
            ],
        ),
    ]


def _generic_guidance(day: LearningDay) -> list[dict[str, Any]]:
    profile = _domain_profile(day)
    return [
        _section(
            "1. 目标拆解与边界确认",
            "先把今天的概念、环境、输入、输出和验收标准拆开。专业学习不是照抄步骤，而是知道每一步在验证什么假设，并能从 AI 应用工程、架构和产品三个角度解释取舍。",
            [
                _step("学习目标", day.learning_goal, verify="验证命令：能用一句话解释今天练习要证明什么能力。"),
                _step("环境依赖", day.environment, verify="验证命令：列出今天会用到的依赖，确认没有提前引入无关工具。"),
                _step("专业能力锚点", profile["ability"], verify="验收：能把今天能力放进真实 AI 应用链路里，而不是只背术语。"),
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
                    f"{day.practice_steps}\n\n专业化执行要求：{profile['implementation']}",
                    commands=[
                        f"echo 目标：{day.learning_goal} >> notes\\day-{day.day_number}\\README.md",
                        f"echo 操作步骤：{day.practice_steps} >> notes\\day-{day.day_number}\\README.md",
                        *profile["commands"].splitlines(),
                    ],
                    verify="验证命令：当天 README 中能看到目标、步骤、关键观察。",
                )
            ],
        ),
        _section(
            "4. 质量验证与失败处理",
            "练习不是只做完，还要证明它做对。若失败，不要改状态为已完成，先记录失败模式和排查过程。",
            [
                _step(
                    "质量验证",
                    f"{day.acceptance_criteria}\n\n更高质量验收：{profile['validation']}",
                    verify="验证命令：能对照验收标准逐条说明完成/未完成，并给出可复查证据。",
                ),
                _step(
                    "失败处理",
                    f"{day.guidance}\n\n重点风险：{profile['risk']}",
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
                    f"输出物建议填写：{day.output_artifact}。完成说明写清产物路径、验证方式、遗留风险和下一步。\n\n产品/架构复盘：{profile['product']}",
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
