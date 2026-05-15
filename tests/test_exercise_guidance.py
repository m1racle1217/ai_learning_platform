from app.models import LearningDay, Module
from app.services.exercise_guidance import build_exercise_guidance


def guidance_text(sections: list[dict]) -> str:
    return "\n".join(
        [
            section["title"]
            + "\n"
            + section["intro"]
            + "\n"
            + "\n".join(
                step["title"]
                + "\n"
                + step["body"]
                + "\n"
                + "\n".join(step["commands"])
                + "\n"
                + str(step["verify"])
                for step in section["steps"]
            )
            for section in sections
        ]
    )


def make_day(day_number: int, topic: str, environment: str, practice_steps: str) -> LearningDay:
    module = Module(id=1, name="最小环境与学习仓库", sort_order=1, description="")
    return LearningDay(
        id=day_number,
        day_number=day_number,
        module_id=module.id,
        module=module,
        stage="最小环境",
        topic=topic,
        environment=environment,
        learning_goal="只搭最小开发环境，后续工具用到再搭",
        resources_text="",
        resource_hint="",
        practice_steps=practice_steps,
        acceptance_criteria="能提交第一次 commit；README 写明目录用途",
        output_artifact="repo + README.md",
        status="未开始",
        guidance="版本号、路径、环境变量、网络代理、终端是否重启。",
    )


def test_day_one_guidance_is_beginner_friendly():
    day = make_day(
        1,
        "学习仓库与基础环境",
        "Python 3.11+、Git、VS Code、uv/pip；不用 Docker/Dify/RAG",
        "创建 ai-agent-learning 仓库并提交第一次 commit",
    )

    sections = build_exercise_guidance(day)
    text = "\n".join(
        [
            section["title"]
            + "\n"
            + "\n".join(
                step["body"] + "\n" + "\n".join(step["commands"]) + "\n" + str(step["verify"])
                for step in section["steps"]
            )
            for section in sections
        ]
    )

    for keyword in ["Python 3.11", "Git", "VS Code", "uv", "pip", "git init", "git commit"]:
        assert keyword in text
    assert len(sections) >= 6
    assert all(section["steps"] for section in sections)


def test_day_one_guidance_is_executable_professional_runbook():
    day = make_day(
        1,
        "学习仓库与基础环境",
        "Python 3.11+、Git、VS Code、uv/pip；不用 Docker/Dify/RAG",
        "创建 ai-agent-learning 仓库并提交第一次 commit",
    )

    sections = build_exercise_guidance(day)
    text = "\n".join(
        [
            section["title"]
            + "\n"
            + section["intro"]
            + "\n"
            + "\n".join(
                step["title"]
                + "\n"
                + step["body"]
                + "\n"
                + "\n".join(step["commands"])
                + "\n"
                + str(step["verify"])
                for step in section["steps"]
            )
            for section in sections
        ]
    )

    for keyword in ["PowerShell", "py -3.11 -m venv .venv", "git status --short", "失败处理", "验证命令"]:
        assert keyword in text


def test_later_day_guidance_has_professional_runbook_structure():
    day = make_day(
        29,
        "RAG 基础链路",
        "Python、embedding、向量检索、固定问题集",
        "准备文档，切分，检索，再生成答案",
    )
    day.learning_goal = "理解 chunk、embedding、retrieval、rerank、answer generation 的链路"
    day.acceptance_criteria = "能解释 RAG 每一层如何影响答案质量"
    day.output_artifact = "rag_pipeline_notes.md"
    day.guidance = "检查 chunk 是否过大、召回是否为空、答案是否引用来源。"

    sections = build_exercise_guidance(day)
    text = "\n".join(
        [
            section["title"]
            + "\n"
            + section["intro"]
            + "\n"
            + "\n".join(
                step["title"]
                + "\n"
                + step["body"]
                + "\n"
                + "\n".join(step["commands"])
                + "\n"
                + str(step["verify"])
                for step in section["steps"]
            )
            for section in sections
        ]
    )

    for keyword in ["目标拆解", "执行步骤", "质量验证", "失败处理", "提交证据", "git status --short"]:
        assert keyword in text


def test_mcp_guidance_is_executable_professional_runbook():
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

    text = guidance_text(build_exercise_guidance(day))

    for keyword in [
        "mcp[cli]",
        "FastMCP",
        "demos/06_mcp_hello.py",
        "@mcp.tool",
        "mcp dev demos/06_mcp_hello.py",
        "Inspector",
        "工具发现",
        "list_tools",
        "stdio",
        "transport",
        "客户端配置",
        "安全边界",
        "失败处理",
        "验收",
    ]:
        assert keyword in text


def test_mcp_file_guidance_focuses_on_allowlisted_file_tool():
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

    text = guidance_text(build_exercise_guidance(day))

    for keyword in [
        "demos/07_file_mcp_server.py",
        "read_file",
        "allowlist",
        "resolve",
        "越权",
        "mcp dev demos/07_file_mcp_server.py",
        "list_tools",
        "正常",
        "异常",
    ]:
        assert keyword in text
    assert "demos/06_mcp_hello.py" not in text


def test_mcp_orchestration_guidance_focuses_on_traceable_multi_tool_flow():
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

    text = guidance_text(build_exercise_guidance(day))

    for keyword in [
        "demos/08_tool_orchestration.py",
        "trace_id",
        "tool_name",
        "arguments",
        "result_summary",
        "error",
        "duration_ms",
        "file.read",
        "sql.query",
        "可回放",
    ]:
        assert keyword in text
    assert "mcp dev demos/06_mcp_hello.py" not in text
