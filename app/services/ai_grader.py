import httpx

from app.config import DEEPSEEK_BASE_URL, DEEPSEEK_MODEL


def grade_open_answer(prompt: str, answer: str, api_key: str) -> dict:
    if not api_key:
        return {
            "status": "待人工复核",
            "score": None,
            "feedback": "未配置模型 API Key，开放题保留为人工复核。",
        }

    payload = {
        "model": DEEPSEEK_MODEL,
        "messages": [
            {
                "role": "system",
                "content": "你是严格但友好的 AI 学习助教。请按 0-100 分评分，并给出简短改进建议。",
            },
            {
                "role": "user",
                "content": f"题目：{prompt}\n\n学生答案：{answer}\n\n请输出 JSON：score, feedback。",
            },
        ],
        "temperature": 0,
    }
    response = httpx.post(
        f"{DEEPSEEK_BASE_URL}/chat/completions",
        headers={"Authorization": f"Bearer {api_key}"},
        json=payload,
        timeout=30,
    )
    response.raise_for_status()
    content = response.json()["choices"][0]["message"]["content"]
    return {"status": "已评分", "score": None, "feedback": content}
