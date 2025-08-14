import re
from typing import List, Tuple
from sklearn.feature_extraction.text import TfidfVectorizer

def get_top_keywords(text: str, top_k: int = 20) -> List[Tuple[str, float]]:
    if not text or not text.strip():
        return []
    vectorizer = TfidfVectorizer(
        stop_words="english",
        ngram_range=(1,2),
        max_features=5000,
        min_df=1
    )

    X = vectorizer.fit_transform([text, text])
    weights = X.toarray().mean(axis=0)
    vocab = vectorizer.get_feature_names_out()
    pairs = list(zip(vocab, weights))
    pairs.sort(key=lambda x: x[1], reverse=True)
    return pairs[:top_k]

def normalize_keywords(keywords: List[str]) -> List[Tuple[str, str]]:
    norm = []
    for kw in keywords:
        k = kw.lower().strip()
        k = re.sub(r'[^a-z0-9+.# ]+', ' ', k)
        k = re.sub(r'\s+', ' ', k)
        norm.append((k, kw))
    seen = set()
    unique = []
    for k, orig in norm:
        if k not in seen:
            seen.add(k)
            unique.append((k, orig))
    return unique
