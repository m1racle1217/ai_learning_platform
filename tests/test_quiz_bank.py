import json

from app.models import LearningDay, Module, QuizQuestion
from app.services.quiz_bank import build_day_quiz


def test_build_day_quiz_adds_at_least_eight_questions():
    module = Module(id=1, name="RAG / 知识库 Agent", sort_order=1, description="")
    day = LearningDay(
        id=1,
        day_number=3,
        module_id=module.id,
        module=module,
        stage="理论基础篇",
        topic="RAG 基础判断",
        environment="Python + DeepSeek API",
        learning_goal="理解检索增强生成适合知识更新场景",
        resources_text="",
        resource_hint="",
        practice_steps="准备文档，切分，检索，再生成答案",
        acceptance_criteria="能说明 RAG 与微调的差异",
        output_artifact="一个最小知识库问答 demo",
        status="未开始",
        guidance="先检查数据，再检查检索结果",
    )

    questions = build_day_quiz(day, [])

    assert len(questions) >= 8
    assert all(question["prompt"] for question in questions)
    assert all(question["options"] for question in questions)


def test_day_one_quiz_does_not_include_future_rag_topics():
    module = Module(id=1, name="最小环境与学习仓库", sort_order=1, description="")
    day = LearningDay(
        id=1,
        day_number=1,
        module_id=module.id,
        module=module,
        stage="最小环境",
        topic="学习仓库与基础环境",
        environment="Python 3.11+、Git、VS Code、uv/pip；不用 Docker/Dify/RAG",
        learning_goal="只搭最小开发环境，后续工具用到再搭",
        resources_text="",
        resource_hint="",
        practice_steps="创建仓库并提交第一次 commit",
        acceptance_criteria="能提交第一次 commit；README 写明目录用途",
        output_artifact="repo + README.md",
        status="未开始",
        guidance="版本号、路径、环境变量、网络代理、终端是否重启。",
    )

    questions = build_day_quiz(day, [])
    text = "\n".join(question["prompt"] + "\n" + "\n".join(question["options"]) for question in questions)

    assert "LoRA" not in text
    assert "微调" not in text
    assert "知识更新类问题" not in text


def test_module_level_questions_are_not_used_as_day_quiz_fallback():
    module = Module(id=1, name="最小环境与学习仓库", sort_order=1, description="")
    day = LearningDay(
        id=1,
        day_number=1,
        module_id=module.id,
        module=module,
        stage="最小环境",
        topic="学习仓库与基础环境",
        environment="Python 3.11+、Git、VS Code、uv/pip",
        learning_goal="只搭最小开发环境",
        resources_text="",
        resource_hint="",
        practice_steps="创建仓库",
        acceptance_criteria="能提交 commit",
        output_artifact="repo + README.md",
        status="未开始",
        guidance="检查版本号",
    )
    module_question = QuizQuestion(
        id=99,
        day_id=None,
        module_id=module.id,
        question_type="single",
        prompt="知识更新类问题通常优先选择哪种方案？",
        options_json=json.dumps(["Prompt", "RAG", "LoRA 微调", "只改 UI"], ensure_ascii=False),
        correct_answer_json=json.dumps(["RAG"], ensure_ascii=False),
        explanation="这是后面 RAG 的内容。",
    )

    questions = build_day_quiz(day, [module_question])

    assert all(question["id"] != 99 for question in questions)


def test_day_one_quiz_uses_professional_scenario_questions():
    module = Module(id=1, name="最小环境与学习仓库", sort_order=1, description="")
    day = LearningDay(
        id=1,
        day_number=1,
        module_id=module.id,
        module=module,
        stage="最小环境",
        topic="学习仓库与基础环境",
        environment="Python 3.11+、Git、VS Code、uv/pip",
        learning_goal="只搭最小开发环境，后续工具用到再搭",
        resources_text="",
        resource_hint="",
        practice_steps="创建仓库并提交第一次 commit",
        acceptance_criteria="能提交第一次 commit；README 写明目录用途",
        output_artifact="repo + README.md",
        status="未开始",
        guidance="版本号、路径、环境变量、网络代理、终端是否重启。",
    )

    questions = build_day_quiz(day, [])
    text = "\n".join(question["prompt"] + "\n" + question["explanation"] for question in questions)

    for keyword in ["场景", "排查", "验证", "交付", "风险"]:
        assert keyword in text
    assert all(len(question["explanation"]) >= 28 for question in questions)


def test_later_day_quiz_is_domain_specific_and_professional():
    module = Module(id=7, name="RAG / 知识库 Agent", sort_order=7, description="")
    day = LearningDay(
        id=29,
        day_number=29,
        module_id=module.id,
        module=module,
        stage="理论基础篇",
        topic="RAG 基础链路",
        environment="Python、embedding、向量检索、固定问题集",
        learning_goal="理解 chunk、embedding、retrieval、rerank、answer generation 的链路",
        resources_text="",
        resource_hint="",
        practice_steps="准备文档，切分，检索，再生成答案",
        acceptance_criteria="能解释 RAG 每一层如何影响答案质量",
        output_artifact="rag_pipeline_notes.md",
        status="未开始",
        guidance="检查 chunk 是否过大、召回是否为空、答案是否引用来源。",
    )

    questions = build_day_quiz(day, [])
    text = "\n".join(question["prompt"] + "\n" + question["explanation"] for question in questions)

    for keyword in ["场景", "检索", "评估", "排查", "交付", "风险"]:
        assert keyword in text
    assert "只收藏视频" not in text


def test_mcp_quiz_targets_protocol_architecture_and_product_judgment():
    module = Module(id=4, name="4. MCP", sort_order=4, description="")
    day = LearningDay(
        id=15,
        day_number=15,
        module_id=module.id,
        module=module,
        stage="理论基础篇",
        topic="MCP SDK 搭建",
        environment="MCP Python SDK；今天第一次搭",
        learning_goal="把本地工具标准化为 MCP server",
        resources_text="",
        resource_hint="",
        practice_steps="安装 MCP Python SDK，跑通 hello MCP server，记录客户端发现工具流程",
        acceptance_criteria="hello MCP server 能启动",
        output_artifact="demos/06_mcp_hello.py",
        status="未开始",
        guidance="SDK 版本、启动命令、客户端配置、工具名称是否暴露、日志。",
    )

    questions = build_day_quiz(day, [])
    text = "\n".join(
        question["prompt"] + "\n" + "\n".join(question["options"]) + "\n" + question["explanation"]
        for question in questions
    )

    assert len(questions) >= 8
    for keyword in [
        "MCP server",
        "tool schema",
        "工具发现",
        "client",
        "transport",
        "stdio",
        "安全边界",
        "allowlist",
        "架构",
        "产品",
        "验收",
    ]:
        assert keyword in text
    assert "最应该先确认什么" not in text


def test_mcp_file_quiz_targets_allowlist_and_error_handling():
    module = Module(id=4, name="4. MCP", sort_order=4, description="")
    day = LearningDay(
        id=16,
        day_number=16,
        module_id=module.id,
        module=module,
        stage="进阶篇",
        topic="文件 MCP 工具",
        environment="MCP SDK、data/",
        learning_goal="把 read_file 改成 MCP tool",
        resources_text="",
        resource_hint="",
        practice_steps="复用 read_file，改造成 MCP tool，补 schema 和错误处理",
        acceptance_criteria="MCP tool 能被发现和调用",
        output_artifact="demos/07_file_mcp_server.py",
        status="未开始",
        guidance="SDK 版本、启动命令、客户端配置、工具名称是否暴露。",
    )

    questions = build_day_quiz(day, [])
    text = "\n".join(question["prompt"] + "\n" + question["explanation"] for question in questions)

    for keyword in ["read_file", "allowlist", "resolve", "越权", "tool schema", "错误返回", "产品"]:
        assert keyword in text
    assert "hello server 原样复制" in "\n".join(option for q in questions for option in q["options"])


def test_mcp_orchestration_quiz_targets_traceability_and_tool_choice():
    module = Module(id=4, name="4. MCP", sort_order=4, description="")
    day = LearningDay(
        id=17,
        day_number=17,
        module_id=module.id,
        module=module,
        stage="实战篇",
        topic="多工具编排",
        environment="File/SQL/MCP；不需要 LangGraph",
        learning_goal="让 agent 在多个工具间选择",
        resources_text="",
        resource_hint="",
        practice_steps="准备 file、sql 两个工具，记录每次工具调用日志",
        acceptance_criteria="多工具任务可复现、可观察",
        output_artifact="demos/08_tool_orchestration.py",
        status="未开始",
        guidance="schema 是否太宽、工具是否有副作用、错误是否可见。",
    )

    questions = build_day_quiz(day, [])
    text = "\n".join(question["prompt"] + "\n" + question["explanation"] for question in questions)

    for keyword in ["多工具", "trace_id", "tool_name", "arguments", "失败", "产品", "架构", "可复现"]:
        assert keyword in text
    assert "最终答案看起来像真的即可" in "\n".join(option for q in questions for option in q["options"])
