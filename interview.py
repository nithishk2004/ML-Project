
import ollama


def generate_interview_questions(
    target_role,
    matched_skills,
    missing_skills,
    difficulty,
    number_of_questions
):

    prompt = f"""
    You are an experienced technical interviewer.

    Generate {number_of_questions} interview questions
    for the following job role:

    Target Job Role: {target_role}

    Candidate's Matched Skills:
    {", ".join(matched_skills) or "None"}

    Candidate's Missing Skills:
    {", ".join(missing_skills) or "None"}

    Difficulty Level: {difficulty}

    Requirements:

    1. Generate questions relevant to the target job role.
    2. Include questions about matched skills.
    3. Include questions about missing skills.
    4. Include technical and practical questions.
    5. Provide a simple sample answer for every question.
    6. Explain answers in beginner-friendly language.
    7. Number each question clearly.

    Use this format:

    Question 1:
    [Interview question]

    Sample Answer:
    [Answer]

    Repeat for all questions.
    """

    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as error:
        return f"Interview question generation failed: {error}"


def evaluate_interview_answer(question, user_answer, target_role):

    prompt = f"""
    You are an experienced technical interviewer.

    Target Job Role: {target_role}

    Interview Question:
    {question}

    Candidate's Answer:
    {user_answer}

    Evaluate the candidate's answer.

    Provide the following:

    1. Score out of 10.
    2. What the candidate did well.
    3. What is missing or incorrect.
    4. How to improve the answer.
    5. A better sample answer.

    Be supportive and beginner-friendly.
    Give honest feedback.
    Do not give a high score just to encourage the candidate.
    """

    try:
        response = ollama.chat(
            model="llama3.2:1b",
            messages=[
                {
                    "role": "user",
                    "content": prompt
                }
            ]
        )

        return response["message"]["content"]

    except Exception as error:
        return f"Answer evaluation failed: {error}"
