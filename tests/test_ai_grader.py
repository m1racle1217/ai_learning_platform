from app.services.ai_grader import grade_open_answer


def test_grade_open_answer_without_api_key_returns_manual_review():
    result = grade_open_answer(
        prompt="解释 RAG 和微调的区别",
        answer="RAG 用检索，微调用训练。",
        api_key="",
    )

    assert result["status"] == "待人工复核"
    assert "未配置" in result["feedback"]
