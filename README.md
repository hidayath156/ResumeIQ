# ResumeIQ — AI-Enhanced Resume Builder

This project follows the supplied ResumeIQ screenshots and the stated stack: **HTML, CSS, JavaScript, Flask, MySQL, scikit-learn KNN and an LLM API**. No frontend framework is used.

## Features

- User registration and login
- Resume dashboard
- Create/open/delete resumes
- Contact, Summary, Education, Experience, Skills, Projects and Certifications tabs
- Modern, Classic and Compact templates
- Live resume preview
- KNN resume-quality evaluation using the supplied trained model
- Six required ML features: skills count, years of experience, education level, certifications count, project relevance and resume completeness
- Strong Resume / Moderate Resume / Needs Improvement classification
- KNN confidence, rubric score, model accuracy and recommendations
- LLM generation for professional summary, career objective, skill descriptions and project descriptions
- Print-ready resume page; browser Print → Save as PDF provides the PDF download without adding a PDF framework outside the required stack

## ML model supplied with the project

The supplied `resume_knn_model.pkl` contains a `StandardScaler` + distance-weighted `KNeighborsClassifier`, with `k=7`. The supplied training code defines the six features and three labels and exports both the pickle model and JSON metadata. The JSON reports test accuracy of 0.7944.

## 1. Create the MySQL database

Run `database/schema.sql` in MySQL.

## 2. Configure environment variables

Copy `.env.example` to your environment configuration and set the MySQL values.

Required MySQL variables:

- `MYSQL_HOST`
- `MYSQL_PORT`
- `MYSQL_USER`
- `MYSQL_PASSWORD`
- `MYSQL_DATABASE`

For Generative AI, configure:

- `LLM_API_URL`
- `LLM_API_KEY`
- `LLM_MODEL`

The LLM route uses an OpenAI-compatible chat-completions HTTP interface so the frontend/backend remains Flask + standard Python HTTP; no frontend AI SDK is introduced.

## 3. Install Python packages

```bash
pip install -r requirements.txt
```

## 4. Start Flask

```bash
python app.py
```

Open `http://127.0.0.1:5000`.

## 5. ML regeneration (only if you want to retrain)

The supplied training scripts are retained under `ML/`.

```bash
python ML/generate_dataset.py
python ML/train_knn.py
```

`train_knn.py` reads `ML/resume_dataset.csv`, uses the six specified features, performs a stratified 80/20 split, standardizes the features, trains KNN with `k=7` and distance weights, and writes `resume_knn_model.pkl` and `knn_model.json`.

## Important PDF note

The **Download PDF** button opens the exact print layout. Use the browser's Print dialog and choose **Save as PDF**. This keeps the implementation inside the requested HTML/CSS/JavaScript + Flask stack rather than introducing ReportLab, WeasyPrint or another PDF technology that was not in the project specification.

## Project structure

```text
ResumeIQ/
├── app.py
├── requirements.txt
├── .env.example
├── README.md
├── database/
│   └── schema.sql
├── ML/
│   ├── generate_dataset.py
│   ├── train_knn.py
│   ├── knn_model.json
│   └── resume_dataset.csv
├── models/
│   └── resume_knn_model.pkl
├── templates/
│   ├── base.html
│   ├── index.html
│   ├── auth.html
│   ├── dashboard.html
│   ├── editor.html
│   ├── resume_print.html
│   └── _resume_content.html
└── static/
    ├── css/style.css
    └── js/
        ├── app.js
        ├── auth.js
        ├── dashboard.js
        └── editor.js
```
