from flask import Flask, request, jsonify
from flask_cors import CORS
import requests
import xml.etree.ElementTree as ET
import json
import io
import re

app = Flask(__name__)
CORS(app)

GROQ_URL  = "https://api.groq.com/openai/v1/chat/completions"
ARXIV_URL = "https://export.arxiv.org/api/query"

def groq_call(api_key, messages, max_tokens=1800, temperature=0.7):
    resp = requests.post(
        GROQ_URL,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {api_key}"},
        json={"model": "llama-3.3-70b-versatile", "max_tokens": max_tokens,
              "temperature": temperature, "messages": messages},
        timeout=60
    )
    if not resp.ok:
        err = resp.json().get("error", {})
        if resp.status_code == 401: raise ValueError("Invalid Groq API key. Check console.groq.com")
        if resp.status_code == 429: raise ValueError("Groq rate limit. Wait 30 seconds and try again.")
        raise ValueError(err.get("message", f"Groq error {resp.status_code}"))
    return resp.json()["choices"][0]["message"]["content"]


# ── ArXiv paper search ──────────────────────────────────────────────
@app.route("/search", methods=["GET"])
def search_papers():
    topic  = request.args.get("topic", "")
    domain = request.args.get("domain", "")
    max_r  = request.args.get("max", "8")
    query  = f"all:{topic}"
    if domain:
        query += f"+AND+cat:{domain}"
    params = {"search_query": query, "start": 0, "max_results": int(max_r),
              "sortBy": "relevance", "sortOrder": "descending"}
    resp = requests.get(ARXIV_URL, params=params, timeout=15)
    if not resp.ok:
        return jsonify({"error": "ArXiv fetch failed"}), 500
    root = ET.fromstring(resp.text)
    ns   = {"atom": "http://www.w3.org/2005/Atom"}
    papers = []
    for i, entry in enumerate(root.findall("atom:entry", ns)):
        title    = (entry.findtext("atom:title",    "", ns) or "").strip().replace("\n", " ")
        summary  = (entry.findtext("atom:summary",  "", ns) or "").strip().replace("\n", " ")
        pub      = (entry.findtext("atom:published","", ns) or "")[:4]
        url      = (entry.findtext("atom:id",       "", ns) or "").strip()
        authors  = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)][:3]
        arxiv_id = url.split("/abs/")[-1] if "/abs/" in url else ""
        papers.append({"id": i+1, "title": title, "authors": authors,
                       "abstract": summary[:600], "year": pub, "url": url, "arxivId": arxiv_id})
    return jsonify(papers)


# ── Fetch single ArXiv paper by ID ──────────────────────────────────
@app.route("/fetch_arxiv", methods=["GET"])
def fetch_arxiv():
    arxiv_id = request.args.get("id", "").strip()
    if not arxiv_id:
        return jsonify({"error": "No ArXiv ID provided"}), 400
    url = f"https://export.arxiv.org/api/query?id_list={arxiv_id}"
    resp = requests.get(url, timeout=15)
    if not resp.ok:
        return jsonify({"error": "Failed to reach ArXiv"}), 500
    root  = ET.fromstring(resp.text)
    ns    = {"atom": "http://www.w3.org/2005/Atom"}
    entry = root.find("atom:entry", ns)
    if entry is None:
        return jsonify({"error": f"No paper found for ID: {arxiv_id}"}), 404
    title     = (entry.findtext("atom:title",    "", ns) or "").strip().replace("\n", " ")
    summary   = (entry.findtext("atom:summary",  "", ns) or "").strip().replace("\n", " ")
    pub       = (entry.findtext("atom:published","", ns) or "")[:4]
    paper_url = (entry.findtext("atom:id",       "", ns) or "").strip()
    authors   = [a.findtext("atom:name", "", ns) for a in entry.findall("atom:author", ns)][:5]
    return jsonify({"id": 0, "title": title, "authors": authors,
                    "abstract": summary[:800], "year": pub, "url": paper_url, "arxivId": arxiv_id})


# ── Upload & parse PDF ──────────────────────────────────────────────
@app.route("/upload_pdf", methods=["POST"])
def upload_pdf():
    if "pdf" not in request.files:
        return jsonify({"error": "No PDF file uploaded"}), 400

    pdf_file = request.files["pdf"]
    if not pdf_file.filename.lower().endswith(".pdf"):
        return jsonify({"error": "File must be a .pdf"}), 400

    try:
        import pypdf
    except ImportError:
        try:
            import PyPDF2 as pypdf
        except ImportError:
            return jsonify({"error": "PDF library not installed. Run: pip install pypdf"}), 500

    try:
        pdf_bytes = pdf_file.read()
        reader    = pypdf.PdfReader(io.BytesIO(pdf_bytes))

        # Extract all text from PDF
        full_text = ""
        for page in reader.pages[:20]:          # cap at 20 pages
            full_text += (page.extract_text() or "") + "\n"

        full_text = re.sub(r'\s+', ' ', full_text).strip()

        if len(full_text) < 100:
            return jsonify({"error": "Could not extract text from this PDF. It may be scanned/image-based."}), 422

        # Heuristic extraction — first 3000 chars usually has title/authors/abstract
        head = full_text[:3000]

        # Try to extract title: usually the longest line in first 300 chars
        first_block = full_text[:400].split('\n')
        title_guess = max(first_block, key=len).strip() if first_block else "Untitled"
        title_guess = title_guess[:200]

        # Abstract: text between "abstract" and "introduction" keywords
        abstract_match = re.search(
            r'(?i)abstract[:\s]+(.*?)(?=\n\s*\n|\bintroduction\b|\b1\.\s)',
            head, re.DOTALL
        )
        abstract_text = ""
        if abstract_match:
            abstract_text = re.sub(r'\s+', ' ', abstract_match.group(1)).strip()[:800]

        # Fallback: use first 600 chars of body as abstract
        if not abstract_text or len(abstract_text) < 80:
            abstract_text = full_text[len(title_guess):len(title_guess)+600].strip()

        # Year: find 4-digit year between 2000-2030
        year_match = re.search(r'\b(20[0-2]\d)\b', head)
        year = year_match.group(1) if year_match else ""

        # Body text for AI to use (capped at 4000 chars)
        body_for_ai = full_text[:4000]

        return jsonify({
            "id":        0,
            "title":     title_guess,
            "authors":   [],
            "abstract":  abstract_text,
            "year":      year,
            "url":       "",
            "arxivId":   "",
            "full_text": body_for_ai,
            "filename":  pdf_file.filename
        })

    except Exception as e:
        return jsonify({"error": f"PDF parsing failed: {str(e)}"}), 500


# ── Literature review generation ────────────────────────────────────
@app.route("/generate", methods=["POST"])
def generate_review():
    body    = request.get_json()
    api_key = body.get("api_key", "")
    papers  = body.get("papers", [])
    topic   = body.get("topic", "")
    style   = body.get("style", "comprehensive")
    if not api_key or not papers or not topic:
        return jsonify({"error": "Missing api_key, papers, or topic"}), 400

    style_guide = {
        "comprehensive": "Write a comprehensive review covering all major themes, methodologies, and findings.",
        "thematic":      "Organize thematically, grouping papers by their core contributions.",
        "chronological": "Organize chronologically to show how research has evolved over time.",
        "gap-focused":   "Focus on identifying research gaps, open problems, and future directions."
    }.get(style, "")

    papers_text = "\n\n".join([
        f'[{p["id"]}] "{p["title"]}" — {", ".join(p["authors"])} ({p["year"]})\nAbstract: {p.get("full_text", p["abstract"])[:500]}'
        for p in papers
    ])

    prompt = f"""You are an expert academic researcher. Write a formal literature review on: "{topic}"
{style_guide}
Papers (use [N] citation format):
{papers_text}
Structure with these exact sections:
## Introduction
## Main Themes and Findings
## Methodologies and Approaches
## Research Gaps and Future Directions
## Conclusion
Write in formal academic paragraphs (no bullet points). Be specific, cite papers by number, aim for 700-900 words."""

    try:
        text = groq_call(api_key, [
            {"role": "system", "content": "You are an expert academic researcher who writes precise, well-structured literature reviews."},
            {"role": "user",   "content": prompt}
        ])
        return jsonify({"review": text})
    except ValueError as e:
        return jsonify({"error": str(e)}), 500


# ── Methodology comparison table ────────────────────────────────────
@app.route("/compare", methods=["POST"])
def compare_papers():
    body    = request.get_json()
    api_key = body.get("api_key", "")
    papers  = body.get("papers", [])
    topic   = body.get("topic", "")
    if not api_key or not papers or not topic:
        return jsonify({"error": "Missing api_key, papers, or topic"}), 400

    papers_text = "\n\n".join([
        f'[{p["id"]}] "{p["title"]}" — {", ".join(p["authors"])} ({p["year"]})\nAbstract: {p["abstract"]}'
        for p in papers
    ])

    prompt = f"""You are an expert academic researcher. Analyze these {len(papers)} papers on "{topic}".

Papers:
{papers_text}

Return ONLY a valid JSON object (no markdown, no explanation, no code fences) in this exact format:
{{"columns":["Paper","Year","Method/Model","Dataset","Key Metric","Result","Limitation"],"rows":[{{"Paper":"Short title [1]","Year":"2023","Method/Model":"CNN+Transformer","Dataset":"FaceForensics++","Key Metric":"Accuracy","Result":"97.2%","Limitation":"High compute cost"}}]}}

Fill all {len(papers)} papers as rows. If a field is not mentioned, write "N/A". Keep each cell under 8 words. Return raw JSON only."""

    try:
        raw = groq_call(api_key, [
            {"role": "system", "content": "You are a precise academic data extractor. Return valid JSON only, no extra text, no markdown."},
            {"role": "user",   "content": prompt}
        ], max_tokens=2000, temperature=0.2)

        raw = raw.strip()
        if raw.startswith("```"):
            raw = raw.split("```")[1]
            if raw.startswith("json"): raw = raw[4:]
        raw = raw.strip()
        table = json.loads(raw)
        return jsonify(table)
    except ValueError as e:
        return jsonify({"error": str(e)}), 500
    except Exception:
        return jsonify({"error": "Failed to parse comparison table. Please try again."}), 500


if __name__ == "__main__":
    print("\n✅ LitReview AI server running!")
    print("   Open index.html in your browser\n")
    app.run(port=5000, debug=False)
