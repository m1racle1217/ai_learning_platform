from dataclasses import dataclass
from pathlib import Path


@dataclass(frozen=True)
class ExerciseCheckResult:
    status: str
    feedback: str


def check_exercise_submission(
    answer_text: str,
    output_path: str | None,
    expected_output: str,
) -> ExerciseCheckResult:
    answer = answer_text.strip()
    if len(answer) < 15:
        return ExerciseCheckResult("需要补充", "至少写 15 个字，说明你完成了什么、卡在哪里、如何验证。")

    if expected_output and not output_path:
        return ExerciseCheckResult("需要补充", f"今天预期输出物是：{expected_output}。请填写输出物路径或说明。")

    path_feedback = ""
    if output_path:
        output = Path(output_path).expanduser()
        if not output.is_absolute():
            output = Path.cwd() / output
        if not output.exists():
            return ExerciseCheckResult(
                "需要补全",
                f"没有找到输出物路径：`{output_path}`。请确认路径是否写对，或先创建对应文件/目录后再提交。",
            )

        checks = [f"已找到输出物：`{output_path}`"]
        expected_lower = expected_output.lower()
        if "readme" in expected_lower:
            readme = output / "README.md" if output.is_dir() else output
            if readme.name.lower() != "readme.md" or not readme.exists():
                return ExerciseCheckResult("需要补全", "预期输出物包含 README.md，但当前路径下没有找到 README.md。")
            checks.append("README.md 已存在")
        if "repo" in expected_lower and output.is_dir():
            checks.append("目录产物已存在")
            if (output / ".git").exists():
                checks.append("检测到 Git 仓库")
        path_feedback = "；".join(checks) + "。"

    if output_path and expected_output:
        expected_hint = expected_output.split()[0].strip()
        if expected_hint and "/" in expected_hint and expected_hint not in output_path:
            return ExerciseCheckResult(
                "待人工复核",
                f"已提交，但输出路径 `{output_path}` 和预期 `{expected_output}` 不完全匹配，请人工确认。",
            )

    return ExerciseCheckResult("已完成", f"{path_feedback}满足最小完成要求。建议继续对照验收标准检查质量。")
