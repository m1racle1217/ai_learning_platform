from fastapi import APIRouter, Depends, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import UserEvent
from app.services.user_data import clear_learning_progress

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/settings")
def settings_page(request: Request, session: Session = Depends(get_session)):
    events = session.scalars(select(UserEvent).order_by(UserEvent.created_at.desc()).limit(30)).all()
    return templates.TemplateResponse("settings.html", {"request": request, "events": events})


@router.post("/settings/clear-progress")
def clear_progress(session: Session = Depends(get_session)):
    clear_learning_progress(session)
    return RedirectResponse("/settings", status_code=303)
