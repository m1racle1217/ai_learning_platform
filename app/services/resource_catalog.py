from urllib.parse import quote_plus

from sqlalchemy import select
from sqlalchemy.orm import Session

from app.models import LearningDay, Resource


def dedupe_resources(resources: list[Resource]) -> list[Resource]:
    seen: set[str] = set()
    unique: list[Resource] = []
    for resource in resources:
        key = resource.url.strip().lower()
        if key in seen:
            continue
        seen.add(key)
        unique.append(resource)
    return unique


def generate_day_resource_specs(day: LearningDay) -> list[dict[str, str]]:
    topic = day.topic.strip()
    module_name = day.module.name if day.module else ""
    query = quote_plus(f"{topic} {module_name} tutorial")
    zh_query = quote_plus(f"{topic} {module_name} 教程")
    github_query = quote_plus(f"{topic} {module_name}")
    doc_query = quote_plus(f"{topic} {module_name} docs")

    specs = [
        {
            "title": f"YouTube 深度教程搜索：{topic}",
            "url": f"https://www.youtube.com/results?search_query={query}",
            "resource_type": "video",
        },
        {
            "title": f"Bilibili 高质量教程搜索：{topic}",
            "url": f"https://search.bilibili.com/all?keyword={zh_query}",
            "resource_type": "video",
        },
        {
            "title": f"YouTube 工程实战搜索：{topic}",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(topic + ' hands on project')}",
            "resource_type": "video",
        },
        {
            "title": f"Bilibili 实战项目搜索：{topic}",
            "url": f"https://search.bilibili.com/all?keyword={quote_plus(topic + ' 实战 项目')}",
            "resource_type": "video",
        },
        {
            "title": f"YouTube 排错 / Best Practices：{topic}",
            "url": f"https://www.youtube.com/results?search_query={quote_plus(topic + ' best practices debugging')}",
            "resource_type": "video",
        },
        {
            "title": f"Google / 官方文档搜索：{topic}",
            "url": f"https://www.google.com/search?q={doc_query}",
            "resource_type": "doc",
        },
        {
            "title": f"GitHub 高星项目搜索：{topic}",
            "url": f"https://github.com/search?q={github_query}&type=repositories&s=stars&o=desc",
            "resource_type": "github",
        },
        {
            "title": f"GitHub 代码示例搜索：{topic}",
            "url": f"https://github.com/search?q={quote_plus(topic + ' example')}&type=code",
            "resource_type": "github",
        },
        {
            "title": f"Stack Overflow 排错搜索：{topic}",
            "url": f"https://stackoverflow.com/search?q={quote_plus(topic)}",
            "resource_type": "tool",
        },
        {
            "title": f"Perplexity / 多源资料搜索：{topic}",
            "url": f"https://www.perplexity.ai/search?q={quote_plus(topic + ' learning resources')}",
            "resource_type": "tool",
        },
    ]
    return _module_specific_specs(day) + specs


def _module_specific_specs(day: LearningDay) -> list[dict[str, str]]:
    name = (day.module.name if day.module else "").lower()
    topic = day.topic
    specs: list[dict[str, str]] = []
    if "prompt" in name:
        specs.extend(
            [
                {"title": "OpenAI Prompt Engineering Guide", "url": "https://platform.openai.com/docs/guides/prompt-engineering", "resource_type": "doc"},
                {"title": "Anthropic Prompt Engineering", "url": "https://docs.anthropic.com/en/docs/build-with-claude/prompt-engineering/overview", "resource_type": "doc"},
            ]
        )
    if "rag" in name or "知识库" in name:
        specs.extend(
            [
                {"title": "LangChain RAG Tutorial", "url": "https://python.langchain.com/docs/tutorials/rag/", "resource_type": "doc"},
                {"title": "LlamaIndex RAG Docs", "url": "https://docs.llamaindex.ai/en/stable/understanding/rag/", "resource_type": "doc"},
                {"title": "RAGAS Evaluation", "url": "https://docs.ragas.io/", "resource_type": "tool"},
            ]
        )
    if "mcp" in name:
        specs.extend(
            [
                {"title": "Model Context Protocol Docs", "url": "https://modelcontextprotocol.io/docs", "resource_type": "doc"},
                {"title": "MCP Python SDK", "url": "https://github.com/modelcontextprotocol/python-sdk", "resource_type": "github"},
            ]
        )
    if "langgraph" in name or "agent" in name:
        specs.extend(
            [
                {"title": "LangGraph Docs", "url": "https://langchain-ai.github.io/langgraph/", "resource_type": "doc"},
                {"title": "OpenAI Agents SDK", "url": "https://openai.github.io/openai-agents-python/", "resource_type": "doc"},
            ]
        )
    if "微调" in name or "lora" in topic.lower():
        specs.extend(
            [
                {"title": "Hugging Face PEFT", "url": "https://huggingface.co/docs/peft/index", "resource_type": "doc"},
                {"title": "Unsloth Docs", "url": "https://docs.unsloth.ai/", "resource_type": "doc"},
                {"title": "Axolotl", "url": "https://github.com/axolotl-ai-cloud/axolotl", "resource_type": "github"},
            ]
        )
    return specs


def ensure_resource_catalog(session: Session) -> None:
    existing = {
        (resource.day_id, resource.url.strip().lower())
        for resource in session.scalars(select(Resource)).all()
    }
    days = session.scalars(select(LearningDay).order_by(LearningDay.day_number)).all()
    for day in days:
        for spec in generate_day_resource_specs(day):
            key = (day.id, spec["url"].strip().lower())
            if key in existing:
                continue
            session.add(
                Resource(
                    day_id=day.id,
                    module_id=day.module_id,
                    title=spec["title"],
                    url=spec["url"],
                    resource_type=spec["resource_type"],
                    notes="自动补充的高质量资源入口",
                )
            )
            existing.add(key)
    session.commit()
