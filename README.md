# 🧠 PSA-reliAI — Hackathon Code Sprint

**Team Project:** AI-powered Reliability Assistant for PSA Systems

---

## 🚀 Overview
This project integrates **Retrieval-Augmented Generation (RAG)**, **FastAPI backend**, **Streamlit frontend**, and **Database logging** to provide intelligent support for PSA operations.

It enables:
- Searching through case logs and knowledge base using embeddings (FAISS)
- Intelligent chatbot responses with contextual retrieval
- Escalation logging & status tracking
- Frontend UI for interactions

---

## 🏗️ Project Structure
ai/ → Embeddings, RAG, retrieval logic
app/ → FastAPI backend routes
frontend/ → Streamlit UI
database/ → Models & DB connection setup
data/ → Raw, prepared, and embeddings data
scripts/ → Data preprocessing & embeddings prep
tests/ → Unit tests


---

## ⚙️ Setup Instructions
1️⃣ Clone the Repo
```bash
git clone https://github.com/hetavi4/psa-reliAI.git
cd psa-reliAI

2️⃣ Create and Activate a Virtual Environment
python3 -m venv .venv
source .venv/bin/activate       # Mac/Linux
# OR
.venv\Scripts\activate          # Windows

3️⃣ Install Dependencies
pip install -r requirements.txt

📊 Data Preparation

Place the raw input files (these are not committed to GitHub for privacy):

data/raw/Case Log.xlsx
data/raw/Knowledge Base.docx


Then run the preprocessing and embedding generation scripts:

# Step 1: Prepare data
python scripts/prepare_embeddings.py

# Step 2: Build FAISS embedding indexes
python ai/build_indexes.py


This will automatically generate:

data/prepared/cases.csv
data/prepared/knowledge.csv
data/embeddings/*.npy
data/embeddings/*.index

🔧 Running the Application
▶️ Start Backend (FastAPI)
uvicorn app.main:app --reload


This launches the API at:
👉 http://127.0.0.1:8000

Example routes:

/search → Retrieve similar cases or knowledge base answers

/cases → Fetch stored case metadata

💻 Start Frontend (Streamlit)
streamlit run frontend/app.py


The frontend provides:

A user view to raise and track queries

A resolver view showing similar past cases + solution steps

Insights / foresight section for trend prediction

🧩 Tech Stack
Layer	Technology
Backend	FastAPI
Frontend	Streamlit
AI / RAG	Sentence Transformers (all-MiniLM-L6-v2), FAISS
Database	SQLite / PostgreSQL
Language	Python
Data Handling	Pandas, regex, openpyxl
Environment	virtualenv
👥 Team Roles
Member	Responsibility
Hetavi Shah	RAG pipeline, embeddings, retrieval, integration
Teammate 2	API & FastAPI backend logic
Teammate 3	Streamlit frontend (UI/UX)
Teammate 4	Database schema, escalation logic, connection handling
🧠 Future Enhancements

Integrate real-time escalation predictions

Improve semantic similarity scoring

Add role-based authentication (Admin, Resolver, User)

Enable API call monitoring and analytics

🪄 Quick Commands Reference
Task	Command
Activate environment	source .venv/bin/activate
Install dependencies	pip install -r requirements.txt
Prepare embeddings	python scripts/prepare_embeddings.py
Build FAISS index	python ai/build_indexes.py
Run backend	uvicorn app.main:app --reload
Run frontend	streamlit run frontend/app.py
