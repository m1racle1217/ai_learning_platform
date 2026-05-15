from fastapi.testclient import TestClient

from app.main import app


def test_dashboard_loads():
    client = TestClient(app)
    response = client.get("/")

    assert response.status_code == 200
    assert "AI 学习平台" in response.text


def test_learning_plan_loads():
    client = TestClient(app)
    response = client.get("/plan")

    assert response.status_code == 200
    assert "70天路线" in response.text


def test_exercise_page_loads_for_day_one():
    client = TestClient(app)
    response = client.get("/days/1/exercise")

    assert response.status_code == 200
    assert "提交练习" in response.text


def test_quiz_page_loads_for_day_one():
    client = TestClient(app)
    response = client.get("/days/1/quiz")

    assert response.status_code == 200
    assert "随堂小测" in response.text


def test_runtime_heartbeat_endpoint_updates_lifecycle():
    from app.services.runtime_lifecycle import configure_auto_shutdown

    lifecycle = configure_auto_shutdown(idle_seconds=30)
    client = TestClient(app)

    response = client.post("/runtime/heartbeat")

    assert response.status_code == 200
    assert response.json() == {"ok": True}
    assert lifecycle.last_heartbeat_at is not None
