# Resume Screening & Job Matching Web Application

This repository contains a simple Flask-based web application for analyzing resumes and comparing them to job descriptions. It provides an ATS score, skill match, missing keywords, suggestions, and more.

## Features

- Upload resume (PDF or DOCX)
- Optional job description input
- Extract and preprocess resume text
- Compute similarity and ATS score
- Highlight missing keywords and skills
- Offer improvement suggestions and basic grammar checks
- Display best-suited job roles when JD is not provided

## Project Structure

```
project/
│── app.py
│── utils/
│   ├── parser.py
│   ├── analyzer.py
│   ├── scorer.py
│── templates/
│   └── index.html
│── static/
│   └── style.css
│── requirements.txt
│── README.md
```

## Setup Instructions

1. **Clone repository** or copy files to your workspace.
2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   source venv/bin/activate   # macOS/Linux
   venv\Scripts\activate    # Windows
   ```
3. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
4. **Download NLTK and spaCy data** (the code tries to auto-download missing NLTK corpora on first run):
   ```bash
   python -m nltk.downloader stopwords words punkt
   python -m spacy download en_core_web_sm
   ```
5. **Install additional dependencies** (if you added new requirements):
   ```bash
   pip install -r requirements.txt
   # or, if using conda:
   conda run -n base pip install -r requirements.txt
   ```
6. **Run the application**:
   ```bash
   python app.py
   ```
6. Open a browser and navigate to `http://127.0.0.1:5000/`.

## Docker Deployment

From the repository root, build and start the app with Docker Compose:

```bash
docker compose up --build
```

The container serves the Flask app on `http://127.0.0.1:5000/`.

The compose file mounts these host directories into the container so data persists across restarts:

- `./data` -> `/app/data`
- `./uploads` -> `/app/uploads`
- `./stored_resumes` -> `/app/stored_resumes`

## Usage

- Choose a resume file (PDF or DOCX).
- Optionally paste a job description text.
- Click **Analyze** and wait for results to be displayed below.

## Notes

- This is a beginner-friendly template. The logic is kept simple for clarity and demonstration.
- You can extend the skill list in `utils/analyzer.py` or add advanced NLP models.
- A sample resume dataset is included under `data/archive (1)/Resume/Resume.csv`. The `utils/dataset.py` module can read this file and analyze a batch of resumes, and it now supports ranking against a job description.
- Similarity is computed using semantic embeddings (Sentence-Transformers) for more meaningful comparisons.
- Skill extraction uses spaCy to pull phrases and named entities instead of simple keyword matching.
- User authentication has been added using Flask-Login with SQLite persistence; analyses are saved and can be reviewed later.
- New pages `/browse` and `/rank` let authenticated users explore the dataset and rank resumes.
- Frontend improvements include bullet lists, login/register forms and dataset browsing, and there is scaffolding for charts and downloadable reports.
- Database file is stored at `data/app.db` and is automatically created.
- For a production-ready system, consider secure keys, file storage (S3/Blob), better error handling, and integration with job listing APIs.

## Advanced Version

For an advanced AI version (BERT embeddings, ranking multiple resumes, etc.), use a more powerful backend with transformers and a database.

---
*Built by a Python AI engineer and full-stack developer.*
