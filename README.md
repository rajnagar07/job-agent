# 🤖 AI Job Agent

An AI-powered Job Aggregator and Career Assistant that automatically collects software engineering jobs, intelligently matches resumes using Google Gemini, and recommends the best opportunities through AI-powered analysis.

---

## 🚀 Features

### 🔍 Job Aggregation
- RemoteOK Integration
- Wellfound Integration
- Greenhouse Integration
- Multi-source Job Collection
- Duplicate Detection
- Hybrid Job Filtering
- Job Lifecycle Management
- Automatic Job Refresh
- Scheduler Support

### 🤖 AI Resume Intelligence
- Resume Upload (PDF)
- Resume Parsing (PyMuPDF)
- Skill Extraction
- Resume vs Job Matching
- Google Gemini Integration
- LangChain Integration
- AI Match Score
- Matched Skills
- Missing Skills
- Resume Summary
- Job Summary
- AI Hiring Verdict
- Personalized Recommendations
- Rule-Based Fallback

### 🔐 Authentication
- Signup
- Login
- Logout
- Email Verification
- Forgot Password
- Reset Password
- Protected AI Features
- Public Landing Page
- Redirect After Login

### 📊 Dashboard
- Job Search
- Job Details
- Resume Analysis
- AI Recommendations
- Recommendation Engine
- Dashboard Statistics

---

# 🏗 Architecture

```text
Job Sources
      │
      ▼
Job Scrapers
      │
      ▼
Hybrid Job Filter
      │
      ▼
SQLite Database
      │
      ▼
Recommendation Engine
      │
      ▼
Google Gemini
      │
      ▼
Flask Dashboard
```

---

# 🔄 Recommendation Workflow

```text
Resume Upload
      │
      ▼
Extract Resume Text
      │
      ▼
Extract Skills
      │
      ▼
Compare with ALL Active Jobs
      │
      ▼
Fast Rule-Based Matching
      │
      ▼
Rank Jobs
      │
      ▼
Top Recommendations
      │
      ▼
Gemini Deep Analysis
      │
      ▼
Display AI Report
```

---

# 📁 Project Structure

```text
AI-Job-Agent/
│
├── ai/
├── auth/
├── dashboard/
├── database/
├── jobs/
├── services/
├── static/
├── templates/
├── uploads/
├── config.py
├── app.py
└── requirements.txt
```

---

# 🛠 Tech Stack

### Backend
- Python
- Flask
- SQLAlchemy

### AI
- Google Gemini
- LangChain
- Prompt Engineering

### Database
- SQLite

### Resume Processing
- PyMuPDF

### Web Scraping
- BeautifulSoup
- Requests
- lxml

### Frontend
- HTML
- CSS
- Bootstrap 5
- Jinja2

### Utilities
- APScheduler
- python-dotenv
- Regex

---

# ⚙️ Installation

```bash
git clone https://github.com/<your-username>/AI-Job-Agent.git

cd AI-Job-Agent

python -m venv venv

# Windows
venv\Scripts\activate

# Linux/macOS
source venv/bin/activate

pip install -r requirements.txt
```

Create a `.env`

```env
GOOGLE_API_KEY=your_key
FLASK_SECRET_KEY=your_secret
EMAIL=your_email
EMAIL_PASSWORD=your_password
```

Collect jobs

```bash
python app.py
```

Run dashboard

```bash
python -m dashboard.app
```

Open

```
http://127.0.0.1:5000
```

---

# ✅ Current Features

- Multi-source Job Aggregation
- AI Resume Matching
- Hybrid Job Filtering
- Recommendation Engine
- Authentication System
- Email Verification
- Forgot Password
- Job Lifecycle
- Automatic Refresh
- Dashboard
- Scheduler

---

# 🚀 Upcoming Features

- Saved Resume
- Saved Jobs
- Recommendation History
- ATS Resume Score
- AI Cover Letter
- Interview Questions
- Daily Email Alerts
- WhatsApp Notifications
- PostgreSQL
- Docker
- ChromaDB
- Semantic Search
- Career Chatbot

---

# 👨‍💻 Author

**Raj Nagar**

MCA Student | Python Backend Developer | GenAI Enthusiast

---

⭐ If you found this project useful, consider giving it a star on GitHub.