from app.services.exercise_checker import check_exercise_submission


def test_empty_submission_needs_more_detail():
    result = check_exercise_submission("", None, "notes/example.md")

    assert result.status == "需要补充"
    assert "至少写" in result.feedback


def test_submission_with_output_path_is_complete(tmp_path):
    output = tmp_path / "example.md"
    output.write_text("done", encoding="utf-8")

    result = check_exercise_submission(
        "我完成了今天的练习，记录了问题和复盘。",
        str(output),
        "example.md",
    )

    assert result.status == "已完成"
    assert "满足最小完成" in result.feedback


def test_submission_checks_real_output_file(tmp_path):
    output = tmp_path / "README.md"
    output.write_text("# 学习仓库\n", encoding="utf-8")

    result = check_exercise_submission(
        "我完成了当天练习，创建了 README，并验证文件可以打开。",
        str(output),
        "repo + README.md",
    )

    assert result.status == "已完成"
    assert "已找到输出物" in result.feedback


def test_submission_reports_missing_output_file(tmp_path):
    result = check_exercise_submission(
        "我完成了当天练习，但路径可能还没有创建，需要自动检查。",
        str(tmp_path / "missing.md"),
        "repo + README.md",
    )

    assert result.status == "需要补全"
    assert "没有找到输出物路径" in result.feedback
