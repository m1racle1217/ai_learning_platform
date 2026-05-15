from fastapi import APIRouter

from app.services.runtime_lifecycle import get_lifecycle

router = APIRouter()


@router.post("/runtime/heartbeat")
def runtime_heartbeat():
    get_lifecycle().heartbeat()
    return {"ok": True}
