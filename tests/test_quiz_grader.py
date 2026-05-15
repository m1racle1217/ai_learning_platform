from app.services.quiz_grader import grade_questions


def test_single_choice_correct():
    questions = [
        {
            "id": 1,
            "question_type": "single",
            "correct": ["RAG"],
            "explanation": "知识更新优先 RAG。",
        }
    ]
    answers = {"1": ["RAG"]}

    result = grade_questions(questions, answers)

    assert result.score == 1
    assert result.total == 1
    assert result.feedback[0]["correct"] is True


def test_multiple_choice_order_does_not_matter():
    questions = [
        {
            "id": 2,
            "question_type": "multiple",
            "correct": ["chunk", "rerank"],
            "explanation": "RAG 依赖检索链路。",
        }
    ]
    answers = {"2": ["rerank", "chunk"]}

    result = grade_questions(questions, answers)

    assert result.score == 1
    assert result.feedback[0]["correct"] is True
