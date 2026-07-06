import os

# pyrefly: ignore [missing-import]
from pydantic import BaseModel, Field

# pyrefly: ignore [missing-import]
from google import genai

# pyrefly: ignore [missing-import]
from google.genai import types


class GradeResult(BaseModel):
    score: int = Field(
        ...,
        description="The SM-2 score from 0 to 5 based on how well the user answered the question.",
    )
    feedback: str = Field(
        ...,
        description="Constructive and concise feedback explaining the grade and what points were correct or missing.",
    )


def grade_answer(
    question: str, expected_answer: str, user_answer: str, api_key: str = None
) -> tuple[int, str]:
    """Grades a user's answer against the expected answer using the Google Gemini API.

    Parameters:
    - question (str): The review question asked.
    - expected_answer (str): The expected correct details.
    - user_answer (str): The answer submitted by the user.
    - api_key (str): Optional Gemini API key. If not provided, the SDK will look for
                      the GEMINI_API_KEY environment variable.

    Returns:
    - tuple: (score, feedback)
             score (int): SM-2 quality score from 0 to 5.
             feedback (str): Constructive feedback explaining the grade.
    """
    # 1. Check if Gemini API key is configured
    effective_api_key = api_key or os.getenv("GEMINI_API_KEY")
    if not effective_api_key or effective_api_key.startswith("your_gemini_api_key"):
        # If API key is missing, raise a friendly ValueError
        raise ValueError(
            "Gemini API key is not configured. Please set the GEMINI_API_KEY "
            "environment variable in your .env file."
        )

    # 2. Initialize the Gemini Client
    # Passing the api_key explicitly if provided, otherwise client looks at os.environ["GEMINI_API_KEY"]
    client = genai.Client(api_key=effective_api_key)

    # 3. Formulate the prompt
    prompt = f"""
You are an AI learning assistant grading a student's answer for a spaced repetition system.

Review details:
- Question / Concept Prompt: {question}
- Expected Answer / Key Points: {expected_answer}
- User's Answer: {user_answer}

Grade the user's answer using the SuperMemo-2 (SM-2) scale (0 to 5):
- 5: Perfect response. Fully correct, complete, and contains no errors.
- 4: Correct response after hesitation or minor omissions.
- 3: Correct response, but with significant omissions or difficulties.
- 2: Incorrect response, but it seemed easy to recall (e.g. user was very close or got some concepts right).
- 1: Incorrect response, but user remembered the concept name.
- 0: Complete blackout, blank answer, or completely wrong.

Generate your grading response conforming to the JSON schema. Be encouraging and concise in your feedback.
"""

    # 4. Request Structured Output from Gemini with retry logic for 503 errors
    import time

    # pyrefly: ignore [missing-import]
    from google.genai.errors import APIError

    retries = 3
    backoff_times = [2, 4, 8]
    response = None

    for attempt in range(retries + 1):
        try:
            # We use gemini-2.5-flash as the fast, high-quality default model
            response = client.models.generate_content(
                model="gemini-2.5-flash",
                contents=prompt,
                config=types.GenerateContentConfig(
                    response_mime_type="application/json",
                    response_schema=GradeResult,
                    temperature=0.2,  # Low temperature for more consistent, objective grading
                ),
            )
            break
        except APIError as e:
            if e.code == 503 and attempt < retries:
                wait_time = backoff_times[attempt]
                print(
                    f"\n[Gemini API] Attempt {attempt + 1} (503 Service Unavailable). Retrying in {wait_time} seconds (Retry {attempt + 1}/{retries})..."
                )
                time.sleep(wait_time)
                continue

            # Logging final failure reason before raising
            if e.code == 503:
                print(
                    f"\n[Gemini API] Attempt {attempt + 1} failed. All {retries} retries exhausted. Final failure reason: 503 Service Unavailable."
                )
            else:
                print(
                    f"\n[Gemini API] Request failed. Final failure reason: Code {e.code} - {e.message}"
                )
            raise e

    try:
        # The response.text will be a valid JSON matching GradeResult
        # We can parse it using Pydantic
        result = GradeResult.model_validate_json(response.text)
        # Ensure the score is bounded between 0 and 5
        score = max(0, min(5, result.score))
        return score, result.feedback
    except Exception as e:
        print(f"Error parsing Gemini response: {e}")
        print(f"Raw response was: {response.text}")
        # Fallback in case of parsing error
        return (
            3,
            f"Feedback could not be parsed. (Raw response: {response.text})",
        )
