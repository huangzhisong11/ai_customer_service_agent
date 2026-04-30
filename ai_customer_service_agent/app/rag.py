import re
from pathlib import Path
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
from app.config import KNOWLEDGE_PATH

class KnowledgeBase:
    def __init__(self, path: str = KNOWLEDGE_PATH):
        self.path = Path(path)
        self.docs = []
        self.vectorizer = TfidfVectorizer()
        self.matrix = None
        self.load()

    def load(self) -> None:
        text = self.path.read_text(encoding="utf-8") if self.path.exists() else ""
        chunks = re.split(r"\n##\s+", text)
        clean = []
        for chunk in chunks:
            chunk = chunk.strip()
            if not chunk:
                continue
            if not chunk.startswith("#"):
                chunk = "## " + chunk
            clean.append(chunk)
        self.docs = clean or ["暂无知识库内容。"]
        self.matrix = self.vectorizer.fit_transform(self.docs)

    def search(self, query: str, top_k: int = 3) -> list[str]:
        if not query.strip():
            return []
        q = self.vectorizer.transform([query])
        scores = cosine_similarity(q, self.matrix)[0]
        ranked = scores.argsort()[::-1][:top_k]
        return [self.docs[i] for i in ranked if scores[i] > 0.02]
