from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import LearningDay
from app.services.progress import dashboard_summary, module_progress

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/")
def dashboard(request: Request, session: Session = Depends(get_session)):
    next_day = session.scalar(
        select(LearningDay)
        .where(LearningDay.status != "已完成")
        .order_by(LearningDay.day_number)
        .limit(1)
    )
    review_days = session.scalars(
        select(LearningDay)
        .where(LearningDay.status == "需要复盘")
        .order_by(LearningDay.day_number)
        .limit(5)
    ).all()
    return templates.TemplateResponse(
        "dashboard.html",
        {
            "request": request,
            "summary": dashboard_summary(session),
            "module_progress": module_progress(session),
            "next_day": next_day,
            "review_days": review_days,
        },
    )
