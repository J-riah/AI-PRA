import json
import io
from datetime import datetime

import streamlit as st
import numpy as np
from sklearn.metrics.pairwise import cosine_similarity

from modules.parsing import extract_text_from_file
from modules.db import init_db, insert_analysis, fetch_history
from modules.utils import clean_text
from modules.nlp_utils import get_top_keywords, normalize_keywords

st.set_page_config(
    page_title="AI-PRA",
)

st.title("📄 AI-PRA (AI - Powered Resume Analyser)")
st.caption("Upload your resume and paste a Job Description (JD). We'll compute a match score using sentence embeddings and highlight missing keywords.")


@st.cache_resource(show_spinner=True)
def load_embedder():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer('all-MiniLM-L6-v2')

@st.cache_data(show_spinner=False)
def embed_texts(model_name, texts):
    from sentence_transformers import SentenceTransformer
    model = SentenceTransformer(model_name)
    return model.encode(texts, show_progress_bar=False, normalize_embeddings=True)


DB_PATH = "resume_analyzer.db"
init_db(DB_PATH)

with st.sidebar:
    st.header("🗂️ History")
    hist = fetch_history(DB_PATH, limit=20)
    if len(hist) == 0:
        st.info("No analyses yet.")
    else:
        for row in hist:
            _id, score, ts, file_name = row
            st.write(f"**#{_id}** • {score:.1f} • {ts} • {file_name or 'N/A'}")



uploaded = st.file_uploader("Upload Resume (PDF/DOCX/TXT)", type=["pdf", "docx", "txt"])
jd_text = st.text_area("Paste Job Description (JD)", height=220, placeholder="Paste or type the job description here...")

col1, col2 = st.columns([1,1])
with col1:
    topk = st.slider("How many top JD keywords to consider", 5, 40, 20, 1)
with col2:
    analyze_btn = st.button("🔍 Analyze", type="primary")




if analyze_btn:
    if uploaded is None:
        st.error("Please upload your resume.")
        st.stop()
    if not jd_text.strip():
        st.error("Please paste a Job Description.")
        st.stop()

    with st.spinner("Extracting text from resume..."):
        resume_text = extract_text_from_file(uploaded)

    if not resume_text.strip():
        st.error("Could not extract text from the uploaded file.")
        st.stop()

    # clena and prep
    resume_text_clean = clean_text(resume_text)
    jd_text_clean = clean_text(jd_text)

    # embeddings and similarity
    with st.spinner("Computing embeddings and similarity..."):
        model_name = 'all-MiniLM-L6-v2'
        embeddings = embed_texts(model_name, [resume_text_clean, jd_text_clean])
        resume_vec, jd_vec = embeddings[0].reshape(1,-1), embeddings[1].reshape(1,-1)
        sim = float(cosine_similarity(resume_vec, jd_vec)[0][0])
        score_pct = max(0.0, min(100.0, sim * 100))

    # Keyword extraction & gap analysis
    with st.spinner("Extracting keywords and finding gaps..."):
        jd_keywords_scored = get_top_keywords(jd_text_clean, top_k=topk)
        jd_keywords = [kw for kw, wt in jd_keywords_scored]
        jd_keywords_norm = normalize_keywords(jd_keywords)
        resume_lower = resume_text_clean.lower()

        matched = []
        missing = []
        for kw_norm, original_kw in jd_keywords_norm:
            if kw_norm in resume_lower:
                matched.append(original_kw)
            else:
                missing.append(original_kw)

    # Display results
    st.subheader("✅ Results")
    st.metric("Job Match Score", f"{score_pct:.1f}%")

    st.progress(score_pct / 100.0)

    c1, c2 = st.columns(2)
    with c1:
        st.markdown("**Matched Keywords**")
        if matched:
            st.write(", ".join(sorted(set(matched))))
        else:
            st.write("_None matched_")

    with c2:
        st.markdown("**Missing Keywords**")
        if missing:
            st.write(", ".join(sorted(set(missing))))
        else:
            st.write("_None missing_")

    file_name = getattr(uploaded, "name", None)
    insert_analysis(
        DB_PATH,
        resume_text=resume_text_clean,
        job_desc=jd_text_clean,
        score=score_pct,
        matched_keywords=json.dumps(matched, ensure_ascii=False),
        missing_keywords=json.dumps(missing, ensure_ascii=False),
        file_name=file_name
    )

    report = {
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "file_name": file_name,
        "score_percent": round(score_pct, 1),
        "matched_keywords": matched,
        "missing_keywords": missing,
        "top_jd_keywords_considered": jd_keywords,
    }
    st.download_button(
        label="⬇️ Download JSON Report",
        file_name="resume_analysis_report.json",
        mime="application/json",
        data=json.dumps(report, indent=2, ensure_ascii=False)
    )

    with st.expander("📄 Preview Extracted Resume Text", expanded=False):
        st.write(resume_text_clean[:4000] + ("..." if len(resume_text_clean) > 4000 else ""))

    with st.expander("🧾 Job Description (Cleaned)", expanded=False):
        st.write(jd_text_clean)

else:
    st.info("Upload a resume and paste a JD, then click **Analyze**.")

