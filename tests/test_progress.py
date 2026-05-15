from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session

from app.models import Base, ExerciseSubmission, LearningDay, Module, QuizAttempt, ResourceProgress, UserEvent
from app.services.progress import dashboard_summary, percentage
from app.services.user_data import clear_learning_progress, log_user_event


def test_database_can_create_module():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        session.add(Module(name="Prompt", sort_order=1, description="Prompt basics"))
        session.commit()

        module = session.scalar(select(Module).where(Module.name == "Prompt"))

    assert module is not None
    assert module.sort_order == 1


def test_percentage_handles_zero_total():
    assert percentage(0, 0) == 0.0


def test_percentage_rounds_to_one_decimal():
    assert percentage(1, 3) == 33.3


def test_dashboard_quiz_average_uses_percent_score():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        module = Module(name="Prompt", sort_order=1, description="Prompt basics")
        session.add(module)
        session.flush()
        day = LearningDay(
            day_number=1,
            module_id=module.id,
            stage="理论基础篇",
            topic="Prompt 测试",
            environment="Python",
            learning_goal="会评估提示词质量",
            resources_text="",
            resource_hint="",
            practice_steps="",
            acceptance_criteria="",
            output_artifact="",
            status="未开始",
            guidance="",
        )
        session.add(day)
        session.flush()
        session.add_all(
            [
                QuizAttempt(day_id=day.id, module_id=module.id, score=1, total=2, feedback_json="[]"),
                QuizAttempt(day_id=day.id, module_id=module.id, score=3, total=4, feedback_json="[]"),
            ]
        )
        session.commit()

        summary = dashboard_summary(session)

    assert summary["average_quiz_score"] == 62.5


def test_clear_learning_progress_resets_user_data():
    engine = create_engine("sqlite:///:memory:")
    Base.metadata.create_all(engine)

    with Session(engine) as session:
        module = Module(name="Prompt", sort_order=1, description="Prompt basics")
        session.add(module)
        session.flush()
        day = LearningDay(
            day_number=1,
            module_id=module.id,
            stage="理论基础篇",
            topic="Prompt 测试",
            environment="Python",
            learning_goal="会评估提示词质量",
            resources_text="",
            resource_hint="",
            practice_steps="",
            acceptance_criteria="",
            output_artifact="",
            status="已完成",
            guidance="",
        )
        session.add(day)
        session.flush()
        session.add_all(
            [
                QuizAttempt(day_id=day.id, module_id=module.id, score=1, total=1, feedback_json="[]"),
                ExerciseSubmission(
                    day_id=day.id,
                    answer_text="done",
                    checklist_json="{}",
                    auto_status="已完成",
                    auto_feedback="ok",
                ),
                ResourceProgress(resource_id=1, completed=1),
            ]
        )
        log_user_event(session, "test_event", "day", day.id, {"day_number": 1})
        session.commit()

        clear_learning_progress(session)

        assert session.get(LearningDay, day.id).status == "未开始"
        assert session.query(QuizAttempt).count() == 0
        assert session.query(ExerciseSubmission).count() == 0
        assert session.query(ResourceProgress).count() == 0
        assert session.query(UserEvent).count() == 2
