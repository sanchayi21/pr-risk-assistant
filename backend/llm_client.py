import os
import json
import httpx
from dotenv import load_dotenv

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
GROQ_MODEL = "llama-3.1-8b-instant"

async def review_diff_with_groq(diff: str) -> dict:
    """
    Sends a code diff to Groq and returns structured review as a dict.
    """

    prompt = f"""You are a senior software engineer doing a code review.

Analyze this git diff and return ONLY a JSON object with exactly these fields:
{{
    "summary": "2-3 sentence overall summary of the changes",
    "bugs": "describe any bugs or logic errors found, or null if none",
    "security_issues": "describe any security problems found, or null if none",
    "test_gaps": "describe missing tests or edge cases, or null if none",
    "risk_score": <a number from 1 to 10 where 1 is safe and 10 is very risky>
}}

Return ONLY the JSON. No explanation. No markdown. No extra text.

Git diff:
{diff[:3000]}
"""

    headers = {
        "Authorization": f"Bearer {GROQ_API_KEY}",
        "Content-Type": "application/json"
    }

    body = {
        "model": GROQ_MODEL,
        "messages": [
            {"role": "user", "content": prompt}
        ],
        "temperature": 0.3
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(
            "https://api.groq.com/openai/v1/chat/completions",
            headers=headers,
            json=body,
            timeout=30.0
        )

        if response.status_code != 200:
            raise Exception(f"Groq API error: {response.status_code} - {response.text}")

        data = response.json()
        content = data["choices"][0]["message"]["content"]

        # Parse the JSON response
        review = json.loads(content)
        return review