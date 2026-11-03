import pandas as pd
import plotly.express as px
from interview import (
    generate_interview_questions,
    evaluate_interview_answer
)

import streamlit.components.v1 as components

from career_assistant import ask_career_assistant

from database import (
    initialize_database,
    save_analysis,
    get_analysis_history,
    save_interview_result,
    get_interview_history
)

initialize_database()

from analyzer import (
    extract_resume_text,
    analyze_job_gap,
    recommend_learning
)
import streamlit as st
import re

st.set_page_config(
    page_title="AI Resume Job Gap Analyzer",
    page_icon="🧭",
    layout="wide"
)

st.title("AI Resume Job Gap Analyzer")

st.write(
    "Analyze your resume, identify potential skill gaps, "
    "and get personalized career guidance."
)

st.subheader("User Profile")

user_name = st.text_input("Your name")
user_email = st.text_input("Your email address")

st.subheader("Upload your resume")

resume = st.file_uploader(
    "Choose your resume",
    type=["pdf", "docx", "txt"]
)

st.subheader("Enter the job description")

job_description = st.text_area(
    "Paste the job description here",
    height=200
)

job_role = st.selectbox(
    "Select your target role",
    [
        "Data Analyst",
        "Software Developer",
        "Software Tester / QA",
        "Digital Marketing Executive",
        "Data Scientist / ML Engineer"
    ]
)


if st.button("Analyze Resume"):
    if resume is None:
        st.error("Please upload your resume.")

    elif not job_description.strip():
        st.error("Please enter a job description.")

    else:
        resume_text = extract_resume_text(resume)

        if resume_text.startswith("Error reading resume:"):
            st.error(resume_text)

        elif not resume_text:
            st.warning("No text found in the uploaded resume.")

        else:
            st.success("Resume text extracted successfully!")

            result = analyze_job_gap(
                resume_text,
                job_description
            )

            st.session_state["career_context"] = {
                 "target_role": job_role,
                 "match_score": result["match_score"],
                 "matched_skills": result["matched_skills"],
                 "missing_skills": result["missing_skills"]
            }

            
            if not user_name.strip() or not user_email.strip():
                st.warning(
                    "Please enter your name and email "
                    "in the User Profile section."
                )
                st.stop()

            save_analysis(
                name=user_name.strip(),
                email=user_email.strip().lower(),
                target_role=job_role,
                resume_filename=resume.name,
                job_description=job_description,
                result=result
            )

            st.success("Analysis saved to your database!")

            
            st.subheader("📊 Resume Analysis Dashboard")

            # Summary metrics
            total_required = len(result["required_skills"])
            total_matched = len(result["matched_skills"])
            total_missing = len(result["missing_skills"])

            col1, col2, col3 = st.columns(3)

            col1.metric("Required Skills", total_required)
            col2.metric("Matched Skills", total_matched)
            col3.metric("Missing Skills", total_missing)

            # Pie chart
            if total_required > 0:
                chart_data = {
                    "Skill Status": ["Matched", "Missing"],
                    "Count": [total_matched, total_missing]
                }

                fig = px.pie(
                    chart_data,
                    names="Skill Status",
                    values="Count",
                    title="Matched vs Missing Skills",
                    hole=0.4
                )

                st.plotly_chart(fig, use_container_width=True)

            # Bar chart
            if result["resume_skills"]:
                resume_chart_data = {
                    "Skill": result["resume_skills"],
                    "Status": [
                        "Found in Resume"
                        for skill in result["resume_skills"]
                    ]
                }

                fig2 = px.bar(
                    resume_chart_data,
                    x="Skill",
                    title="Skills Identified in Your Resume"
                )

                fig2.update_layout(
                    xaxis_tickangle=-45,
                    showlegend=False
                )

                st.plotly_chart(
                    fig2,
                    use_container_width=True
                )


            st.subheader("Resume Skills")

            if result["resume_skills"]:
                st.write(", ".join(result["resume_skills"]))
            else:
                st.info("No recognized skills found in the resume.")

            st.subheader("Job Analysis Results")

            st.metric(
                "Skill Match Score",
                f'{result["match_score"]}%'
            )

            col1, col2 = st.columns(2)

            with col1:
                st.subheader("Matched Skills")

                if result["matched_skills"]:
                    for skill in result["matched_skills"]:
                        st.success(skill)
                else:
                    st.write("No matching skills found.")

            with col2:
                st.subheader("Missing Skills")

                if result["missing_skills"]:
                    for skill in result["missing_skills"]:
                        st.warning(skill)
                else:
                    st.write("No missing recognized skills.")

            st.subheader("Required Skills Found in Job Description")

            st.write(
                ", ".join(result["required_skills"])
                or "No recognized skills found."
            )


            st.subheader("Personalized Learning Recommendations")

            recommendations = recommend_learning(
                result["missing_skills"]
            )

            if recommendations:
                for item in recommendations:
                    with st.expander(
                        f"How to improve: {item['skill']}"
                    ):
                        st.write("**What to learn:**")
                        st.write(item["learning"])

                        st.write("**Practice project:**")
                        st.write(item["practice"])
            else:
                st.success(
                    "No recognized skill gaps found! "
                    "Review the job requirements to confirm."
                )


# st.divider()
# st.subheader("Analysis History")
# =====================================
# RESUME ANALYSIS HISTORY
# =====================================

st.divider()

st.header("📋 Resume Analysis History")

history_email = st.text_input(
    "Enter your email to view saved analyses",
    key="history_email"
)

if st.button("View History"):

    if not history_email.strip():

        st.warning("Please enter your email address.")

    else:

        history = get_analysis_history(
            history_email.strip().lower()
        )

        if history:

            st.success("Analysis history loaded successfully!")

            df = pd.DataFrame(history)

            # Select only the five required columns
            df = df[
                [
                    "Analysis ID",
                    "Target Role",
                    "Match Score (%)",
                    "Matched Skills",
                    "Missing Skills"
                ]
            ]

            st.subheader("Previous Resume Analyses")

            st.dataframe(
                df,
                use_container_width=True,
                hide_index=True,
                height=400
            )

        else:

            st.info(
                "No previous analyses found for this email."
            )

st.divider()
st.header("🤖 AI Career Assistant")

st.write(
    "Ask questions about your skill gaps, learning roadmap, "
    "projects, or interview preparation."
)

if "career_chat" not in st.session_state:
    st.session_state["career_chat"] = []

if "career_context" not in st.session_state:
    st.info(
        "Analyze a resume first to give the assistant "
        "your latest skill analysis."
    )
else:
    context = st.session_state["career_context"]

    for message in st.session_state["career_chat"]:
        with st.chat_message(message["role"]):
            st.markdown(message["content"])

    question = st.chat_input(
        "Ask a career question..."
    )

    if question:
        st.session_state["career_chat"].append({
            "role": "user",
            "content": question
        })

        with st.chat_message("user"):
            st.markdown(question)

        with st.chat_message("assistant"):

            # Create an anchor at the beginning of the answer
            st.markdown(
                '<div id="latest-ai-answer"></div>',
                unsafe_allow_html=True
            )

            with st.spinner("Thinking..."):
                answer = ask_career_assistant(
                    question=question,
                    target_role=context["target_role"],
                    match_score=context["match_score"],
                    matched_skills=context["matched_skills"],
                    missing_skills=context["missing_skills"]
                )

                st.markdown(answer)

        # Automatically scroll to the latest AI answer
        # Automatically scroll to the latest AI answer
        components.html(
            """
            <script>
                function scrollToLatestAnswer() {
                    const parentDoc = window.parent.document;

                    const answer = parentDoc.getElementById(
                        "latest-ai-answer"
                    );

                    if (answer) {
                        answer.scrollIntoView({
                            behavior: "smooth",
                            block: "start"
                        });
                    }
                }

                setTimeout(scrollToLatestAnswer, 300);
                setTimeout(scrollToLatestAnswer, 800);
                setTimeout(scrollToLatestAnswer, 1200);
            </script>
            """,
            height=0
        )

        st.session_state["career_chat"].append({
            "role": "assistant",
            "content": answer
        })


# =====================================
# AI INTERVIEW PREPARATION MODULE
# =====================================

st.divider()

st.header("🎯 AI Interview Preparation")

st.write(
    "Prepare for your job interviews with AI-generated "
    "questions and sample answers based on your resume."
)

if "career_context" not in st.session_state:

    st.warning(
        "Please analyze your resume first to access "
        "personalized interview preparation."
    )

else:

    context = st.session_state["career_context"]

    st.write(
        f"**Target Job Role:** {context['target_role']}"
    )

    difficulty = st.selectbox(
        "Select Interview Difficulty",
        ["Beginner", "Intermediate", "Advanced"]
    )

    number_of_questions = st.slider(
        "Number of Interview Questions",
        min_value=3,
        max_value=15,
        value=5
    )

    if st.button("Generate Interview Questions"):

        with st.spinner(
            "Ollama is generating your interview questions..."
        ):

            interview_result = generate_interview_questions(
                target_role=context["target_role"],
                matched_skills=context["matched_skills"],
                missing_skills=context["missing_skills"],
                difficulty=difficulty,
                number_of_questions=number_of_questions
            )

            st.session_state["interview_result"] = interview_result

    if "interview_result" in st.session_state:

        st.subheader("Your Interview Questions")

        st.markdown(
            st.session_state["interview_result"]
        )

# =====================================
# AI INTERVIEW ANSWER EVALUATION
# =====================================

st.divider()

st.header("📝 Practice Your Interview Answers")

st.write(
    "Enter an interview question and your answer. "
    "The AI will evaluate your response and suggest improvements."
)

if "career_context" in st.session_state:

    context = st.session_state["career_context"]

    interview_question = st.text_area(
        "Enter or copy an interview question",
        placeholder="Example: What is the difference between SQL and Python?"
    )

    user_answer = st.text_area(
        "Write your answer",
        placeholder="Type your interview answer here...",
        height=180
    )

    if st.button("Evaluate My Answer"):

        if not interview_question.strip():
            st.warning("Please enter an interview question.")

        elif not user_answer.strip():
            st.warning("Please write your answer first.")

        else:

            with st.spinner("AI is evaluating your answer..."):

                feedback = evaluate_interview_answer(
                    question=interview_question,
                    user_answer=user_answer,
                    target_role=context["target_role"]
                )

                st.session_state["answer_feedback"] = feedback

                score_match = re.search(
                    r"Score:\s*(\d+(?:\.\d+)?)\s*(?:out of 10)?",
                    feedback,
                    re.IGNORECASE
                )

                if score_match:

                    score = float(score_match.group(1))

                    save_interview_result(
                        email=user_email.strip().lower(),
                        target_role=context["target_role"],
                        question=interview_question,
                        user_answer=user_answer,
                        feedback=feedback,
                        score=score
                    )

                    st.success(
                        "Interview result saved successfully!"
                    )

                else:
                    st.warning(
                        "Feedback generated, but the score "
                        "could not be identified. Result not saved."
                    )

    if "answer_feedback" in st.session_state:

        st.subheader("📊 Your Interview Feedback")

        st.markdown(
            st.session_state["answer_feedback"]
        )

else:

    st.warning(
        "Please analyze your resume first to use answer practice."
    )



# =====================================
# INTERVIEW PERFORMANCE HISTORY
# =====================================

st.divider()

st.header("📈 Interview Performance History")

st.write(
    "Track your previous interview attempts, scores, "
    "and performance over time."
)

if st.button("View Interview History"):

    if not user_email.strip():

        st.warning("Please enter your email address.")

    else:

        history = get_interview_history(
            user_email.strip().lower()
        )

        if history:

            st.success("Interview history loaded successfully!")

            # Convert database records into a table
            history_data = []

            for row in history:

                history_data.append({
                    "ID": row[0],
                    "Target Role": row[1],
                    "Question": row[2],
                    "Score": row[3],
                    "Date": row[4]
                })

            # Display performance metrics
            total_attempts = len(history_data)

            average_score = sum(
                item["Score"] for item in history_data
            ) / total_attempts

            col1, col2 = st.columns(2)

            col1.metric(
                "Total Questions Attempted",
                total_attempts
            )

            col2.metric(
                "Average Interview Score",
                f"{average_score:.1f}/10"
            )

            # Display history table
            st.subheader("Previous Interview Attempts")

            st.dataframe(
                history_data,
                use_container_width=True,
                hide_index=True
            )

            # Display score chart
            st.subheader("Interview Score Progress")

            chart_data = {
                "Attempt": list(
                    range(1, total_attempts + 1)
                ),
                "Score": [
                    item["Score"] for item in reversed(history_data)
                ]
            }

            fig = px.line(
                chart_data,
                x="Attempt",
                y="Score",
                markers=True,
                title="Your Interview Performance"
            )

            fig.update_yaxes(range=[0, 10])

            st.plotly_chart(
                fig,
                use_container_width=True
            )

        else:

            st.info(
                "No interview practice history found for this email."
            )
