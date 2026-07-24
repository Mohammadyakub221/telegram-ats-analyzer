import json
import os

from groq import AsyncGroq

client = AsyncGroq(api_key=os.environ["GROQ_API_KEY"])

SYSTEM_PROMPT = """You are an expert ATS resume analyzer. Analyze the given resume against the job description and return ONLY valid JSON (no other text) with this exact structure:

{
  "resume": { "name": "...", "email": "...", "phone": "...", "linkedin": "...", "github": "...",
              "education": "...", "experience": "...", "skills": [...], "certifications": "..." },
  "jd": { "company": "...", "role": "...", "required_skills": [...], "preferred_skills": [...],
          "required_experience": "...", "keywords": [...] },
  "matching_skills": [...],
  "missing_skills_critical": [...],
  "missing_skills_nice_to_have": [...],
  "experience_match": "...",
  "education_match": "...",
  "ats_score": 0-100,
  "score_breakdown": { "skills": 0-100, "experience": 0-100, "projects": 0-100, "education": 0-100,
                       "keywords": 0-100, "formatting": 0-100, "certifications": 0-100 },
  "strengths": [...],
  "weaknesses": [...],
  "improvement_suggestions": [...],
  "interview_readiness_percent": 0-100,
  "interview_readiness_reason": [...],
  "learning_roadmap": { "high": [...], "medium": [...], "low": [...] },
  "final_verdict": "Excellent Match | Strong Match | Good Match | Average Match | Weak Match",
  "verdict_reason": "..."
}

Rules:
- Use "Not Mentioned" for resume fields not present.
- Do not invent skills, experience, or certifications not in the source text.
- Compute ats_score as weighted average: skills 40%, experience 20%, projects 10%, education 10%, keywords 10%, formatting 5%, certifications 5%.
- Show the per-category scores in score_breakdown so the score is auditable."""


async def run_analysis(resume_text: str, jd_text: str) -> dict:
    user_prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
    messages = [
        {"role": "system", "content": SYSTEM_PROMPT},
        {"role": "user", "content": user_prompt},
    ]

    for attempt in range(2):
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.1,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            if attempt == 0:
                messages.append({"role": "assistant", "content": raw})
                messages.append({"role": "user", "content": "Return only valid JSON, no other text."})
            else:
                raise


REWRITE_PROMPT = """You are a professional resume rewrite expert. Given the resume and job description below, rewrite the weak or generic bullet points to be stronger, more quantifiable, and ATS-friendly. Return the rewritten bullet points as a JSON object with a single key "rewritten_bullets" containing an array of strings. Only return valid JSON."""


async def rewrite_resume(resume_text: str, jd_text: str) -> dict:
    user_prompt = f"Resume:\n{resume_text}\n\nJob Description:\n{jd_text}"
    messages = [
        {"role": "system", "content": REWRITE_PROMPT},
        {"role": "user", "content": user_prompt},
    ]
    for attempt in range(2):
        response = await client.chat.completions.create(
            model="llama-3.3-70b-versatile",
            messages=messages,
            temperature=0.3,
            response_format={"type": "json_object"},
        )
        raw = response.choices[0].message.content
        try:
            return json.loads(raw)
        except json.JSONDecodeError:
            if attempt == 0:
                messages.append({"role": "assistant", "content": raw})
                messages.append({"role": "user", "content": "Return only valid JSON, no other text."})
            else:
                raise
