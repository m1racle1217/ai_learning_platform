from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, LearningDay, Module, Resource
from app.services.resource_catalog import (
    dedupe_resources,
    ensure_resource_catalog,
    generate_day_resource_specs,
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
