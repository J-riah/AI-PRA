# AI-PRA (AI-Powered Resume Analyzer)

A **Streamlit** web app that scores how well a resume matches a given job description using **Sentence-BERT embeddings** and shows **missing keywords/skills**.  
All analyses are saved in a local **SQLite** database for history and reporting.

## Tech
- Python, Streamlit
- NLP: sentence-transformers (`all-MiniLM-L6-v2`)
- Similarity: cosine similarity
- Keyword extraction: TF-IDF (1–2 grams)
- Storage: SQLite

## Quickstart

```bash
# 1) Clone or download this folder
cd ai_resume_analyzer

# 2) Create and activate a virtualenv (recommended)
python -m venv .venv
# Windows:
.venv\Scripts\activate
# macOS/Linux:
source .venv/bin/activate

# 3) Install dependencies
pip install -r requirements.txt

# 4) Run the app
streamlit run app.py
```

Open the URL Streamlit prints (usually http://localhost:8501).

## Try it quickly
Use the sample files in `samples/`:
- `sample_resume.txt`
- `sample_job_desc.txt`

## Database
A local SQLite DB `resume_analyzer.db` is created automatically with a single table `analyses`.  
Columns:
- `id` (PK), `resume_text`, `job_desc`, `score`, `matched_keywords`, `missing_keywords`, `timestamp`, `file_name`

## Deploy on Streamlit Community Cloud
1. Push this project to a **public GitHub repo**.
2. Go to Streamlit Community Cloud.
3. New app → point to your repo → set `app.py` as the entry file.
4. Click Deploy.

## Project Structure
```
ai_resume_analyzer/
├─ app.py
├─ modules/
│  ├─ __init__.py
│  ├─ parsing.py
│  ├─ nlp_utils.py
│  ├─ db.py
│  └─ utils.py
├─ samples/
│  ├─ sample_resume.txt
│  └─ sample_job_desc.txt
├─ requirements.txt
├─ README.md
└─ .gitignore
```

## Notes
- The app uses `all-MiniLM-L6-v2` which downloads on first run. That's normal.
- If you want to switch models, edit `load_embedder()` in `app.py`.
- You can export a single analysis as JSON from the UI.
