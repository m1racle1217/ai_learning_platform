import json

from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import ExerciseSubmission, LearningDay
from app.services.exercise_checker import check_exercise_submission
from app.services.exercise_guidance import build_exercise_guidance
from app.services.user_data import log_user_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/days/{day_number}/exercise")
def exercise_page(day_number: int, request: Request, session: Session = Depends(get_session)):
    day = session.scalar(select(LearningDay).where(LearningDay.day_number == day_number))
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    submissions = session.scalars(
        select(ExerciseSubmission)
        .where(ExerciseSubmission.day_id == day.id)
        .order_by(ExerciseSubmission.created_at.desc())
    ).all()
    return templates.TemplateResponse(
        "exercise.html",
        {
            "request": request,
            "day": day,
            "submissions": submissions,
            "guidance_sections": build_exercise_guidance(day),
        },
    )


@router.post("/days/{day_number}/exercise")
def submit_exercise(
    day_number: int,
    answer_text: str = Form(...),
    output_path: str = Form(""),
    session: Session = Depends(get_session),
):
    day = session.scalar(select(LearningDay).where(LearningDay.day_number == day_number))
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    result = check_exercise_submission(answer_text, output_path or None, day.output_artifact)
    submission = ExerciseSubmission(
        day_id=day.id,
        answer_text=answer_text,
        output_path=output_path or None,
        checklist_json=json.dumps({"expected_output": day.output_artifact}, ensure_ascii=False),
        auto_status=result.status,
        auto_feedback=result.feedback,
    )
    session.add(submission)
    if result.status == "已完成":
        day.status = "已完成"
    elif day.status == "未开始":
        day.status = "学习中"
    log_user_event(
        session,
        "exercise_submit",
        "day",
        day.id,
        {"day_number": day.day_number, "status": result.status, "output_path": output_path or None},
    )
    session.commit()
    return RedirectResponse(f"/days/{day_number}/exercise", status_code=303)
