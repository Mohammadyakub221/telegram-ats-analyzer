_ESCAPE_CHARS = str.maketrans({
    "_": "\\_", "*": "\\*", "[": "\\[", "]": "\\]", "(": "\\(",
    ")": "\\)", "~": "\\~", "`": "\\`", ">": "\\>", "#": "\\#",
    "+": "\\+", "-": "\\-", "=": "\\=", "|": "\\|", "{": "\\{",
    "}": "\\}", ".": "\\.", "!": "\\!",
})


def escape(text: str) -> str:
    return text.translate(_ESCAPE_CHARS)


def _score_emoji(score: int) -> str:
    if score >= 90:
        return "🟢"
    if score >= 70:
        return "🟡"
    if score >= 50:
        return "🟠"
    return "🔴"


def _bullet(items: list[str]) -> str:
    return "\n".join(f"• {escape(item)}" for item in items)


def _section(title: str, body: str) -> str:
    return f"*{escape(title)}*\n{body}"


def build_messages(data: dict) -> list[str]:
    messages = []
    msgs = [_msg1(data), _msg2(data), _msg3(data), _msg4(data)]
    for msg in msgs:
        parts = _split_long_message(msg)
        messages.extend(parts)
    return messages


def _split_long_message(text: str, limit: int = 3950) -> list[str]:
    if len(text) <= limit:
        return [text]
    parts = []
    while len(text) > limit:
        split_at = text.rfind("\n", 0, limit)
        if split_at == -1:
            split_at = limit
        parts.append(text[:split_at])
        text = text[split_at:].lstrip()
    if text:
        parts.append(text)
    return parts


def _msg1(data: dict) -> str:
    score = data.get("ats_score", 0)
    emoji = _score_emoji(score)
    verdict = data.get("final_verdict", "N/A")
    verdict_reason = data.get("verdict_reason", "")
    sb = data.get("score_breakdown", {})
    lines = [
        f"{emoji} *ATS Score: {score}/100*",
        "",
        f"*Verdict:* {escape(verdict)}",
        "",
        escape(verdict_reason),
        "",
        "── *Breakdown* ──",
        f"• Skills: {sb.get('skills', 0)}/100",
        f"• Experience: {sb.get('experience', 0)}/100",
        f"• Projects: {sb.get('projects', 0)}/100",
        f"• Education: {sb.get('education', 0)}/100",
        f"• Keywords: {sb.get('keywords', 0)}/100",
        f"• Formatting: {sb.get('formatting', 0)}/100",
        f"• Certifications: {sb.get('certifications', 0)}/100",
    ]
    return "\n".join(lines)


def _msg2(data: dict) -> str:
    sections = []
    matching = data.get("matching_skills", [])
    if matching:
        sections.append(_section("✅ Matching Skills", _bullet(matching)))

    missing_critical = data.get("missing_skills_critical", [])
    if missing_critical:
        sections.append(_section("❌ Missing Skills \\(Critical\\)", _bullet(missing_critical)))

    missing_nice = data.get("missing_skills_nice_to_have", [])
    if missing_nice:
        sections.append(_section("⚠️ Missing Skills \\(Nice‑to‑Have\\)", _bullet(missing_nice)))

    return "\n\n".join(sections) if sections else "No skill data available."


def _msg3(data: dict) -> str:
    sections = []
    strengths = data.get("strengths", [])
    if strengths:
        sections.append(_section("💪 Strengths", _bullet(strengths)))

    weaknesses = data.get("weaknesses", [])
    if weaknesses:
        sections.append(_section("🔧 Weaknesses", _bullet(weaknesses)))

    suggestions = data.get("improvement_suggestions", [])
    if suggestions:
        sections.append(_section("📈 Improvement Suggestions", _bullet(suggestions)))

    roadmap = data.get("learning_roadmap", {})
    roadmap_parts = []
    for priority, label in [("high", "High Priority"), ("medium", "Medium Priority"), ("low", "Low Priority")]:
        items = roadmap.get(priority, [])
        if items:
            roadmap_parts.append(f"*{escape(label)}*\n{_bullet(items)}")
    if roadmap_parts:
        sections.append(_section("📚 Learning Roadmap", "\n\n".join(roadmap_parts)))

    return "\n\n".join(sections) if sections else "No analysis data available."


def _msg4(data: dict) -> str:
    readiness = data.get("interview_readiness_percent", 0)
    reasons = data.get("interview_readiness_reason", [])
    lines = [
        f"🎯 *Interview Readiness: {readiness}%*",
        "",
    ]
    if reasons:
        lines.append(_bullet(reasons))
    lines.append("")
    lines.append("Use the buttons below to continue \\-\\- pick an option:")
    return "\n".join(lines)
