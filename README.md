# 🧠 PSA-reliAI — Hackathon Code Sprint 2025

**Team Project:** AI-Powered Reliability Assistant for PSA Systems  
**Goal:** Empower duty officers with intelligent incident management, faster resolutions, and predictive insights using AI.

---

## 🚀 Overview

**PSA-reliAI** integrates **Retrieval-Augmented Generation (RAG)**, a **FastAPI backend**, **Streamlit frontend**, and **Database logging** to create a smart assistant for PSA’s operational reliability.

The system enables:
- 🔍 **Semantic search** through case logs and knowledge base using embeddings (FAISS)
- 🤖 **AI-assisted recommendations** and contextual retrieval
- ⚙️ **Incident escalation tracking** and resolution workflow management
- 🧭 **Predictive foresight** for identifying potential future issues

---

## 🏗️ Project Structure

ai/ → Embeddings, RAG, retrieval logic
app/ → FastAPI backend routes and controllers
frontend/ → Streamlit user interface
database/ → Models, DB schema, and connection setup
data/
├── raw/ → Original data files (e.g., Case Log.xlsx, Knowledge Base.docx)
├── prepared/ → Cleaned CSVs for embeddings
└── embeddings/ → FAISS indexes and numpy embedding arrays
scripts/ → Data preprocessing scripts
tests/ → Unit and integration tests

yaml
Copy code

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the Repository
```bash
git clone https://github.com/hetavi4/psa-reliAI.git
cd psa-reliAI
2️⃣ Create and Activate a Virtual Environment
bash
Copy code
python3 -m venv .venv
source .venv/bin/activate       # Mac/Linux
# OR
.venv\Scripts\activate          # Windows
3️⃣ Install Dependencies
bash
Copy code
pip install -r requirements.txt
📊 Data Preparation
The data files are already included in the repo under data/raw/, but if re-running or updating embeddings:

bash
Copy code
# Step 1: Prepare data
python scripts/prepare_embeddings.py

# Step 2: Build FAISS embedding indexes
python ai/build_indexes.py
These commands will generate:

bash
Copy code
data/prepared/cases.csv
data/prepared/knowledge.csv
data/embeddings/*.npy
data/embeddings/*.index
🔧 Running the Application
▶️ Backend (FastAPI)
bash
Copy code
uvicorn app.main:app --reload
Access the backend here:
👉 http://127.0.0.1:8000

Example routes:

/search — Retrieve similar cases or knowledge base insights

/cases — Fetch stored case metadata

💻 Frontend (Streamlit)
bash
Copy code
streamlit run frontend/app.py
Features include:

User dashboard to raise and track incidents

Resolver panel showing related cases and recommended actions

Foresight section for predicted patterns or risks

🧩 Tech Stack
Layer	Technology
Backend	FastAPI
Frontend	Streamlit
AI / RAG	Sentence Transformers (all-MiniLM-L6-v2), FAISS
Database	SQLite / PostgreSQL
Language	Python
Data Handling	Pandas, regex, openpyxl
Environment	virtualenv

🧠 Future Enhancements
Integrate real-time escalation predictions

Improve semantic similarity scoring

Add role-based authentication (Admin, Resolver, User)

Implement API analytics and monitoring

Visualize incident trends using Streamlit charts

🪄 Quick Commands Reference
Task	Command
Activate environment	source .venv/bin/activate
Install dependencies	pip install -r requirements.txt
Prepare embeddings	python scripts/prepare_embeddings.py
Build FAISS index	python ai/build_indexes.py
Run backend	uvicorn app.main:app --reload
Run frontend	streamlit run frontend/app.py

