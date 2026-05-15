from app.seed_from_excel import parse_day_number, parse_resources_from_text


def test_parse_day_number():
    assert parse_day_number("第51天") == 51


def test_parse_resources_from_text_extracts_urls():
    text = (
        "视频资源：\n"
        "1、课程：https://example.com/video\n\n"
        "文档 / GitHub / 工具资源：\n"
        "1、文档：https://example.com/docs"
    )
    resources = parse_resources_from_text(text)

    assert resources == [
        {"title": "课程", "url": "https://example.com/video", "resource_type": "video"},
        {"title": "文档", "url": "https://example.com/docs", "resource_type": "doc"},
    ]
