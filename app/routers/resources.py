from fastapi import APIRouter, Depends, Request
from fastapi.templating import Jinja2Templates
from sqlalchemy import select
from sqlalchemy.orm import joinedload
from sqlalchemy.orm import Session

from app.database import get_session
from app.models import Resource
from app.services.resource_catalog import dedupe_resources, sort_resources_for_learning_path

router = APIRouter()
templates = Jinja2Templates(directory="app/templates")


@router.get("/resources")
def resources_page(request: Request, session: Session = Depends(get_session)):
    resources = session.scalars(select(Resource).options(joinedload(Resource.day))).all()
    resources = sort_resources_for_learning_path(dedupe_resources(resources))
    return templates.TemplateResponse(
        "resources.html",
        {"request": request, "resources": resources},
    )
