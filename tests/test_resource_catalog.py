from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, LearningDay, Module, Resource
from app.services.resource_catalog import (
    dedupe_resources,
    ensure_resource_catalog,
    generate_day_resource_specs,
    sort_resources_for_learning_path,
)


def make_day(day_number: int, topic: str, module_name: str = "RAG / 知识库 Agent") -> LearningDay:
    module = Module(id=1, name=module_name, sort_order=1, description="")
    return LearningDay(
        id=day_number,
        day_number=day_number,
        module_id=module.id,
        module=module,
        stage="理论基础篇",
        topic=topic,
        environment="Python、embedding、向量检索",
        learning_goal="理解当天主题的工程边界和质量判断",
        resources_text="",
        resource_hint="",
        practice_steps="完成最小实验并记录验证结果",
        acceptance_criteria="能解释关键决策和失败模式",
        output_artifact="notes.md",
        status="未开始",
        guidance="检查输入、输出、版本和路径。",
    )


def test_generate_day_resource_specs_has_five_videos_and_five_deep_resources():
    day = make_day(29, "RAG 基础链路")

    specs = generate_day_resource_specs(day)

    assert len([item for item in specs if item["resource_type"] == "video"]) >= 5
    assert len([item for item in specs if item["resource_type"] in {"doc", "github", "tool"}]) >= 5
    assert len({item["url"] for item in specs}) == len(specs)


def test_dedupe_resources_removes_duplicate_urls():
    resources = [
        Resource(title="A", url="https://example.com/a", resource_type="doc"),
        Resource(title="A duplicate", url="https://example.com/a", resource_type="doc"),
        Resource(title="B", url="https://example.com/b", resource_type="video"),
    ]

    unique = dedupe_resources(resources)

    assert [item.url for item in unique] == ["https://example.com/a", "https://example.com/b"]


def test_ensure_resource_catalog_adds_dense_daily_resources():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        module = Module(name="RAG / 知识库 Agent", sort_order=1, description="")
        session.add(module)
        session.flush()
        day = make_day(29, "RAG 基础链路")
        day.module_id = module.id
        day.module = module
        session.add(day)
        session.commit()

        ensure_resource_catalog(session)

        resources = session.scalars(select(Resource).where(Resource.day_id == day.id)).all()

    assert len(resources) >= 10
    assert len([item for item in resources if item.resource_type == "video"]) >= 5


def test_sort_resources_follows_learning_day_before_type_and_title():
    module = Module(id=1, name="学习路线", sort_order=1, description="")
    day_1 = make_day(1, "学习仓库与基础环境")
    day_1.id = 101
    day_1.module = module
    day_1.module_id = module.id
    day_15 = make_day(15, "MCP SDK 搭建")
    day_15.id = 115
    day_15.module = module
    day_15.module_id = module.id
    day_29 = make_day(29, "RAG 向量库搭建")
    day_29.id = 129
    day_29.module = module
    day_29.module_id = module.id

    resources = [
        Resource(title="MCP 视频", url="https://example.com/mcp", resource_type="video", day_id=day_15.id, day=day_15),
        Resource(title="RAG 文档", url="https://example.com/rag", resource_type="doc", day_id=day_29.id, day=day_29),
        Resource(title="基础环境 工具", url="https://example.com/env", resource_type="tool", day_id=day_1.id, day=day_1),
        Resource(title="基础环境 视频", url="https://example.com/env-video", resource_type="video", day_id=day_1.id, day=day_1),
    ]

    sorted_resources = sort_resources_for_learning_path(resources)

    assert [resource.title for resource in sorted_resources] == [
        "基础环境 视频",
        "基础环境 工具",
        "MCP 视频",
        "RAG 文档",
    ]
