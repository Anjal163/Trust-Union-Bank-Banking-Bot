# 🏦 Trust Union Bank – AI Banking Chatbot

A **secure, sessionless, Rasa-driven banking chatbot** built using **FastAPI + Rasa + PostgreSQL**, designed with real-world backend and security practices.

This repository intentionally **does not include secrets or trained ML models**.  
All sensitive or generated artifacts are created **locally by each developer**.

---

## 🚀 Key Highlights

- 🤖 Rasa-powered conversational AI
- ⚡ FastAPI backend
- 🔐 OTP + MPIN authentication flows
- 🧠 Sentiment-aware chat handling
- 🏦 Banking capabilities (accounts, balance, branches, loans, cards)
- 🧩 Stateless, sessionless design
- 🛡️ Secure Git practices (no secrets or models in repo)
- ▶️ Rasa auto-starts with backend (no separate command)

---

## 📦 Prerequisites

Install the following before starting:

- **Python 3.9 – 3.11**
- **pip**
- **Git**
- **PostgreSQL** (or Supabase)
- **Rasa**

Verify installation:
```bash
python --version
pip --version
rasa --version


📁 Clone the Repository
git clone https://github.com/Arkadeep01/TrustUnionBank.git
cd TrustUnionBank


🐍 Virtual Environment (Recommended)
Windows
python -m venv venv
venv\Scripts\activate

Linux / macOS
python3 -m venv venv
source venv/bin/activate



🔐 Environment Configuration
Create .env file

A template file .env.example is provided.

cp .env.example .env


🗄️ Database Setup

Create a PostgreSQL database

Execute the SQL files in this order:

schema.sql
schema_indexes.sql


schema_migrations.sql is optional and used only for future upgrades.


🤖 Train the Rasa Model (REQUIRED)

Rasa models are not stored in GitHub by design.

Train the model locally:

cd rasa
rasa train
This generates trained models locally, which Rasa will load at runtime.

▶️ Run the Application

From the project root:

python api_server.py


🌐 Verify the Setup
Health Check
GET http://localhost:8000/api/health

{ "status": "ok" }

Why trained Rasa models are not in GitHub

They are generated artifacts

They are environment-specific

They can be recreated anytime

Always run:

rasa train


🛠️ Common Issues
Rasa does not start
pip install rasa
rasa --version

✅ Developer Checklist

 Python installed

 Virtual environment activated

 Dependencies installed

 .env configured

 Database schema applied

 Rasa model trained

 python api_server.py running

 /api/health returns OK


 