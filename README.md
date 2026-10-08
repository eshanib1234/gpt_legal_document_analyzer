# College Laboratory Experiment 5: Automated Legal Document Analyzer using Ollama

An automated, on-premise Legal Document Analysis system built with **FastAPI**, **React.js**, and a local **Ollama** LLM running **Llama 3.2**.

> **Note for Lab Evaluation**: This experiment replaces OpenAI/GPT-4 with local Ollama (`llama3.2:latest`). It runs 100% locally with zero cloud API keys, zero external network dependency, and complete data privacy.

---

## 🏗️ System Architecture & Workflow

```
   +-----------------------------------------------------------+
   |                     Legal Document                        |
   |              (Raw Text / .txt File Upload)                |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |                  Document Preprocessing                   |
   |          (Normalize whitespace, clean linebreaks)         |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |              Section / Chunk Identification               |
   |    (Single pass if <=3000 chars, or smart paragraph-split)|
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |                     Prompt Generation                     |
   |     (Strict JSON schema, legal role, no hallucinations)   |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |                     Ollama Local LLM                      |
   |               Endpoint: localhost:11434                   |
   |                 Model: llama3.2:latest                    |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |                Legal Information Extraction               |
   |   - Document Type         - Parties Involved              |
   |   - Document Purpose      - Obligations & Duties          |
   |   - Rights & Entitlements - Payment Terms                 |
   |   - Duration / Term       - Termination Conditions        |
   |   - Confidentiality       - Important Dates               |
   |   - Governing Law         - Key Clauses                   |
   |   - Risk Clauses          - Executive Summary             |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |                  Structured JSON Output                   |
   |                (Merged & Deduplicated)                    |
   +-----------------------------+-----------------------------+
                                 |
                                 v
   +-----------------------------------------------------------+
   |                     React Frontend UI                     |
   |   (Interactive 14-Card Grid, Raw JSON Viewer, Lab Report) |
   +-----------------------------------------------------------+
```

---

## 🛠️ Technology Stack

| Layer | Technology | Purpose |
|---|---|---|
| **Frontend** | React 18, Vite, Vanilla CSS, Lucide Icons | Responsive student lab interface |
| **Backend** | Python 3.11+, FastAPI, Uvicorn, Pydantic | REST API, preprocessing, schema enforcement |
| **LLM Inference** | Ollama (`llama3.2:latest`) | Local deterministic JSON extraction |
| **Communication** | HTTP REST (Zero paid APIs, Zero OpenAI keys) | Local IPC (`:5173` -> `:8000` -> `:11434`) |

---

## 📁 Project Structure

```
legal-document-analyzer/
│
├── backend/
│   ├── main.py                   # FastAPI REST API server & CORS configuration
│   ├── ollama_service.py         # Ollama HTTP client, prompt formulation, JSON normalizer
│   ├── document_processor.py     # Preprocessing, length validation, paragraph chunker
│   ├── requirements.txt          # Python dependencies
│   └── sample_document.txt       # Lab test Employment Agreement
│
├── frontend/
│   ├── src/
│   │   ├── components/
│   │   │   ├── Header.jsx          # Header with lab title and security badges
│   │   │   ├── SystemHealth.jsx    # Real-time backend & Ollama status checker
│   │   │   ├── WorkflowDiagram.jsx # Visual 7-step pipeline flow diagram
│   │   │   ├── DocumentInput.jsx   # Textarea, file uploader, sample button
│   │   │   ├── AnalysisResult.jsx  # 14 distinct structured analysis cards
│   │   │   └── RawJsonModal.jsx    # Raw JSON payload inspector
│   │   ├── App.jsx                 # Root application state & coordination
│   │   ├── index.css               # Clean, modern Vanilla CSS design system
│   │   └── main.jsx                # React DOM entry point
│   ├── index.html                # Web page shell with typography links
│   ├── vite.config.js            # Vite bundler configuration
│   └── package.json              # Frontend scripts & dependencies
│
└── README.md                     # Experiment manual, commands, and explanation
```

---

## 🚀 Step-by-Step Execution Guide

### Step 1: Start and Verify Ollama

1. Start the Ollama background engine:
   ```bash
   ollama serve
   ```
2. Verify installed models:
   ```bash
   ollama list
   ```
3. If `llama3.2:latest` is not listed, pull it:
   ```bash
   ollama pull llama3.2:latest
   ```

---

### Step 2: Start the FastAPI Backend

1. Navigate to the `backend` directory:
   ```bash
   cd backend
   ```
2. Create and activate a Python virtual environment:
   - **Windows (PowerShell/CMD):**
     ```powershell
     python -m venv venv
     .\venv\Scripts\activate
     ```
   - **Linux / macOS:**
     ```bash
     python3 -m venv venv
     source venv/bin/activate
     ```
3. Install required packages:
   ```bash
   pip install -r requirements.txt
   ```
4. Start the backend server with auto-reload:
   ```bash
   uvicorn main:app --reload --port 8000
   ```
   *The backend will be running at `http://127.0.0.1:8000` (API Docs available at `http://127.0.0.1:8000/docs`).*

---

### Step 3: Start the React Frontend

1. Open a new terminal tab and navigate to the `frontend` directory:
   ```bash
   cd frontend
   ```
2. Install npm dependencies:
   ```bash
   npm install
   ```
3. Launch the development server:
   ```bash
   npm run dev
   ```
4. Open your browser and navigate to `http://localhost:5173`.

---

## 🧪 Testing with the Sample Document

1. Click the **"Load Sample Agreement"** button in the Document Input section.
2. The standard lab Employment Agreement will appear in the textarea:
   ```text
   EMPLOYMENT AGREEMENT

   This Employment Agreement is between ABC Technologies Pvt. Ltd. and John Smith.

   The employee will work as a Software Developer.

   The employment period is 12 months starting from 01-07-2026.

   The employee will receive a monthly salary of ₹50,000.

   The employee must maintain confidentiality regarding company information.

   The employee must perform assigned duties and follow company policies.

   Either party may terminate the agreement by providing 30 days written notice.

   Any intellectual property created during employment belongs to the company.

   The agreement is governed by the applicable laws of India.
   ```
3. Click **"Analyze Document"**.
4. Observe the live pipeline stepper transition through preprocessing, prompt creation, local Ollama execution, and structured result rendering.
5. Review the 14 extracted cards:
   - **Document Type**: Employment Agreement
   - **Parties**: ABC Technologies Pvt. Ltd., John Smith
   - **Purpose**: Software Developer employment
   - **Obligations**: Maintain confidentiality, perform assigned duties, follow policies
   - **Rights**: 30 days written notice for termination
   - **Payment Terms**: ₹50,000 monthly salary
   - **Duration**: 12 months (starting 01-07-2026)
   - **Termination**: 30 days written notice by either party
   - **Confidentiality**: Must maintain confidentiality regarding company information
   - **Important Dates**: 01-07-2026 (Start Date)
   - **Governing Law**: Laws of India
   - **Key Clauses**: Intellectual property assignment, notice period
   - **Potentially Important Clauses**: Intellectual property ownership by employer
   - **Summary**: Comprehensive factual synthesis

---

## 🧠 How the Experiment Works (Simplified Student Explanation)

1. **Document Ingestion**:
   The user supplies legal text either by typing, pasting, or uploading a `.txt` file.
2. **Text Normalization**:
   The backend removes redundant whitespace, normalizes CRLF/LF line breaks, and validates that the text has at least 5 words.
3. **Adaptive Chunking**:
   - For standard contracts (under ~3,000 characters), the text is processed in one direct LLM call.
   - For long contracts, the text is split cleanly into paragraph chunks without cutting sentences midway.
4. **Constrained Prompting**:
   The prompt instructs the local LLM to adopt the persona of a legal document analyzer, extract *only* explicit facts, write `"Not specified in the document."` for missing fields, and enforce a strict JSON output structure.
5. **Ollama JSON Mode**:
   FastAPI sends an HTTP POST request to Ollama's `/api/generate` endpoint with `"format": "json"`, ensuring valid JSON syntax.
6. **Merging & Deduplication**:
   If multi-chunk processing occurred, list attributes (parties, obligations, clauses) are deduplicated, and scalar fields are combined.
7. **Interactive UI Rendering**:
   The frontend organizes the response into color-coded cards, tags, and warning indicators, with options to copy JSON or print a report.

---

## 📡 REST API Reference

### `GET /health`
Verifies backend connectivity and checks if Ollama and `llama3.2:latest` are available.

**Response Example:**
```json
{
  "status": "ok",
  "ollama": true,
  "model": "llama3.2:latest",
  "model_available": true,
  "available_models": ["llama3.2:latest", "qwen:latest"],
  "pull_command": null,
  "message": "Ollama is running and ready."
}
```

### `GET /sample`
Returns the default sample legal agreement for test runs.

### `POST /analyze`
Accepts a document text payload and returns structured analysis.

**Request:**
```json
{
  "document_text": "EMPLOYMENT AGREEMENT\nThis Employment Agreement is between..."
}
```

**Response:**
```json
{
  "success": true,
  "analysis": {
    "document_type": "Employment Agreement",
    "parties": ["ABC Technologies Pvt. Ltd.", "John Smith"],
    "purpose": "Employment as Software Developer",
    "obligations": ["Maintain confidentiality", "Perform assigned duties"],
    "rights": ["30 days notice for termination"],
    "payment_terms": "₹50,000 per month",
    "duration": "12 months starting from 01-07-2026",
    "termination": "30 days written notice by either party",
    "confidentiality": "Must maintain confidentiality regarding company information",
    "important_dates": ["01-07-2026"],
    "governing_law": "Laws of India",
    "key_clauses": ["Intellectual property ownership", "Confidentiality"],
    "potentially_important_clauses": ["All intellectual property belongs to the company"],
    "summary": "This is a 12-month employment agreement between ABC Technologies and John Smith..."
  },
  "metadata": {
    "character_count": 524,
    "word_count": 82,
    "is_chunked": false,
    "chunk_count": 1
  }
}
```
