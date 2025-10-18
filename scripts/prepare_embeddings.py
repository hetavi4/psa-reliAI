import re
import pandas as pd
from docx import Document
from pathlib import Path

# Define folder paths
RAW = Path("data/raw")
PREP = Path("data/prepared")
PREP.mkdir(parents=True, exist_ok=True)

# Helper function to clean text
def clean(x):
    s = "" if pd.isna(x) else str(x)
    s = re.sub(r"\s+", " ", s).strip()
    return s

# ---- Process Case Log (Excel) ----
cases_xls = RAW / "Case Log.xlsx"
cases_df = pd.read_excel(cases_xls).fillna("")
cols = [c.strip().lower() for c in cases_df.columns]
cases_df.columns = cols

# Function to automatically find column names
def pick(colopts):
    for key in colopts:
        for c in cols:
            if key in c:
                return c
    return None

# Identify possible columns
id_col   = pick(["module", "case", "id"]) or cols[0]
sum_col  = pick(["problem statements", "problem", "alert / email", "alert"]) or cols[0]
root_col = pick(["solution", "sop"]) or None
res_col  = pick(["solution", "sop"]) or None

rows = []
for i, r in cases_df.iterrows():
    rid   = clean(r.get(id_col) or f"CASE-{i:04d}")
    parts = []
    for c in [sum_col, root_col, res_col]:
        if c and c in r:
            parts.append(r[c])
    text  = clean(" | ".join([clean(p) for p in parts if p]))
    if len(text) >= 40:
        rows.append({"id": rid, "text": text})

pd.DataFrame(rows).to_csv(PREP / "cases.csv", index=False)

# ---- Process Knowledge Base (DOCX) ----
kbdoc = Document(RAW / "Knowledge Base.docx")
chunks, buf = [], []

def flush():
    global buf
    if buf:
        paragraph = clean(" ".join(buf))
        if len(paragraph) >= 40:
            chunks.append(paragraph)
        buf = []

for p in kbdoc.paragraphs:
    t = clean(p.text)
    if not t:
        flush()
    else:
        buf.append(t)
flush()

pd.DataFrame([{"id": f"KB-{i:04d}", "text": t} for i, t in enumerate(chunks)]).to_csv(PREP / "knowledge.csv", index=False)
print("✅ Wrote:", (PREP / "cases.csv").as_posix(), (PREP / "knowledge.csv").as_posix())
