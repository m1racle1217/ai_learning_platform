from fastapi import APIRouter, Depends, Form, HTTPException, Request
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import LearningDay, Module, Resource, ResourceProgress
from app.services.resource_catalog import dedupe_resources
from app.services.user_data import log_user_event

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")

VALID_STATUSES = {"未开始", "学习中", "已完成", "需要复盘"}


@router.get("/plan")
def plan(request: Request, session: Session = Depends(get_session)):
    days = session.scalars(select(LearningDay).order_by(LearningDay.day_number)).all()
    return templates.TemplateResponse("learning_plan.html", {"request": request, "days": days})


@router.get("/days/{day_number}")
def day_detail(day_number: int, request: Request, session: Session = Depends(get_session)):
    day = session.scalar(select(LearningDay).where(LearningDay.day_number == day_number))
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    resources = dedupe_resources(session.scalars(select(Resource).where(Resource.day_id == day.id)).all())
    progress_rows = session.scalars(
        select(ResourceProgress).where(ResourceProgress.resource_id.in_([resource.id for resource in resources]))
    ).all() if resources else []
    completed_resource_ids = {row.resource_id for row in progress_rows if row.completed}
    resource_total = len(resources)
    resource_done = len(completed_resource_ids)
    resource_percent = round(resource_done / resource_total * 100) if resource_total else 0
    return templates.TemplateResponse(
        "day_detail.html",
        {
            "request": request,
            "day": day,
            "resources": resources,
            "completed_resource_ids": completed_resource_ids,
            "resource_total": resource_total,
            "resource_done": resource_done,
            "resource_percent": resource_percent,
        },
    )


@router.post("/resources/{resource_id}/progress")
def update_resource_progress(
    resource_id: int,
    completed: int = Form(...),
    session: Session = Depends(get_session),
):
    resource = session.get(Resource, resource_id)
    if not resource:
        raise HTTPException(status_code=404, detail="Resource not found")
    row = session.scalar(select(ResourceProgress).where(ResourceProgress.resource_id == resource_id))
    if not row:
        row = ResourceProgress(resource_id=resource_id, completed=1 if completed else 0)
        session.add(row)
    else:
        row.completed = 1 if completed else 0
    log_user_event(
        session,
        "resource_progress",
        "resource",
        resource_id,
        {"completed": bool(row.completed), "day_id": resource.day_id, "module_id": resource.module_id},
    )
    session.commit()
    return {"ok": True, "completed": bool(row.completed)}


@router.post("/days/{day_number}/status")
def update_status(day_number: int, status: str = Form(...), session: Session = Depends(get_session)):
    if status not in VALID_STATUSES:
        raise HTTPException(status_code=400, detail="Invalid status")
    day = session.scalar(select(LearningDay).where(LearningDay.day_number == day_number))
    if not day:
        raise HTTPException(status_code=404, detail="Day not found")
    day.status = status
    log_user_event(session, "status_update", "day", day.id, {"day_number": day.day_number, "status": status})
    session.commit()
    return RedirectResponse(f"/days/{day_number}", status_code=303)


@router.get("/modules/{module_id}")
def module_detail(module_id: int, request: Request, session: Session = Depends(get_session)):
    module = session.get(Module, module_id)
    if not module:
        raise HTTPException(status_code=404, detail="Module not found")
    days = session.scalars(
        select(LearningDay).where(LearningDay.module_id == module_id).order_by(LearningDay.day_number)
    ).all()
    return templates.TemplateResponse(
        "module_detail.html",
        {"request": request, "module": module, "days": days},
    )
