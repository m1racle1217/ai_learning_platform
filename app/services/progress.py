from sqlalchemy import func, select
from sqlalchemy.orm import Session

from app.models import Chapter, LearningDay, Module, QuizAttempt


def percentage(done: int, total: int) -> float:
    if total <= 0:
        return 0.0
    return round(done / total * 100, 1)


def dashboard_summary(session: Session) -> dict:
    total_days = session.scalar(select(func.count()).select_from(LearningDay)) or 0
    completed_days = (
        session.scalar(
            select(func.count()).select_from(LearningDay).where(LearningDay.status == "已完成")
        )
        or 0
    )
    learning_days = (
        session.scalar(
            select(func.count()).select_from(LearningDay).where(LearningDay.status == "学习中")
        )
        or 0
    )
    review_days = (
        session.scalar(
            select(func.count()).select_from(LearningDay).where(LearningDay.status == "需要复盘")
        )
        or 0
    )
    quiz_count = session.scalar(select(func.count()).select_from(QuizAttempt)) or 0
    attempts = session.scalars(select(QuizAttempt)).all() if quiz_count else []
    avg_score = (
        sum((attempt.score / attempt.total) * 100 for attempt in attempts if attempt.total)
        / len([attempt for attempt in attempts if attempt.total])
        if attempts
        else None
    )

    return {
        "total_days": total_days,
        "completed_days": completed_days,
        "learning_days": learning_days,
        "review_days": review_days,
        "progress_percent": percentage(completed_days, total_days),
        "quiz_count": quiz_count,
        "average_quiz_score": round(float(avg_score), 1) if avg_score is not None else None,
    }


def module_progress(session: Session) -> list[dict]:
    modules = session.scalars(select(Module).order_by(Module.sort_order)).all()
    rows = []
    for module in modules:
        total = len(module.days)
        done = sum(1 for day in module.days if day.status == "已完成")
        rows.append({"module": module, "total": total, "done": done, "percent": percentage(done, total)})
    return rows


def chapter_progress(session: Session) -> list[dict]:
    chapters = session.scalars(select(Chapter).order_by(Chapter.start_day)).all()
    rows = []
    for chapter in chapters:
        total = len(chapter.days)
        done = sum(1 for day in chapter.days if day.status == "已完成")
        rows.append(
            {"chapter": chapter, "total": total, "done": done, "percent": percentage(done, total)}
        )
    return rows
