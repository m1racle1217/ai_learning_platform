import json
from typing import Any

from app.models import LearningDay, QuizQuestion

MIN_QUIZ_QUESTIONS = 8


def question_to_dict(question: QuizQuestion) -> dict[str, Any]:
    return {
        "id": question.id,
        "question_type": question.question_type,
        "prompt": question.prompt,
        "options": json.loads(question.options_json),
        "correct": json.loads(question.correct_answer_json),
        "explanation": question.explanation,
    }


def build_day_quiz(day: LearningDay, db_questions: list[QuizQuestion]) -> list[dict[str, Any]]:
    questions = [question_to_dict(question) for question in db_questions if question.day_id == day.id]
    if len(questions) >= MIN_QUIZ_QUESTIONS:
        return questions

    fallback_questions = _fallback_questions(day)
    used_prompts = {question["prompt"] for question in questions}
    for question in fallback_questions:
        if question["prompt"] not in used_prompts:
            questions.append(question)
            used_prompts.add(question["prompt"])
        if len(questions) >= MIN_QUIZ_QUESTIONS:
            break
    return questions


def _fallback_questions(day: LearningDay) -> list[dict[str, Any]]:
    if day.day_number == 1:
        return _day_one_questions(day)
    if _is_mcp_day(day):
        if "文件" in (day.topic or "") or "read_file" in _context(day):
            return _mcp_file_questions(day)
        if "编排" in (day.topic or "") or "orchestration" in _context(day):
            return _mcp_orchestration_questions(day)
        return _mcp_questions(day)
    topic = day.topic
    environment = day.environment or "当天环境"
    output = day.output_artifact or "当天输出物"
    acceptance = day.acceptance_criteria or "验收标准"
    guidance = day.guidance or "练习指导"

    return [
        _domain_first_question(day, topic, environment, output),
        _single(
            day,
            2,
            "排查：练习运行结果不符合预期，最专业的第一轮排查动作是什么？",
            [
                f"按当天卡点提示逐项排查，并记录输入、输出、版本和复现步骤：{guidance[:48]}",
                "马上更换技术路线，让问题消失",
                "只截图最终页面，不保留中间证据",
                "跳过练习，把状态改成已完成",
            ],
            "排查不是猜答案，而是缩小变量。记录输入、输出、版本、路径和已尝试步骤，后续才能复盘和求助。",
        ),
        _single(
            day,
            3,
            "交付：今天最小合格输出应该是什么？",
            [
                output,
                "一段没有上下文的学习感想",
                "只保存视频链接，不产生自己的输出",
                "一个无法打开、无法复查的临时文件",
            ],
            f"输出物必须能被复查、复现或继续迭代。今天的交付锚点是「{output}」，不是单纯看完材料。",
        ),
        _single(
            day,
            4,
            "质量验收：完成后应该优先用哪条标准判断是否真的达标？",
            [
                acceptance,
                "只要界面或文件看起来很多就算完成",
                "只要运行过一次命令，无论结果如何都算完成",
                "凭感觉判断，不需要验收记录",
            ],
            f"专业验收要回到可观察标准：{acceptance}。如果不能解释为什么达标，就应该标为需要复盘。",
        ),
        _single(
            day,
            5,
            "场景：你想把今天内容写进作品集或面试复盘，最有价值的记录是什么？",
            [
                "问题背景、关键决策、失败记录、验证结果和最终输出路径",
                "只写自己看了哪些视频",
                "只写工具名称，不写为什么这么选",
                "只保存一张截图，不解释如何复现",
            ],
            "真正能体现能力的是决策链和证据链：为什么这么做、怎么验证、遇到什么风险、如何修正。",
        ),
        _single(
            day,
            6,
            "风险：当天环境依赖应该如何处理最稳妥？",
            [
                f"只安装并记录当天需要的依赖：{environment}",
                "为了显得专业，把所有框架和数据库都装上",
                "不记录版本，后面坏了再说",
                "把真实 API Key 直接写进代码仓库",
            ],
            "依赖越多，故障面越大。专业做法是最小依赖、版本可追踪、密钥不入库。",
        ),
        _multiple(
            day,
            7,
            "评估：哪些证据能说明你真正理解了今天内容？",
            [
                "能解释关键概念如何影响输出质量",
                "能用固定输入复现一次结果",
                "能指出至少一个失败模式和排查方法",
                "只记住正确选项，不知道为什么",
            ],
            ["能解释关键概念如何影响输出质量", "能用固定输入复现一次结果", "能指出至少一个失败模式和排查方法"],
            "深层学习不是背术语，而是能预测影响、复现实验、解释失败原因。",
        ),
        _multiple(
            day,
            8,
            "提交：哪些内容应该写进当天练习完成说明？",
            [
                "完成了什么输出物以及路径在哪里",
                "如何验证它达到了验收标准",
                "遇到的卡点、报错和处理方式",
                "一句“已完成”，不写证据",
            ],
            ["完成了什么输出物以及路径在哪里", "如何验证它达到了验收标准", "遇到的卡点、报错和处理方式"],
            "完成说明应该让未来的你或别人能判断：产物在哪里、怎么验证、风险是否处理过。",
        ),
        _single(
            day,
            9,
            "什么时候适合把当天状态改成「需要复盘」？",
            [
                "能描述问题但输出物或验收标准还没达成",
                "已经完整完成并复查过",
                "刚打开页面还没开始",
                "只是想改变进度数字",
            ],
            "需要复盘代表你已经推进过，但仍有缺口要回看。",
        ),
        _single(
            day,
            10,
            "最推荐的学习节奏是哪一种？",
            [
                "资源学习后立刻做最小实践，再用小测巩固",
                "连续刷很多资源但不动手",
                "只做题不看当天材料",
                "把所有任务拖到最后一天",
            ],
            "这个平台的设计就是让资源、实践、小测互相咬合。",
        ),
    ]


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


def _is_mcp_day(day: LearningDay) -> bool:
    return "mcp" in _context(day)


def _domain_terms(day: LearningDay) -> dict[str, str]:
    text = _context(day)
    if any(keyword in text for keyword in ["rag", "向量", "知识库", "检索", "chunk"]):
        return {
            "scenario": "用户投诉知识库答案有引用但仍然答错。作为 AI 应用开发工程师，你优先拆哪条链路？",
            "answer": "按 ingestion -> chunk -> embedding -> retrieval -> rerank -> answer -> citation 分层定位，并用固定问题集复现",
            "bad1": "直接调高 temperature，让回答看起来更自然",
            "bad2": "马上微调模型，因为知识库答错一定是模型能力不够",
            "bad3": "只换一个更大的向量库，不检查原始文档和召回片段",
            "explanation": "RAG 的专业排查要先分层：文档是否进库、chunk 是否合适、召回是否命中、排序是否正确、生成是否忠于证据。否则很容易把检索问题误判成模型问题。",
        }
    if any(keyword in text for keyword in ["prompt", "structured output", "few-shot", "react"]):
        return {
            "scenario": "同一个 prompt 在少数样例上表现变好，但线上输入变多后质量不稳定。你应该如何判断它是否真的改进？",
            "answer": "建立固定测试集和 rubric，对比两个 prompt 版本的正确率、格式错误、遗漏和幻觉",
            "bad1": "只保留表现最好的一个样例，作为改 prompt 成功的证据",
            "bad2": "继续加长 prompt，直到模型看起来更听话",
            "bad3": "删除所有约束，让模型自由发挥",
            "explanation": "Prompt 是接口契约，质量要靠 eval 判断。专业做法是固定输入、固定评分维度、比较版本差异，而不是凭单个漂亮输出下结论。",
        }
    if any(keyword in text for keyword in ["function", "tool calling", "文件工具", "sql 工具", "工具安全"]):
        return {
            "scenario": "你要把一个本地函数暴露给模型使用。最关键的工程边界是什么？",
            "answer": "用严格 tool schema、allowlist、错误返回和调用日志约束真实执行，模型只提出工具调用意图",
            "bad1": "让模型直接拼接 shell 命令执行",
            "bad2": "把任意文件路径和任意 SQL 都开放给模型",
            "bad3": "只要工具调用成功一次，就不需要异常路径测试",
            "explanation": "工具调用的风险在执行边界。模型输出不是权限授权，程序必须负责 schema 校验、权限限制、错误处理和审计日志。",
        }
    if any(keyword in text for keyword in ["langgraph", "state", "planner", "executor", "human-in-the-loop", "multi-agent"]):
        return {
            "scenario": "一个 Agent 任务经常循环、状态变乱、难以复现。你应优先补哪类设计？",
            "answer": "定义 state schema、节点职责、边条件、终止条件和每步 state diff 日志",
            "bad1": "把所有规则写进一个更长的系统提示词",
            "bad2": "增加更多 agent，让系统自己协商",
            "bad3": "隐藏中间状态，只展示最终答案",
            "explanation": "LangGraph 的价值是把 Agent 行为显式化。状态、节点、边和终止条件清晰，才有可调试性、可测试性和产品级稳定性。",
        }
    if any(keyword in text for keyword in ["memory", "记忆", "recall"]):
        return {
            "scenario": "用户说系统记住了错误偏好，后续回答持续被污染。你应先检查什么？",
            "answer": "检查记忆写入策略、记忆 schema、召回条件、过期/删除机制和召回证据",
            "bad1": "把所有历史对话都永久写入长期记忆",
            "bad2": "只提高 top_k，让更多记忆进入上下文",
            "bad3": "告诉用户这是模型幻觉，不处理存储层",
            "explanation": "Memory 不是聊天记录堆积，而是受策略约束的长期状态。错误写入、过度召回和缺少删除机制都会造成持续污染。",
        }
    if "dify" in text:
        return {
            "scenario": "Dify 工作流能跑通，但你要判断它是否适合作为长期方案。你最应该比较什么？",
            "answer": "比较节点可观测性、知识库效果、导出迁移、密钥管理、失败处理和与代码版实现的差异",
            "bad1": "只看界面搭建速度，越快越适合长期核心链路",
            "bad2": "不记录节点输入输出，完全相信可视化编排",
            "bad3": "把所有业务逻辑都写进不可版本管理的节点备注里",
            "explanation": "Dify 很适合快速验证，但产品化还要看可维护、可迁移、可观测和权限治理。对照代码版实现能帮助判断取舍。",
        }
    if any(keyword in text for keyword in ["微调", "lora", "qlora", "sft", "finetune", "adapter"]):
        return {
            "scenario": "团队想用微调解决知识更新和格式不稳定两个问题。你作为 AI 架构师应如何判断？",
            "answer": "先用 Prompt/RAG/微调决策矩阵拆问题，再用固定 eval 比较 baseline 与候选方案收益",
            "bad1": "只要有训练数据，就默认微调",
            "bad2": "把知识库更新问题全部交给 LoRA",
            "bad3": "训练后只展示一个成功样例，不比较退化样本",
            "explanation": "微调不是默认解。知识更新通常优先 RAG，格式与风格可先 Prompt/结构化输出，稳定行为迁移才考虑 SFT/LoRA，并且必须有训练前后评估。",
        }
    return {
        "scenario": f"你要把「{day.topic}」放进真实 AI 应用项目。最专业的第一步是什么？",
        "answer": f"把目标、依赖、最小实现、验收证据和输出物 {day.output_artifact} 拆成可复查清单",
        "bad1": "先堆更多工具和资料，等看完再动手",
        "bad2": "只写学习感想，不留下可运行产物",
        "bad3": "跳过验收，用主观感觉判断完成",
        "explanation": "专业学习要把概念转成可交付证据：产物存在、路径可打开、验证能复现、失败有记录、复盘能解释架构和产品取舍。",
    }


def _domain_first_question(
    day: LearningDay,
    topic: str,
    environment: str,
    output: str,
) -> dict[str, Any]:
    terms = _domain_terms(day)
    return _single(
        day,
        1,
        terms["scenario"],
        [
            terms["answer"],
            terms["bad1"],
            terms["bad2"],
            terms["bad3"],
        ],
        f"{terms['explanation']} 本日范围是「{topic}」，依赖是「{environment}」，输出物是「{output}」。",
    )


def _mcp_questions(day: LearningDay) -> list[dict[str, Any]]:
    return [
        _single(
            day,
            1,
            "架构判断：为什么要把本地函数包装成 MCP server，而不是只在代码里写一个普通函数？",
            [
                "MCP server 提供标准协议边界，让 client 通过工具发现获取 tool schema，并在受控 transport 上调用工具",
                "MCP 会让模型绕过应用权限，直接执行本地函数",
                "MCP 的主要价值是让 prompt 更长，从而提升推理能力",
                "只要用了 MCP，就不需要写工具参数校验和日志",
            ],
            "MCP 的价值在协议化和复用：server 暴露能力，client 发现并调用，模型只参与决策。权限、schema、日志和错误处理仍然是工程责任。",
        ),
        _single(
            day,
            2,
            "工具发现：在 MCP 链路里，谁负责发现 echo/add 这样的工具并读取 tool schema？",
            [
                "MCP client/host 启动 server 后通过协议执行工具发现，读取 list_tools/tool schema，再提供给模型使用",
                "模型直接扫描你的 Python 文件并自动执行所有函数",
                "用户手动把每个函数源码复制到聊天窗口里",
                "数据库自动把函数注册成工具",
            ],
            "专业理解是 client discovery：client/host 管理 server 进程、transport 和工具列表，模型看到的是经过 host 管理后的工具描述。",
        ),
        _single(
            day,
            3,
            "实现细节：使用 Python SDK 写 hello MCP server 时，哪种代码结构最符合今天目标？",
            [
                "创建 FastMCP 实例，用 @mcp.tool 暴露带类型标注和 docstring 的 echo/add，再用 mcp.run() 启动",
                "写一个无限循环 print，让 Inspector 自己猜函数含义",
                "把 DEEPSEEK_API_KEY 写进 server 文件，方便所有 client 调用",
                "直接开放任意 shell 命令工具，证明 MCP 很强",
            ],
            "FastMCP、@mcp.tool、类型标注和 docstring 会形成清晰 tool schema。hello 阶段应选择无副作用工具，避免把安全问题混进协议验证。",
        ),
        _single(
            day,
            4,
            "transport 判断：第 15 天本地 hello server 默认优先使用 stdio transport 的原因是什么？",
            [
                "stdio 适合本地 client 启动和管理 server 进程，调试简单，不需要暴露 HTTP 服务或公网端口",
                "stdio 会自动加密所有业务数据，所以不需要权限设计",
                "stdio 可以让模型直接访问任意本地文件",
                "stdio 是浏览器页面样式的一种配置",
            ],
            "stdio transport 是本地进程通信方式，适合学习和桌面客户端集成。它降低服务化复杂度，但不替代权限、allowlist 和日志。",
        ),
        _multiple(
            day,
            5,
            "验收：哪些证据能说明第 15 天 MCP SDK 搭建真的达标？",
            [
                "mcp[cli] 安装成功，FastMCP 能导入",
                "demos/06_mcp_hello.py 能 py_compile，且包含 @mcp.tool",
                "mcp dev demos/06_mcp_hello.py 能打开 Inspector，并能看到 list_tools 中的 echo/add",
                "只写一句“hello MCP server 能启动”，不提供命令和工具列表",
            ],
            [
                "mcp[cli] 安装成功，FastMCP 能导入",
                "demos/06_mcp_hello.py 能 py_compile，且包含 @mcp.tool",
                "mcp dev demos/06_mcp_hello.py 能打开 Inspector，并能看到 list_tools 中的 echo/add",
            ],
            "MCP 验收必须覆盖依赖、代码、server 启动、client 工具发现和一次调用结果。只说启动成功无法证明 tool schema 或 discovery 正常。",
        ),
        _single(
            day,
            6,
            "安全边界：为什么第 15 天 hello server 不建议直接暴露任意 read_file/write_file 工具？",
            [
                "文件工具涉及路径归一化、allowlist、只读优先、错误返回和审计日志，应该在协议跑通后单独设计",
                "MCP server 天生禁止读取文件，所以永远做不了文件工具",
                "只要工具叫 read_file，就不会有安全风险",
                "让模型自己判断哪些路径安全即可",
            ],
            "文件系统是高风险边界。AI 架构师要先把无副作用 hello 工具跑通，再为文件工具设计 allowlist、权限和日志。",
        ),
        _single(
            day,
            7,
            "产品判断：什么时候 MCP 比项目内部临时 function calling 更值得引入？",
            [
                "当同一组本地/企业工具需要被多个 client 复用，并且需要标准化 discovery、schema 和权限边界时",
                "当只有一个一次性脚本，且不会被任何客户端复用时",
                "当你想避免写验收和日志时",
                "当模型回答不够长时",
            ],
            "产品经理视角要看复用、集成和维护成本。MCP 适合把工具能力标准化给多个 host/client，而不是为了炫技替代所有简单函数。",
        ),
        _single(
            day,
            8,
            "排障：Inspector 里看不到 echo 工具时，最合理的排查顺序是什么？",
            [
                "检查 mcp[cli] 版本、FastMCP 导入、py_compile、mcp dev 启动日志、@mcp.tool 装饰器、tool schema 和 transport 配置",
                "立刻重装系统，因为工具没显示一定是系统坏了",
                "把函数名改成中文，让模型更容易理解",
                "跳过 Inspector，只要 Python 文件存在就算完成",
            ],
            "排障要按层缩小变量：依赖 -> 代码语法 -> server 启动 -> transport -> client discovery -> 工具 schema。这样才能定位真正失败点。",
        ),
        _multiple(
            day,
            9,
            "架构复盘：完成今天练习后，哪些结论应该写进 notes/day-15/README.md？",
            [
                "MCP server 和 client 的职责边界",
                "stdio transport、工具发现和 list_tools 观察结果",
                "暴露文件/SQL 等有副作用工具前需要的 allowlist 和审计策略",
                "只写“今天看懂了 MCP”，不记录证据",
            ],
            [
                "MCP server 和 client 的职责边界",
                "stdio transport、工具发现和 list_tools 观察结果",
                "暴露文件/SQL 等有副作用工具前需要的 allowlist 和审计策略",
            ],
            "复盘要服务于后续工程：第 16 天文件 MCP 工具、第 17 天多工具编排都会依赖今天的协议边界、安全边界和调试证据。",
        ),
        _single(
            day,
            10,
            "专业取舍：第 15 天如果 mcp dev 因环境问题暂时跑不起来，最合格的降级交付是什么？",
            [
                "保留 server 代码、安装/启动日志、失败截图或错误文本、已验证的 FastMCP 导入结果，并写清下一步排查计划",
                "把状态改成已完成，不记录失败原因",
                "改学微调，因为 MCP 太难",
                "删除所有文件，等以后重新开始",
            ],
            "降级不是糊弄，而是保留证据链。能说明失败发生在哪一层、已经排除了哪些变量，才算专业学习。",
        ),
    ]


def _mcp_file_questions(day: LearningDay) -> list[dict[str, Any]]:
    return [
        _single(
            day,
            1,
            "架构判断：把 read_file 改成 MCP tool 时，最重要的安全边界是什么？",
            [
                "只允许读取 allowlist 根目录内文件，并对路径做 resolve/归一化后再判断",
                "让模型自己判断哪些文件路径安全",
                "只要函数名叫 read_file，就不会写文件，所以不需要限制路径",
                "把用户传入路径直接拼接到 open() 里，失败再说",
            ],
            "文件工具是高风险能力。MCP 标准化的是调用协议，不会自动替你做文件权限控制，allowlist、resolve 路径归一化和错误返回必须由 server 实现。",
        ),
        _single(
            day,
            2,
            "tool schema：read_file 的参数设计为什么优先使用 relative_path，而不是 absolute_path？",
            [
                "relative_path 更容易约束到 allowlist 根目录，减少泄露任意本地路径的风险",
                "absolute_path 更长，看起来更专业",
                "模型只能理解绝对路径",
                "MCP 禁止字符串参数",
            ],
            "相对路径配合固定 ROOT 更容易做边界校验。绝对路径会扩大攻击面，也让跨机器复现更困难。",
        ),
        _single(
            day,
            3,
            "工具发现：Inspector/list_tools 里能看到 read_file，但调用失败，最先看什么？",
            [
                "查看参数 schema、传入 relative_path、server 日志和错误返回是否说明 file not found/越权",
                "直接重装 MCP SDK",
                "把 allowlist 删除，让任意路径都能成功",
                "跳过异常测试，只保留成功截图",
            ],
            "工具能被发现只证明 schema 暴露成功，不代表权限和业务逻辑正确。调用失败要继续看参数、路径和 server 错误。",
        ),
        _multiple(
            day,
            4,
            "验收：哪些测试必须覆盖，才能说明文件 MCP tool 不是只跑通 happy path？",
            [
                "读取 allowlist 内存在的 sample.txt",
                "读取 allowlist 内不存在的 missing.txt",
                "尝试 ../secrets.txt 这类越权路径",
                "只在 README 写一句工具能用",
            ],
            [
                "读取 allowlist 内存在的 sample.txt",
                "读取 allowlist 内不存在的 missing.txt",
                "尝试 ../secrets.txt 这类越权路径",
            ],
            "文件工具验收必须包含正常、缺失和越权三类路径。否则你只能证明能读一个文件，不能证明安全边界有效。",
        ),
        _single(
            day,
            5,
            "产品判断：如果用户要求文件工具能读取整个电脑，你应该如何回应？",
            [
                "说明风险，先限定业务目录和只读能力，必要时增加用户确认、审计日志和权限配置",
                "直接开放整个磁盘，用户体验最好",
                "把所有失败都包装成成功，避免用户焦虑",
                "让模型自己决定是否读取敏感文件",
            ],
            "AI 产品经理要平衡能力和风险。文件读取必须有范围、确认、审计和失败提示，不应默认给模型全盘权限。",
        ),
        _single(
            day,
            6,
            "排障：read_file('../secrets.txt') 居然返回了文件内容，这说明什么？",
            [
                "allowlist 校验有漏洞，路径 resolve 后没有确认仍位于 ROOT 下",
                "MCP Inspector 显示错误，应该忽略",
                "这是正常行为，说明工具很强",
                "只要没有写文件，就不算安全问题",
            ],
            "越权读取是严重安全问题。路径校验必须基于规范化后的绝对路径，并确认 target 在允许根目录内。",
        ),
        _single(
            day,
            7,
            "架构复盘：文件 MCP tool 的错误返回应更偏向哪种形式？",
            [
                "返回可被 client 和用户理解的结构化错误/清晰错误文本，同时 server 侧保留日志",
                "把 Python 堆栈完整暴露给最终用户",
                "吞掉错误并返回空字符串",
                "随机换一个文件读取",
            ],
            "错误设计会影响 Agent 的下一步决策。清晰错误能帮助 client 决定重试、换参数或提示用户，而不是制造幻觉式结果。",
        ),
        _single(
            day,
            8,
            "交付：第 16 天最能体现工程专业性的输出是什么？",
            [
                "demos/07_file_mcp_server.py、三类调用证据、allowlist 说明、失败处理和安全复盘",
                "只提交一个能读取 sample.txt 的截图",
                "只收藏 MCP 教程链接",
                "把 Day 15 hello server 原样复制一遍",
            ],
            "第 16 天的能力点是安全文件工具，不是重复 hello server。交付必须证明 discovery、调用和安全边界都成立。",
        ),
    ]


def _mcp_orchestration_questions(day: LearningDay) -> list[dict[str, Any]]:
    return [
        _single(
            day,
            1,
            "架构判断：多工具编排的核心难点是什么？",
            [
                "让 agent 可解释地选择工具、确定调用顺序、记录每次调用，并在失败时可重试或降级",
                "把所有工具都暴露出去，数量越多越智能",
                "隐藏中间调用，只展示最终答案",
                "让模型直接执行任意 SQL 和 shell",
            ],
            "多工具系统真正难的是可控性和可观察性。工具多不等于能力强，选择依据、调用日志和失败处理才是工程质量。",
        ),
        _single(
            day,
            2,
            "日志设计：为什么 trace_id、tool_name、arguments、result_summary、error、duration_ms 都重要？",
            [
                "它们能把一次任务的工具链路串起来，支持复现、排障、性能分析和安全审计",
                "这些字段只是为了让日志看起来更长",
                "只记录最终答案就足够",
                "模型会自动记住所有工具调用，不需要日志",
            ],
            "没有 trace 和结构化日志，多工具 Agent 出错时很难判断是选错工具、参数错、工具失败还是生成阶段误读。",
        ),
        _single(
            day,
            3,
            "产品判断：什么时候用户需要看到工具调用证据？",
            [
                "当答案涉及事实、文件、数据库或业务决策时，应展示摘要级证据和来源，避免暴露敏感细节",
                "任何时候都隐藏工具证据，用户只看结论",
                "把完整参数和敏感路径全部展示给用户",
                "只有开发者才需要证据，产品不需要",
            ],
            "产品经理要设计可解释性。用户需要足够证据建立信任，但敏感参数和内部路径要做脱敏或摘要。",
        ),
        _multiple(
            day,
            4,
            "验收：哪些现象说明多工具任务可复现、可观察？",
            [
                "同一固定输入能得到同一工具顺序或可解释的分支",
                "每次工具调用有 trace 日志",
                "失败路径能看到错误并触发重试/降级策略",
                "最终答案看起来像真的即可",
            ],
            [
                "同一固定输入能得到同一工具顺序或可解释的分支",
                "每次工具调用有 trace 日志",
                "失败路径能看到错误并触发重试/降级策略",
            ],
            "多工具验收不能只看最终答案。可复现输入、调用日志和失败策略才证明系统可工程化。",
        ),
        _single(
            day,
            5,
            "架构取舍：第 17 天为什么可以先不用 LangGraph？",
            [
                "今天重点是理解多工具选择、调用日志和失败处理；确定性编排器能先验证边界，后续再引入状态机",
                "LangGraph 永远不适合多工具 Agent",
                "不用 LangGraph 就不能记录日志",
                "只要用了 MCP，就不需要编排逻辑",
            ],
            "专业路线是先验证最小闭环，再引入复杂框架。状态机适合复杂流程，但不能替代对工具边界和日志的理解。",
        ),
        _single(
            day,
            6,
            "排障：最终答案错误，但日志显示 file.read 结果正确、sql.query 参数错误。根因更可能在哪里？",
            [
                "planner/工具选择或参数生成阶段，而不是文件工具本身",
                "文件工具一定坏了",
                "用户问题一定不合法",
                "只要最终错了，就必须换大模型",
            ],
            "结构化日志的价值就是分层定位。工具结果正确而 SQL 参数错误，说明问题在规划或参数生成。",
        ),
        _single(
            day,
            7,
            "安全边界：多工具编排中为什么不能让模型自由组合任意工具？",
            [
                "组合后的副作用可能放大，必须按工具风险分级、设置确认点、限制参数和记录审计日志",
                "模型组合越自由越安全",
                "只要每个工具单独安全，组合一定安全",
                "多工具系统不需要权限设计",
            ],
            "工具组合会产生新风险，例如先读敏感信息再写入外部系统。架构上要做风险分级和人类确认。",
        ),
        _single(
            day,
            8,
            "交付：第 17 天完成说明里最不能缺什么？",
            [
                "两步以上工具调用日志、选择依据、失败处理、运行命令和输出物 demos/08_tool_orchestration.py",
                "一句“多工具任务可复现”",
                "只提交最终答案截图",
                "只写以后要接 LangGraph",
            ],
            "第 17 天的核心证据是 traceable orchestration。没有调用日志和选择依据，就无法证明多工具编排真的可控。",
        ),
    ]


def _day_one_questions(day: LearningDay) -> list[dict[str, Any]]:
    return [
        _single(
            day,
            1,
            "场景：你要在一台新电脑上开始 70 天 AI 应用学习。最专业的第一步是什么？",
            [
                "先确认 Python、Git、VS Code、pip/uv 的版本和命令可用，再创建学习仓库",
                "先安装 Docker、Dify、向量数据库，把后面可能用到的工具全部装完",
                "先复制别人的完整项目，能运行就不需要理解目录结构",
                "只创建一个空文件夹，等后面遇到问题再补环境",
            ],
            "专业交付不是堆工具，而是先建立可复现的最小环境。第 1 天的风险是 PATH、版本、目录混乱，所以先验证基础命令再建仓库。",
        ),
        _multiple(
            day,
            2,
            "你准备提交第 1 天练习。哪些证据能证明环境不是“口头完成”？",
            [
                "python --version 或 python3 --version 的输出",
                "git --version 的输出",
                "git log --oneline -1 能看到第一次 commit",
                "只说“我感觉装好了”",
            ],
            [
                "python --version 或 python3 --version 的输出",
                "git --version 的输出",
                "git log --oneline -1 能看到第一次 commit",
            ],
            "小白也要从第一天建立工程习惯：验证命令、提交记录、输出物路径都是可复查证据，这比主观描述可靠。",
        ),
        _single(
            day,
            3,
            "排查：终端输入 python --version 提示命令不存在，最合理的处理顺序是什么？",
            [
                "先重启终端，再尝试 py --version 或 python3 --version，仍失败再检查 PATH/安装选项",
                "立刻卸载所有软件，重新安装系统",
                "跳过 Python，直接学习 RAG 和 Agent",
                "把报错删掉，只在完成说明里写已经安装",
            ],
            "排查要从低成本动作开始：新终端、替代命令、PATH、安装器选项。记录完整报错能降低后续求助成本。",
        ),
        _single(
            day,
            4,
            "场景：你创建了 README.md、.env.example、.gitignore。哪一个文件绝对不应该提交真实密钥？",
            [
                ".env",
                "README.md",
                ".gitignore",
                "notes/troubleshooting.md",
            ],
            ".env 可能保存 DEEPSEEK_API_KEY 等真实密钥，应被 .gitignore 排除；.env.example 只放变量名和占位值，用于说明配置格式。",
        ),
        _multiple(
            day,
            5,
            "关于学习仓库目录设计，哪些判断是专业的？",
            [
                "demos 放可运行代码，notes 放笔记，evals 放评测，data 放测试数据",
                "README 写明每个目录的用途，方便未来复盘和展示",
                "所有文件都堆在桌面，等项目大了再整理",
                "把 API Key 直接写进 README，方便以后复制",
            ],
            [
                "demos 放可运行代码，notes 放笔记，evals 放评测，data 放测试数据",
                "README 写明每个目录的用途，方便未来复盘和展示",
            ],
            "目录结构是后续 Prompt、RAG、Agent、评测实验的地基。早期结构清晰，后面才能复现、扩展和展示。",
        ),
        _single(
            day,
            6,
            "验证：执行 git status --short 后看到 README.md、.env.example、.gitignore 都是未跟踪文件，下一步应该做什么？",
            [
                "确认没有 .env 等敏感文件后，执行 git add . 和 git commit",
                "直接删除 .git 文件夹",
                "不用提交，截图文件夹就算完成",
                "把所有系统缓存文件也一起提交",
            ],
            "提交前先检查风险，尤其是密钥、缓存、虚拟环境。确认干净后再 add/commit，这是基本工程流程。",
        ),
        _single(
            day,
            7,
            "交付：第 1 天的输出物路径应该优先填写什么？",
            [
                "ai-agent-learning 仓库目录或 README.md 的真实本地路径",
                "Python 官网地址",
                "一个还不存在的未来项目链接",
                "随便写“完成了”",
            ],
            "平台的自动检查会验证路径是否存在。真实路径让练习从“学习感受”变成“可检查交付”。",
        ),
        _single(
            day,
            8,
            "风险判断：为什么第 1 天不建议安装 Docker、Dify、RAG、向量数据库？",
            [
                "它们不是今天最小闭环必需品，提前安装会增加变量和排错成本",
                "这些工具完全没用，后面永远不会学",
                "因为 Python 项目不能使用 Docker",
                "因为 Git 必须等 RAG 学完才能用",
            ],
            "专业学习不是越早装越好，而是在需要时引入依赖。先保证 Python/Git/VS Code/包管理稳定，再逐步叠加复杂工具。",
        ),
    ]


def _single(
    day: LearningDay,
    index: int,
    prompt: str,
    options: list[str],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"fallback-{day.day_number}-{index}",
        "question_type": "single",
        "prompt": prompt,
        "options": options,
        "correct": [options[0]],
        "explanation": explanation,
    }


def _multiple(
    day: LearningDay,
    index: int,
    prompt: str,
    options: list[str],
    correct: list[str],
    explanation: str,
) -> dict[str, Any]:
    return {
        "id": f"fallback-{day.day_number}-{index}",
        "question_type": "multiple",
        "prompt": prompt,
        "options": options,
        "correct": correct,
        "explanation": explanation,
    }
