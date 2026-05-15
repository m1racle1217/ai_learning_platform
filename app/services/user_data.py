import json
from typing import Any

from sqlalchemy.orm import Session

from app.models import ExerciseSubmission, LearningDay, QuizAttempt, ResourceProgress, UserEvent


def log_user_event(
    session: Session,
    event_type: str,
    target_type: str | None = None,
    target_id: int | None = None,
    payload: dict[str, Any] | None = None,
) -> UserEvent:
    event = UserEvent(
        event_type=event_type,
        target_type=target_type,
        target_id=target_id,
        payload_json=json.dumps(payload or {}, ensure_ascii=False),
    )
    session.add(event)
    return event


def clear_learning_progress(session: Session) -> None:
    session.query(ResourceProgress).delete()
    session.query(ExerciseSubmission).delete()
    session.query(QuizAttempt).delete()
    session.query(LearningDay).update({LearningDay.status: "未开始"})
    log_user_event(session, "clear_progress", "system", None, {})
    session.commit()
