
import fitz  # PyMuPDF
from docx import Document


def extract_resume_text(uploaded_file):
    """Extract text from PDF, DOCX, or TXT resume files."""

    file_name = uploaded_file.name.lower()

    try:
        # Extract text from PDF
        if file_name.endswith(".pdf"):
            pdf_document = fitz.open(
                stream=uploaded_file.getvalue(),
                filetype="pdf"
            )

            text = ""
            for page in pdf_document:
                text += page.get_text() + "\n"

            pdf_document.close()
            return text.strip()

        # Extract text from DOCX
        elif file_name.endswith(".docx"):
            document = Document(uploaded_file)

            text = "\n".join(
                paragraph.text
                for paragraph in document.paragraphs
            )

            return text.strip()

        # Extract text from TXT
        elif file_name.endswith(".txt"):
            return uploaded_file.getvalue().decode(
                "utf-8",
                errors="replace"
            ).strip()

        else:
            return "Unsupported file format."

    except Exception as error:
        return f"Error reading resume: {error}"



import re

# Common skills grouped by category
SKILL_CATEGORIES = {
    "Programming": [
        "Python", "Java", "JavaScript", "C++", "C#"
    ],
    "Data Analysis": [
        "SQL", "Excel", "Power BI", "Tableau",
        "Pandas", "NumPy", "Statistics", "EDA",
        "Data Cleaning", "Data Visualization"
    ],
    "Machine Learning": [
        "Machine Learning", "Deep Learning",
        "Scikit-learn", "TensorFlow", "PyTorch",
        "NLP", "Regression", "Classification"
    ],
    "Web Development": [
        "HTML", "CSS", "Angular", "React",
        "Node.js", "Flask", "Django"
    ],
    "Tools": [
        "Git", "GitHub", "Jupyter", "Streamlit",
        "MySQL", "MongoDB"
    ],
    "Digital Marketing": [
        "SEO", "Google Ads", "Meta Ads", "PPC",
        "Email Marketing", "Google Analytics"
    ],
    "Testing": [
        "Manual Testing", "Automation Testing",
        "Selenium", "STLC", "SDLC",
        "Test Case Design", "Regression Testing"
    ]
}


def extract_skills(text):
    """Find recognized skills in text."""

    found_skills = []
    text_lower = text.lower()

    for category, skills in SKILL_CATEGORIES.items():
        for skill in skills:
            # Match whole phrases/words, ignoring case
            pattern = r"(?<!\w)" + re.escape(skill.lower()) + r"(?!\w)"

            if re.search(pattern, text_lower):
                found_skills.append(skill)

    return sorted(set(found_skills))


def analyze_job_gap(resume_text, job_description):
    """Compare resume skills with job requirements."""

    resume_skills = extract_skills(resume_text)
    required_skills = extract_skills(job_description)

    matched_skills = [
        skill for skill in required_skills
        if skill.lower() in {
            item.lower() for item in resume_skills
        }
    ]

    missing_skills = [
        skill for skill in required_skills
        if skill.lower() not in {
            item.lower() for item in resume_skills
        }
    ]

    if required_skills:
        match_score = round(
            len(matched_skills) / len(required_skills) * 100
        )
    else:
        match_score = 0

    return {
        "resume_skills": resume_skills,
        "required_skills": required_skills,
        "matched_skills": matched_skills,
        "missing_skills": missing_skills,
        "match_score": match_score
    }


def recommend_learning(missing_skills):
    """Suggest learning topics and practice tasks."""

    recommendations = {
        "Python": (
            "Learn variables, loops, functions, and data structures.",
            "Build a small data-processing program."
        ),
        "SQL": (
            "Learn SELECT, JOIN, GROUP BY, subqueries, and window functions.",
            "Solve employee and sales database queries."
        ),
        "Excel": (
            "Learn formulas, XLOOKUP, PivotTables, and charts.",
            "Create an interactive sales report."
        ),
        "Power BI": (
            "Learn Power Query, data modeling, DAX, and dashboards.",
            "Build a sales performance dashboard."
        ),
        "Tableau": (
            "Learn charts, filters, calculated fields, and dashboards.",
            "Build a sales dashboard."
        ),
        "Statistics": (
            "Learn descriptive statistics, probability, and correlation.",
            "Analyze trends in a sales dataset."
        ),
        "Pandas": (
            "Learn DataFrames, filtering, grouping, and data cleaning.",
            "Clean and analyze a CSV dataset."
        ),
        "NumPy": (
            "Learn arrays, indexing, vectorization, and numerical operations.",
            "Perform numerical analysis on sample data."
        ),
        "Machine Learning": (
            "Learn supervised learning, model evaluation, and feature engineering.",
            "Build a simple prediction model."
        ),
        "HTML": (
            "Learn semantic HTML, forms, and page structure.",
            "Create a personal portfolio webpage."
        ),
        "CSS": (
            "Learn selectors, Flexbox, Grid, and responsive design.",
            "Style a responsive portfolio webpage."
        ),
        "Java": (
            "Learn OOP, collections, exception handling, and file handling.",
            "Build a simple student management application."
        ),
        "Manual Testing": (
            "Learn test cases, test scenarios, and defect reporting.",
            "Write test cases for a login page."
        ),
        "Regression Testing": (
            "Learn how to verify existing functionality after changes.",
            "Prepare a regression test suite for a sample application."
        ),
        "SEO": (
            "Learn keyword research, on-page SEO, and technical SEO.",
            "Perform an SEO audit of a sample website."
        ),
        "Google Ads": (
            "Learn campaign structure, keywords, targeting, and conversion tracking.",
            "Create a mock search advertising campaign."
        )
    }

    results = []

    for skill in missing_skills:
        if skill in recommendations:
            learning, practice = recommendations[skill]
        else:
            learning = f"Study the fundamentals of {skill}."
            practice = f"Complete a small project using {skill}."

        results.append({
            "skill": skill,
            "learning": learning,
            "practice": practice
        })

    return results
