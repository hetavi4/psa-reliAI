import numpy as np, pandas as pd
from pathlib import Path
from sentence_transformers import SentenceTransformer

# Try FAISS; fall back to sklearn-only if unavailable
try:
    import faiss  # type: ignore
    HAVE_FAISS = True
except Exception:
    HAVE_FAISS = False

PREP = Path("data/prepared")
EMB  = Path("data/embeddings")
EMB.mkdir(parents=True, exist_ok=True)

MODEL = "sentence-transformers/all-MiniLM-L6-v2"

def build(name: str):
    df = pd.read_csv(PREP / f"{name}.csv")
    texts = df["text"].astype(str).tolist()
    model = SentenceTransformer(MODEL)
    vecs = model.encode(texts, normalize_embeddings=True, show_progress_bar=True)
    vecs = np.asarray(vecs, dtype="float32")

    # Save vectors + metadata for both FAISS and sklearn paths
    np.save(EMB / f"{name}.npy", vecs)
    df.to_csv(EMB / f"{name}_meta.csv", index=False)

    if HAVE_FAISS:
        index = faiss.IndexFlatIP(vecs.shape[1])  # cosine via normalized vectors
        index.add(vecs)
        faiss.write_index(index, str(EMB / f"{name}.index"))
        print(f"[FAISS] Built {name}: {vecs.shape}")
    else:
        print(f"[SKLEARN] Saved {name} vectors: {vecs.shape} (FAISS not installed)")

if __name__ == "__main__":
    build("cases")
    build("knowledge")
