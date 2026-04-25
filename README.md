# ⚖️ NyayaSetu — AI-Powered Court Judgment to Action Plan System

> **AI for Bharat Hackathon 2026 · Theme 11 · PAN IIT Bangalore Summit**  
> Built for the Centre for e-Governance, Government of Karnataka

---

## 🧩 The Problem

Karnataka's Court Case Monitoring System (CCMS) receives hundreds of High Court judgment PDFs every day. Each judgment contains critical government directives — comply, appeal, assign departments, meet deadlines — buried inside 20–100 pages of complex legal text.

**Today, IAS officers manually read every page.** This causes:
- ⏰ Delays in compliance — missed court deadlines
- ❌ Inconsistent interpretation across departments  
- 📋 No unified tracking of pending government actions
- ⚠️ Risk of contempt of court for missed directives

---

## 💡 The Solution

**NyayaSetu** (meaning *Justice Bridge* in Sanskrit) is an AI system that:

1. **Reads** court judgment PDFs (digital or scanned)
2. **Extracts** case details, directives, parties, and deadlines using Gemini AI
3. **Generates** a structured action plan — Comply / Consider Appeal / Monitor
4. **Verifies** every AI decision through a human-in-the-loop review by the officer
5. **Displays** only approved actions in a department-wise dashboard

> *"If it can't work in the real world, it doesn't win here."* — AI for Bharat 2026

---

## 🖥️ Demo

🔗 **Live App:** [nyayasetu.streamlit.app](https://nyayasetu.streamlit.app)

### Screenshots

| Upload & Analyse | Review & Verify | Dashboard |
|---|---|---|
| Upload PDF → AI analyses in 20s | Officer reviews each field with confidence scores | Verified actions by department & priority |

---

## ⚙️ How It Works

```
Court Judgment PDF
       │
       ▼
┌─────────────────┐
│  PDF Text       │  ← PyMuPDF extracts all text page by page
│  Extraction     │
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini AI      │  ← Call 1: Extract case details + confidence scores
│  Case Details   │     Case no, judge, parties, directives, deadlines
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Gemini AI      │  ← Call 2: Generate structured action plan
│  Action Plan    │     Action type, department, deadline, priority
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Human Review   │  ← Officer approves / edits / rejects each item
│  (Mandatory)    │     Nothing moves forward without human sign-off
└────────┬────────┘
         │
         ▼
┌─────────────────┐
│  Dashboard      │  ← Department-wise verified action tracker
│  + CSV Export   │     Filter by priority, export for records
└─────────────────┘
```

---

## 🏗️ Tech Stack

| Layer | Technology | Why |
|---|---|---|
| Frontend / UI | Streamlit | Rapid prototyping, Python-native |
| AI / LLM | Google Gemini 2.5 Flash | Best-in-class document understanding |
| PDF Parsing | PyMuPDF (fitz) | Fast, handles digital + scanned PDFs |
| Database | SQLite | Zero-setup, file-based, portable |
| Environment | python-dotenv | Secure API key management |
| Deployment | Streamlit Cloud | Free, one-click deploy from GitHub |

---

## 📁 Project Structure

```
nyayasetu/
├── app.py              ← Main Streamlit web application (3 pages)
├── extractor.py        ← PDF parsing + Gemini AI logic
├── database.py         ← SQLite database handler
├── requirements.txt    ← Python dependencies
├── .env                ← API keys (never committed)
├── .gitignore          ← Excludes .env and uploads/
└── uploads/            ← Temporary PDF storage
```

---

## 🚀 Run Locally

### Prerequisites
- Python 3.10+
- A Google Gemini API key (free at [aistudio.google.com](https://aistudio.google.com))

### Setup

```bash
# 1. Clone the repository
git clone https://github.com/YOUR_USERNAME/nyayasetu.git
cd nyayasetu

# 2. Install dependencies
pip install -r requirements.txt

# 3. Create your .env file
echo GEMINI_API_KEY=your_key_here > .env

# 4. Run the app
streamlit run app.py
```

The app opens at `http://localhost:8501`

---

## 📊 Evaluation Criteria Alignment

| Criteria | Weight | How NyayaSetu addresses it |
|---|---|---|
| Problem Relevance & Depth | 20% | Directly solves CCMS PDF processing bottleneck for Karnataka e-Governance |
| Technical Implementation | 25% | LLM-based extraction, confidence scoring, SQLite persistence, modular codebase |
| Real-World Deployability | 25% | Works as add-on to existing CCMS — no source system changes, runs on synthetic data |
| Demo Quality | 15% | Live Streamlit app with working PDF upload, AI analysis, and dashboard |
| Scalability & Impact | 15% | Scales to all 30 Karnataka districts, 50,000+ judgments/year, exportable CSV |

---

## 🔑 Key Design Decisions

**Why human-in-the-loop is mandatory?**  
Every AI extraction has a confidence score (🟢 High / 🟡 Medium / 🔴 Low). Officers must approve or edit each item before it reaches the dashboard. A wrong AI decision is never silently committed — this directly mirrors the hackathon's "explainable and reversible" requirement.

**Why two separate AI calls?**  
One focused prompt yields better results than one giant prompt. Call 1 is about *understanding* the judgment. Call 2 is about *deciding* what government must do. Separation also makes each step independently auditable.

**Why SQLite?**  
Zero infrastructure — runs on any government laptop without database servers. For production deployment, the same schema can be migrated to PostgreSQL with minimal changes.

---

## 🗺️ Roadmap (Post-Hackathon)

- [ ] CCMS API integration — auto-fetch new judgment PDFs as they arrive
- [ ] WhatsApp / email alerts for high-priority action deadlines
- [ ] Scanned PDF OCR support via Google Document AI
- [ ] Multi-language support (Kannada judgments)
- [ ] Role-based access — separate views for Legal, BBMP, Urban Development
- [ ] Deadline reminder engine with escalation workflows

---

## 👥 Team

Built at **AI for Bharat 2026** · PAN IIT Bangalore Alumni Association × Government of Karnataka

---

## 📄 License

MIT License — built for public good, open for government use.
