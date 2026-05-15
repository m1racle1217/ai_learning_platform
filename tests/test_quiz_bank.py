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
