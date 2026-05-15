from fastapi import APIRouter, Depends, HTTPException, Request
from fastapi.templating import Jinja2Templates
import json
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import LearningDay, QuizAttempt, QuizQuestion
from app.services.quiz_bank import build_day_quiz
from app.services.quiz_grader import grade_questions
from app.services.user_data import log_user_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/days/{day_number}/quiz")
def quiz_page(day_number: int, request: Request, session: Session = Depends(get_session)):
    day = session.scalar(select(LearningDay).where(LearningDay.day_number == day_number))
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    questions = session.scalars(select(QuizQuestion).where(QuizQuestion.day_id == day.id)).all()
    return templates.TemplateResponse("quiz.html", {"request": request, "day": day, "questions": build_day_quiz(day, questions)})


@router.post("/days/{day_number}/quiz")
async def submit_quiz(day_number: int, request: Request, session: Session = Depends(get_session)):
    day = session.scalar(select(LearningDay).where(LearningDay.day_number == day_number))
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    form = await request.form()
    questions = session.scalars(select(QuizQuestion).where(QuizQuestion.day_id == day.id)).all()
    question_dicts = build_day_quiz(day, questions)
    answers = {str(question["id"]): form.getlist(str(question["id"])) for question in question_dicts}
    result = grade_questions(question_dicts, answers)
    session.add(
        QuizAttempt(
            day_id=day.id,
            module_id=day.module_id,
            score=result.score,
            total=result.total,
            feedback_json=json.dumps(result.feedback, ensure_ascii=False),
        )
    )
    log_user_event(
        session,
        "quiz_submit",
        "day",
        day.id,
        {"day_number": day.day_number, "score": result.score, "total": result.total},
    )
    session.commit()
    return templates.TemplateResponse(
        "quiz_result.html",
        {"request": request, "day": day, "result": result, "feedback": result.feedback},
    )
