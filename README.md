# 📚 AI-Based Automated Literature Review Generation System

> Automatically search research papers, generate structured literature reviews, and export formatted PDFs — all powered by free AI. Built with Python, Flask, and Llama 3.3-70B.

---

## 🚀 What Does This Project Do?

This is a full-stack web application that automates the complete academic literature review process.

You just type a research topic → the system searches ArXiv for relevant papers → AI reads and analyzes them → generates a complete, structured, well-cited literature review in under 60 seconds.

No paid subscriptions. No installations except Python. Completely free.

---

## ✨ Key Features

- 🔍 **Live Paper Search** — Searches ArXiv database in real time (2M+ papers)
- 🤖 **AI Review Generation** — Uses Groq API + Llama 3.3-70B to write structured reviews
- 📄 **Add Your Own Papers** — Via ArXiv URL, manual entry, or PDF upload
- 📊 **Methodology Comparison Table** — Auto-extracts Method, Dataset, Metric, Result, Limitation
- 🎨 **4 Review Styles** — Comprehensive, Thematic, Chronological, Gap-Focused
- 📥 **Export Options** — Download as formatted PDF or plain text file
- 🔒 **100% Free** — ArXiv API (free) + Groq API (free tier)

---

## 🛠️ Tech Stack

| Layer | Technology |
|---|---|
| Backend | Python 3.8+, Flask, Flask-CORS |
| Frontend | HTML5, CSS3, JavaScript (ES6+) |
| PDF Processing | pypdf |
| Paper Database | ArXiv Open API |
| AI Model | Groq API — Llama 3.3-70B |
| PDF Export | jsPDF + AutoTable (browser-side) |

---

## ⚙️ Installation & Setup

### Step 1 — Clone the Repository

```bash
git clone https://github.com/s-hivamthakur/LitReview.git
cd LitReview
```

### Step 2 — Install Python Dependencies

```bash
pip install flask flask-cors requests pypdf
```

Or using the requirements file:

```bash
pip install -r requirements.txt
```

### Step 3 — Get Your FREE Groq API Key ⚡

> **This is required to run the AI review generation.**

1. Go to **[https://console.groq.com](https://console.groq.com)**
2. Click **Sign Up** — it's completely free, no credit card needed
3. After signing in, click **API Keys** in the left sidebar
4. Click **Create API Key**
5. Give it any name (e.g. `litreview-key`)
6. Copy the key — it starts with `gsk_...`
7. **Keep it safe** — you will paste it into the app when you use it

> ⚠️ **Important:** Never share your API key publicly or push it to GitHub.

### Step 4 — Run the Flask Server

```bash
python server.py
```

You should see:
```
✅ LitReview AI server running on http://localhost:5000
```

> Keep this terminal window open while using the app.

### Step 5 — Open the App

Open `index.html` in your browser (double-click the file or drag it into Chrome/Firefox).

> Do NOT open it as a URL — just open the HTML file directly.

### Step 6 — Start Generating Reviews!

1. Paste your **Groq API Key** (from Step 3) into the API Key field
2. Type your **research topic** (e.g. `deepfake detection using deep learning`)
3. Select domain filter and number of papers
4. Click **Generate Literature Review**
5. Wait ~30–60 seconds and your review is ready!
6. Download as **PDF** or **TXT**

---

## 📁 Project Structure

```
litreview-ai/
│
├── server.py          # Flask backend — handles all API calls
├── index.html         # Frontend UI — single-page web app
├── requirements.txt   # Python dependencies
└── README.md          # You are here
```

---

## 🔌 API Endpoints (server.py)

| Endpoint | Method | Description |
|---|---|---|
| `/search` | GET | Search ArXiv for papers by topic |
| `/fetch_arxiv` | GET | Fetch single paper by ArXiv ID or URL |
| `/upload_pdf` | POST | Extract text and metadata from PDF |
| `/generate` | POST | Generate full literature review using AI |
| `/compare` | POST | Generate methodology comparison table |

---

## 📖 How to Use — Step by Step

### Basic Search and Review
1. Enter your Groq API key in the top field
2. Type your research topic in the search box
3. Select domain (optional) and number of papers (5/8/12/15)
4. Select review style (Comprehensive / Thematic / Chronological / Gap-Focused)
5. Click **Generate Literature Review**

### Adding Your Own Papers
Three ways to add papers not found in ArXiv:

**Option A — ArXiv URL:**
- Click "Add Your Own Papers"
- Paste the ArXiv URL (e.g. `https://arxiv.org/abs/2301.12345`)
- Click Fetch — metadata auto-fills

**Option B — Manual Entry:**
- Fill in Title, Authors, Year, Abstract manually
- Click Add Paper

**Option C — PDF Upload:**
- Drag and drop a PDF file
- System auto-extracts title, abstract, year
- Review and confirm before adding

### Exporting
- **Export PDF** — Downloads a formatted A4 PDF with review sections, comparison table, and references
- **Export TXT** — Downloads plain text version for pasting into Word/LaTeX

---

## 🧠 How It Works (Architecture)

```
Browser (index.html)
       ↕  HTTP (localhost:5000)
Flask Server (server.py)
       ↕                    ↕
  ArXiv API            Groq API
  (paper search)       (Llama 3.3-70B)
                            ↑
                       pypdf (PDF upload)
```

**Why Flask?** Browsers block direct API calls to external services (CORS policy). Flask runs locally and acts as a middleman — browser talks to Flask, Flask talks to ArXiv and Groq.

---

## 📋 Requirements

```
flask
flask-cors
requests
pypdf
```

Minimum Python version: **3.8+**

---

## ❓ Frequently Asked Questions

**Q: Is this really free?**
Yes. ArXiv API is free with no key needed. Groq API is free with generous rate limits for personal use.

**Q: Where do I get the Groq API key?**
Go to [https://console.groq.com](https://console.groq.com), sign up free, and generate a key under API Keys section. The key starts with `gsk_`.

**Q: The server won't start — what do I do?**
Make sure you ran `pip install flask flask-cors requests pypdf` first. Also ensure port 5000 is not used by another app.

**Q: I see "Failed to fetch" in the browser.**
This means the Flask server is not running. Open a terminal, go to the project folder, and run `python server.py`.

**Q: Can I use papers from IEEE or Springer?**
Yes — use the PDF Upload feature to upload papers from any source as PDF files.

**Q: How many papers can I add?**
ArXiv search supports up to 15 papers. You can add unlimited custom papers via URL/manual/PDF.

**Q: Is my API key stored anywhere?**
No. The API key is only used for the current session and never saved anywhere.

---

## 🔮 Future Work

- [ ] Add support for IEEE Xplore, PubMed, and Scopus databases
- [ ] Implement semantic (meaning-based) search using SPECTER/SciBERT
- [ ] Add real-time paper monitoring and alerts
- [ ] Support LaTeX and BibTeX export formats
- [ ] Add user accounts to save past reviews

---

## ⭐ If this project helped you, give it a star on GitHub!
