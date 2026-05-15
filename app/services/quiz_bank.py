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
    topic = day.topic
    environment = day.environment or "当天环境"
    output = day.output_artifact or "当天输出物"
    acceptance = day.acceptance_criteria or "验收标准"
    guidance = day.guidance or "练习指导"

    return [
        _single(
            day,
            1,
            f"场景：你接手第 {day.day_number} 天「{topic}」练习，开始动手前最应该先确认什么？",
            [
                f"确认学习目标、环境依赖和预期输出物：{output}",
                "先把所有相关工具都安装一遍，不管今天是否会用到",
                "直接写最终答案，不记录实验输入和失败过程",
                "只看资源标题，不做最小验证",
            ],
            f"专业学习要先锁定范围：目标是「{day.learning_goal}」，环境是「{environment}」，交付物是「{output}」。这样可以避免把排错范围无限扩大。",
        ),
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
