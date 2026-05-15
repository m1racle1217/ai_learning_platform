from app.models import LearningDay, Module
from app.services.exercise_guidance import build_exercise_guidance


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
