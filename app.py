from flask import Flask, render_template, request
import os
import PyPDF2
import re

app = Flask(__name__)

UPLOAD_FOLDER = 'uploads'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER


def extract_text(pdf_path):

    text = ""

    with open(pdf_path, 'rb') as file:

        reader = PyPDF2.PdfReader(file)

        for page in reader.pages:
            text += page.extract_text()

    return text


@app.route('/')
def home():

    return render_template('index.html')


@app.route('/analyze', methods=['POST'])
def analyze():

    file = request.files['resume']

    if file:

        filepath = os.path.join(
            app.config['UPLOAD_FOLDER'],
            file.filename
        )

        file.save(filepath)

        resume_text = extract_text(filepath)

        job_description = request.form['job_description']

        resume_text = resume_text.lower()
        job_description = job_description.lower()

        resume_text = re.sub(
            r'[^a-zA-Z0-9 ]',
            ' ',
            resume_text
        )

        job_description = re.sub(
            r'[^a-zA-Z0-9 ]',
            ' ',
            job_description
        )

        resume_words = set(
            resume_text.split()
        )

        job_words = set(
            job_description.split()
        )

        skill_mapping = {

            "sql": [
                "mysql",
                "postgresql",
                "sqlite",
                "oracle"
            ],

            "python": [
                "flask",
                "django",
                "fastapi"
            ],

            "javascript": [
                "js",
                "react",
                "nodejs",
                "vue"
            ],

            "html": [
                "html5"
            ],

            "cloud": [
                "aws",
                "azure",
                "gcp"
            ]

        }

        matched_skills = []

        for job_skill in job_words:

            if job_skill in resume_words:

                matched_skills.append(job_skill)

            elif job_skill in skill_mapping:

                related_skills = skill_mapping[job_skill]

                for related_skill in related_skills:

                    if related_skill in resume_words:

                        matched_skills.append(job_skill)

                        break

        missing_skills = []

        for skill in job_words:

            if skill not in matched_skills:

                missing_skills.append(skill)

        matched_count = len(
            matched_skills
        )

        total_words = len(
            job_words
        )

        score = (
            matched_count / total_words
        ) * 100

        return render_template(
            'result.html',
            score=round(score, 2),
            matched_skills=matched_skills,
            missing_skills=missing_skills
        )

    return "No File Uploaded"


if __name__ == '__main__':

    app.run(debug=True)