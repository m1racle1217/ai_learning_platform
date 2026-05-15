from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True)
class QuizGradeResult:
    score: int
    total: int
    feedback: list[dict[str, Any]]


def normalize_answer(values: list[str] | str | None) -> list[str]:
    if values is None:
        return []
    if isinstance(values, str):
        values = [values]
    return sorted(str(value).strip() for value in values if str(value).strip())


def grade_questions(
    questions: list[dict[str, Any]], answers: dict[str, list[str] | str]
) -> QuizGradeResult:
    score = 0
    feedback = []
    for question in questions:
        question_id = str(question["id"])
        expected = normalize_answer(question["correct"])
        actual = normalize_answer(answers.get(question_id))
        correct = expected == actual
        if correct:
            score += 1
        feedback.append(
            {
                "question_id": question["id"],
                "correct": correct,
                "expected": expected,
                "actual": actual,
                "explanation": question["explanation"],
            }
        )
    return QuizGradeResult(score=score, total=len(questions), feedback=feedback)
