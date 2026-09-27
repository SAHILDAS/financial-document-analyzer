# Financial Document Analyzer

AI-powered financial document intelligence prototype for analyzing **salary slips** and **bank statements**.

The system combines document ingestion, PDF/text extraction, OCR, document classification, LLM-based structured extraction, schema validation, deterministic financial analysis, confidence scoring, and salary-to-bank reconciliation.

> **Core engineering principle:** The AI extracts information, but deterministic engineering controls decide whether the extracted information is trustworthy.

---

## 1. Project Overview

Financial documents are semi-structured and can vary in layout, labels, table structure, scan quality, date formats, and number formats.

This prototype converts supported documents into structured financial information and then validates and analyzes that information.

### Supported formats

| Format | Supported |
|---|---|
| PDF | Yes |
| JPG | Yes |
| JPEG | Yes |
| PNG | Yes |

### Supported document types

- Salary Slip
- Bank Statement
- Unknown / Unsupported

---

## 2. Core Capabilities

### Salary Slip

Extracts, when available:

- Employee name
- Employee ID
- Employer
- Salary month
- PAN
- Basic salary
- HRA
- Allowances
- Bonus / incentive
- Other earnings
- Gross salary
- PF
- Professional tax
- TDS
- Other deductions
- Total deductions
- Net salary
- Bank account number

Deterministic validation includes:

```text
Expected Net Salary = Gross Salary - Total Deductions
```

The system reports calculated values, reported values, differences, validation errors/warnings, confidence, and whether human review is required.

### Bank Statement

Extracts:

- Account holder
- Bank name
- Account number
- IFSC
- Statement start/end dates
- Opening balance
- Closing balance
- Transactions

Each transaction contains:

```text
Date
Narration
Debit
Credit
Balance
```

The analysis layer identifies:

- Total credits
- Total debits
- Average monthly credit
- Transactions above ₹50,000
- Possible salary credits
- Recurring transactions
- Likely EMI / loan transactions

These are deterministic/heuristic indicators and are not definitive financial, legal, fraud, or credit conclusions.

---

## 3. Salary-to-Bank Reconciliation

The prototype compares salary-slip net salary against candidate bank credits.

```text
Salary Slip
    |
    | Net Salary
    v
Candidate Bank Credits
    |
    +--> Amount similarity
    +--> Date proximity
    +--> Narration similarity
    +--> Periodicity
    |
    v
Candidate Scoring
    |
    v
Matched / Multiple Candidates / No Match / Needs Review
```

### Prototype scoring weights

| Signal | Weight |
|---|---:|
| Amount | 50% |
| Date | 25% |
| Narration | 15% |
| Periodicity | 10% |

These are configurable prototype choices, not universal financial standards.

Reconciliation statuses:

```text
matched
multiple_candidates
no_match
needs_review
```

Results include candidate scores, reasons, confidence, and selected candidate when appropriate.

Reconciliation is deterministic and does not require an LLM.

---

## 4. Architecture

```text
                    Angular 22 Frontend
                            |
                         REST API
                            |
                            v
                     FastAPI Backend
                            |
              +-------------+-------------+
              |             |             |
              v             v             v
          Ingestion     OCR/Text    Classification
              |             |             |
              +-------------+-------------+
                            |
                            v
                  LLM Structured Extraction
                            |
                            v
                    Pydantic Validation
                            |
                            v
               Numeric / Cross-field Validation
                            |
                            v
                  Deterministic Analysis
                            |
                  +---------+---------+
                  |                   |
                  v                   v
            Salary Analysis     Bank Analysis
                  |                   |
                  +---------+---------+
                            |
                            v
                       Reconciliation
                            |
                            v
                  Confidence + Explainability
                            |
                            v
                       Human Review
```

### Processing pipeline

```text
Document
  ↓
File Validation
  ↓
PDF Text Extraction / Image Handling
  ↓
OCR Fallback
  ↓
Text Normalization
  ↓
Classification
  ↓
AI Structured Extraction
  ↓
Pydantic Schema Validation
  ↓
Numeric / Cross-field Validation
  ↓
Deterministic Financial Analysis
  ↓
Confidence
  ↓
Salary ↔ Bank Reconciliation
  ↓
Explainable Result
  ↓
Human Review when Required
```

### LLM provider abstraction

```text
Application
    |
Extraction Service
    |
LLM Provider Interface
    |
    +---- Mock Provider
    |
    +---- OpenAI Provider
```

Provider-specific AI code is isolated from financial business rules, allowing deterministic testing without live LLM calls.

---

## 5. Technology Stack

### Backend

- Python 3.11+
- FastAPI
- Pydantic v2
- Pydantic Settings
- Uvicorn
- Pytest
- PyMuPDF
- Pillow
- pytesseract
- Tesseract OCR
- OpenAI Python SDK
- Configurable LLM provider

### Frontend

- Angular 22
- TypeScript
- Angular HttpClient
- SCSS
- Vitest / Angular testing tooling

### Development

- Git
- GitHub
- Linux
- Python virtual environment
- npm

The prototype intentionally avoids Kafka, Redis, Kubernetes, microservices, CQRS, and event sourcing because they are not required for the current scope.

---

## 6. Repository Structure

```text
financial-document-analyzer/
├── backend/
│   ├── app/
│   │   ├── api/routes/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   ├── classification/
│   │   │   ├── ocr/
│   │   │   ├── extraction/
│   │   │   │   └── providers/
│   │   │   ├── validation/
│   │   │   ├── analysis/
│   │   │   └── reconciliation/
│   │   └── main.py
│   ├── tests/
│   ├── requirements.txt
│   └── .env
├── frontend/
│   ├── src/app/
│   ├── package.json
│   └── angular.json
├── samples/
│   ├── salary/
│   ├── bank/
│   └── reconciliation/
├── docs/
├── ARCHITECTURE.md
├── API.md
├── SECURITY.md
├── DECISIONS.md
├── LIMITATIONS.md
├── DEMO.md
├── README.md
├── .env.example
├── .gitignore
└── docker-compose.yml
```

`.env` is local-only and must never be committed.

---

## 7. Prerequisites

Install:

- Git
- Python 3.11+
- Node.js 24.x
- npm
- Angular CLI
- Tesseract OCR

Verify:

```bash
git --version
python3 --version
node --version
npm --version
ng version
tesseract --version
```

---

## 8. Clone

```bash
git clone git@github.com:SAHILDAS/financial-document-analyzer.git
cd financial-document-analyzer
```

HTTPS alternative:

```bash
git clone https://github.com/SAHILDAS/financial-document-analyzer.git
cd financial-document-analyzer
```

---

## 9. Backend Setup

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

Create the environment file:

```bash
cp .env.example .env
```

Example configuration:

```env
APP_NAME=Financial Document Analyzer
APP_ENV=development
APP_DEBUG=true
BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000
FRONTEND_URL=http://localhost:4200
LLM_PROVIDER=openai
LLM_API_KEY=your-api-key
OCR_PROVIDER=tesseract
MAX_FILE_SIZE_MB=20
```

Never commit `.env`. Commit only `.env.example`.

For automated tests, the suite forces the mock LLM provider so tests do not make live API calls.

---

## 10. Run Backend

```bash
cd backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

Backend:

```text
http://127.0.0.1:8000
```

Health:

```bash
curl http://127.0.0.1:8000/api/health
```

Expected:

```json
{
  "status": "ok",
  "service": "Financial Document Analyzer",
  "environment": "development"
}
```

Swagger:

```text
http://127.0.0.1:8000/docs
```

OpenAPI:

```text
http://127.0.0.1:8000/openapi.json
```

---

## 11. Frontend Setup

In another terminal:

```bash
cd financial-document-analyzer/frontend
npm install
npm start
```

Frontend:

```text
http://localhost:4200
```

Connectivity:

```text
Angular
  ↓
HttpClient
  ↓
FastAPI /api/health
  ↓
HTTP 200
  ↓
Angular UI
```

---

## 12. API Surface

### Health

```http
GET /api/health
```

### Analyze document

```http
POST /api/documents/analyze
```

Pipeline:

```text
Ingestion
→ OCR/Text Extraction
→ Classification
→ Structured Extraction
→ Validation
→ Analysis
```

### Salary-specific analysis

```http
POST /api/documents/salary-slip
```

### Bank-specific analysis

```http
POST /api/documents/bank-statement
```

### Reconciliation

```http
POST /api/documents/reconcile
```

### Optional document lookup

```http
GET /api/documents/{document_id}
```

See `API.md` for detailed request/response contracts.

---

## 13. Error Handling

The application avoids exposing internal stack traces to users.

Handled cases include:

- Unsupported file type
- Invalid file
- File too large
- Unreadable PDF
- Password-protected PDF
- OCR failure
- Empty/unusable extracted text
- Unknown document type
- LLM/provider failure
- Malformed structured extraction
- Invalid financial values
- No salary credit candidate
- Multiple salary candidates
- Low-confidence result
- Human review required

---

## 14. Confidence Model

Prototype thresholds:

```text
0.85 – 1.00   High
0.65 – 0.84   Medium
0.00 – 0.64   Low
```

Confidence considers factors such as:

- OCR/text quality
- Field completeness
- Validation errors
- Validation warnings
- Extraction completeness
- Reconciliation score

Low-confidence or inconsistent results can require:

```text
NEEDS_REVIEW
```

These thresholds are implementation choices, not statistical guarantees.

---

## 15. Deterministic Financial Analysis

Financial calculations are performed by application code.

```text
Total Credits = Σ credit transactions

Total Debits = Σ debit transactions

Expected Net Salary =
Gross Salary - Total Deductions
```

Large transactions:

```text
Transaction Amount > ₹50,000
```

Recurring detection considers:

- Normalized narration
- Similar amounts
- Repeated occurrence
- Approximate intervals

EMI/loan indicators consider:

- EMI/loan keywords
- NACH/ECS indicators
- Recurring debit behavior
- Similar amount
- Monthly periodicity

These are indicators and heuristics, not definitive classifications.

---

## 16. Testing

### Backend

```bash
cd backend
source .venv/bin/activate
pytest -q
```

Verified:

```text
183 passed, 1 warning
```

The warning is a dependency-level Starlette/AnyIO deprecation warning.

### Frontend

```bash
cd frontend
npm test -- --watch=false
```

Verified:

```text
Test Files  1 passed
Tests       38 passed
```

### Production build

```bash
npm run build
```

Verified:

```text
Application bundle generation complete.
```

### Test coverage areas

- File ingestion and validation
- PDF extraction
- OCR
- Classification
- Salary extraction and normalization
- Salary consistency
- Confidence
- Bank transaction extraction
- Date/currency normalization
- Credit/debit analysis
- Salary candidates
- Recurring transactions
- EMI indicators
- Reconciliation scoring
- Multiple candidates
- No match
- Needs review
- API errors
- Frontend reconciliation state and formatting

---

## 17. Sample Data

### Salary

```text
samples/salary/
├── Ananya Mehta Salary slip.pdf
├── NextGen Corporate Salary Slip.png
├── Payslip_Sanjib Das_September_2026.pdf
└── TechFusion Corporate Salary Slip.png
```

### Bank

```text
samples/bank/
├── Axis Bank Savings Statement Layout.png
├── HDFC Bank July 2025 Statement.png
├── ICICI Bank August 2025 Statement.png
├── PhonePe Digital Bank Statement.png
└── SBI Account Statement Page.png
```

### Reconciliation

```text
samples/reconciliation/
├── bank_sanjib_sep_2026_amount_mismatch.png
├── bank_sanjib_sep_2026_match.png
├── bank_sanjib_sep_2026_multiple_candidates.png
├── bank_sanjib_sep_2026_no_salary.png
└── salary_sanjib_sep_2026_match.png
```

Use only synthetic/test-oriented financial data in the repository. Do not add real financial documents or real PII.

---

## 18. Verified Reconciliation Scenarios

The reconciliation workflow has been verified through the Angular UI.

### Exact match

```text
Salary net:   ₹50,500
Bank credit:  ₹50,500
Status:       Matched
Confidence:   95%
```

### Amount mismatch

```text
Salary net:   ₹50,500
Bank credit:  ₹48,500
Status:       Needs Review
```

The system does not automatically accept a materially different credit merely because other signals are strong.

### Multiple candidates

Two similarly strong salary-like credits result in:

```text
Multiple Candidates
```

The system does not silently choose between ambiguous candidates.

### No salary

When no credible salary credit exists:

```text
No Match
```

These scenarios demonstrate explicit handling of match, ambiguity, mismatch, and absence of a credible candidate.

---

## 19. Security & Privacy

Financial documents contain sensitive information.

Principles:

- Never commit API keys.
- Never commit `.env`.
- Do not log complete financial documents.
- Do not unnecessarily log raw OCR text.
- Mask sensitive identifiers where appropriate.
- Use temporary processing storage.
- Clean temporary files after processing.
- Do not expose internal stack traces.
- Use synthetic/test-oriented sample data.
- Document external OCR/LLM data exposure.

When using a hosted LLM, a production system must additionally address provider retention, data processing agreements, PII minimization, data residency, encryption, access control, auditing, and deletion/retention policies.

See `SECURITY.md`.

---

## 20. Design Principles

### AI is not the source of truth

The LLM performs extraction.

Application code performs:

- Calculations
- Validation
- Cross-field consistency checks
- Financial analysis
- Reconciliation scoring
- Threshold decisions
- Final status decisions

### Multi-layer validation

```text
LLM Output
  ↓
Pydantic Schema
  ↓
Field Validation
  ↓
Cross-field Validation
  ↓
Deterministic Financial Rules
  ↓
Confidence
```

### Explain uncertainty

The UI exposes:

- Confidence
- Validation results
- Warnings
- Candidate scores
- Reconciliation reasons
- Human-review requirements

### Graceful failure

The system prefers useful application errors over stack traces.

### Avoid premature infrastructure

The prototype does not require Kafka, Redis, Kubernetes, microservices, CQRS, or event sourcing.

Priority:

```text
Correctness
  ↓
Reliability
  ↓
Explainability
  ↓
Testability
  ↓
Security
  ↓
Deployment
  ↓
Visual polish
```

---

## 21. Prototype vs Production

This repository is a prototype.

A production implementation would additionally require:

- Authentication
- Authorization
- Persistent storage
- Encrypted object storage
- Stronger PII controls
- Audit logging
- Rate limiting
- Asynchronous processing
- Worker infrastructure
- Retry policies
- Provider failover
- Monitoring and alerting
- High availability
- Disaster recovery
- Data retention enforcement
- Compliance controls
- Multi-tenant isolation
- Formal model/provider evaluation
- Production secrets management

These are intentionally outside the current prototype scope.

---

## 22. Current Implementation Status

### Foundation

- [x] FastAPI application
- [x] Angular application
- [x] Health API
- [x] Frontend/backend connectivity
- [x] Domain schemas
- [x] Architecture documentation
- [x] API documentation
- [x] Security documentation
- [x] Decision documentation
- [x] Limitations documentation
- [x] Demo documentation

### Document Processing

- [x] File ingestion
- [x] File validation
- [x] File size validation
- [x] PDF inspection
- [x] Native PDF text extraction
- [x] Image processing
- [x] OCR fallback
- [x] Scanned PDF OCR
- [x] Text normalization
- [x] Extraction quality metadata
- [x] Graceful ingestion errors
- [x] Document classification

### Salary

- [x] Salary classification
- [x] Structured LLM extraction
- [x] Mock provider
- [x] OpenAI provider
- [x] Schema validation
- [x] Numeric normalization
- [x] Gross/deduction/net validation
- [x] Salary consistency validation
- [x] Confidence calculation
- [x] Salary UI
- [x] Real salary extraction verification

### Bank

- [x] Bank extraction
- [x] Date normalization
- [x] Indian currency/number normalization
- [x] Transaction validation
- [x] Credit/debit totals
- [x] Large transaction detection
- [x] Salary credit candidates
- [x] Recurring transaction detection
- [x] EMI/loan indicators
- [x] Bank UI
- [x] Real bank extraction verification

### Reconciliation

- [x] Candidate generation
- [x] Amount scoring
- [x] Date scoring
- [x] Narration scoring
- [x] Periodicity scoring
- [x] Candidate scoring
- [x] Amount/date tolerance
- [x] Multiple candidate handling
- [x] No-match handling
- [x] Needs-review handling
- [x] Explainable results
- [x] Reconciliation API
- [x] Angular workflow
- [x] Exact-match verification
- [x] Amount-mismatch verification
- [x] Multiple-candidate verification
- [x] No-match verification

### Engineering

- [x] Backend automated tests
- [x] Frontend automated tests
- [x] Production frontend build
- [x] Secret-file protection
- [x] Git diff validation
- [x] End-to-end manual verification
- [x] GitHub push

Current verified tests:

```text
Backend:  183 passed
Frontend: 38 passed
```

---

## 23. Demo Workflow

Recommended presentation:

```text
1. Introduce the problem
2. Explain architecture
3. Upload salary slip
4. Show classification
5. Show extracted salary fields
6. Show deterministic salary validation
7. Show confidence
8. Upload bank statement
9. Show transactions
10. Show financial analysis
11. Show salary-credit candidates
12. Show recurring/EMI indicators
13. Reconcile salary with bank
14. Demonstrate exact match
15. Demonstrate amount mismatch
16. Demonstrate multiple candidates
17. Demonstrate no match
18. Explain security and production evolution
```

The key message:

> **AI extracts. Engineering validates. Deterministic rules analyze. Explainability builds trust.**

---

## 24. Troubleshooting

### Backend does not start

```bash
cd backend
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Port 8000 is busy

```bash
ss -ltnp | grep :8000
```

or:

```bash
lsof -i :8000
```

### Angular does not start

```bash
cd frontend
npm install
npm start
```

### Angular cannot connect to backend

```bash
curl http://127.0.0.1:8000/api/health
```

Check `backend/.env`:

```env
FRONTEND_URL=http://localhost:4200
```

Restart FastAPI after environment changes.

### OCR does not work

```bash
tesseract --version
```

### OpenAI extraction does not work

Verify:

```env
LLM_PROVIDER=openai
LLM_API_KEY=...
```

Tests use the mock provider and therefore do not require live LLM requests.

---

## 25. Git Workflow

Before committing:

```bash
git status
git diff --check
git diff --stat
```

Commit:

```bash
git add .
git commit -m "feat: add AI extraction and document reconciliation"
```

Push:

```bash
git push origin main
```

Verify:

```bash
git status
git log -1 --oneline
```

Current milestone:

```text
d7fc4b2 feat: add AI extraction and document reconciliation
```

---

## 26. Start Here

```bash
git clone git@github.com:SAHILDAS/financial-document-analyzer.git
cd financial-document-analyzer
```

### Backend

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --reload
```

### Frontend

In another terminal:

```bash
cd financial-document-analyzer/frontend
npm install
npm start
```

Open:

```text
http://localhost:4200
```

### Tests

```bash
cd financial-document-analyzer/backend
source .venv/bin/activate
pytest -q
```

```bash
cd financial-document-analyzer/frontend
npm test -- --watch=false
```

### Build

```bash
cd financial-document-analyzer/frontend
npm run build
```

---

## 27. Documentation

- `ARCHITECTURE.md` — system and component architecture
- `API.md` — API contracts and endpoint behavior
- `SECURITY.md` — security and privacy considerations
- `DECISIONS.md` — architectural decisions
- `LIMITATIONS.md` — prototype limitations
- `DEMO.md` — demonstration and presentation workflow

---

## 28. Final Objective

The prototype demonstrates a complete workflow:

```text
Financial Document
        ↓
File Validation
        ↓
Text Extraction / OCR
        ↓
Document Classification
        ↓
AI Structured Extraction
        ↓
Schema Validation
        ↓
Deterministic Validation
        ↓
Financial Analysis
        ↓
Salary ↔ Bank Reconciliation
        ↓
Confidence + Explainability
        ↓
Human Review when Required
```

The project demonstrates that AI can handle difficult unstructured-document understanding while conventional software engineering remains responsible for validation, calculations, business rules, financial analysis, reconciliation, confidence decisions, error handling, and reliability.

> **AI extracts. Engineering validates. Deterministic rules analyze. Explainability builds trust.**
