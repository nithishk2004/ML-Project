
import ollama


def ask_career_assistant(
    question,
    target_role,
    match_score,
    matched_skills,
    missing_skills
):
    context = f"""
    Target job role: {target_role}
    Resume skill match score: {match_score}%
    Matched skills: {", ".join(matched_skills) or "None"}
    Missing recognized skills: {", ".join(missing_skills) or "None"}
    """

    instructions = """
    You are an AI career assistant for a Resume Job Gap Analyzer.

    Help users improve their resumes and prepare for their target roles.
    Give beginner-friendly explanations and practical steps.
    When asked for a learning plan, organize it by week.
    Recommend projects related to the target job role.
    Explain that a missing resume keyword does not necessarily mean
    the user lacks that skill.
    Use the supplied resume analysis to personalize your answers.
    """

    prompt = f"""
    {instructions}

    Resume analysis:
    {context}

    User question:
    {question}
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
        return (
            "Could not connect to Ollama. "
            "Please make sure Ollama is running and the "
            "llama3.2:1b model is installed. "
            f"Details: {error}"
        )
