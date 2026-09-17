# Financial Document Analyzer

AI-powered financial document intelligence prototype for analyzing
**salary slips** and **bank statements**.

The system combines document processing, OCR, LLM-based structured
extraction, deterministic validation, financial analysis, and
salary-to-bank reconciliation.

> **Core engineering principle:** The AI extracts information, but
> deterministic engineering controls decide whether the extracted
> information is trustworthy.

------------------------------------------------------------------------

## 1. Project Overview

Financial documents are semi-structured. Salary slips and bank
statements can have different layouts, labels, table structures, scan
quality, and formatting.

This project provides a processing pipeline that converts those
documents into structured financial information and then validates and
analyzes the result.

### Supported documents

  Format   Supported
  -------- -----------
  PDF      Yes
  JPG      Yes
  JPEG     Yes
  PNG      Yes

### Supported document types

-   Salary Slip
-   Bank Statement
-   Unknown / Unsupported

------------------------------------------------------------------------

## 2. What the System Does

### Salary Slip

The analyzer is designed to extract:

-   Employee name
-   Employee ID
-   Employer
-   Salary month
-   PAN, when available
-   Basic salary
-   HRA
-   Allowances
-   Bonus / incentive
-   Other earnings
-   Gross salary
-   PF
-   Professional tax
-   TDS
-   Other deductions
-   Total deductions
-   Net salary
-   Bank account number, when available

It then performs deterministic validation such as:

``` text
Gross Salary - Total Deductions ≈ Net Salary
```

------------------------------------------------------------------------

### Bank Statement

The analyzer is designed to extract:

-   Account holder
-   Bank
-   Account number
-   IFSC, when available
-   Statement start date
-   Statement end date
-   Opening balance
-   Closing balance
-   Transactions

Each transaction contains:

``` text
Date
Narration
Debit
Credit
Balance
```

The system can then calculate and identify:

-   Total credits
-   Total debits
-   Transactions above ₹50,000
-   Possible salary credits
-   Recurring transactions
-   Likely EMI / loan transactions

These indicators are deterministic or heuristic and should not be
treated as definitive financial or legal conclusions.

------------------------------------------------------------------------

## 3. Salary-to-Bank Reconciliation

The system compares the salary-slip net salary with candidate bank
credits.

Example:

``` text
Salary Slip
Net Salary: ₹66,500
       |
       v
Bank Statement
Candidate Credit: ₹66,500
       |
       v
Reconciliation
       |
       +--> Amount
       +--> Date
       +--> Narration
       +--> Periodicity
       |
       v
Matched / Not Matched / Needs Review
```

The prototype uses configurable reconciliation weights conceptually
based on:

-   Amount: 50%
-   Date: 25%
-   Narration: 15%
-   Periodicity: 10%

These are implementation choices for the prototype, not universal
financial standards.

------------------------------------------------------------------------

## 4. Architecture

``` text
                    Angular Frontend
                          |
                          | REST API
                          v
                    FastAPI Backend
                          |
              +-----------+-----------+
              |           |           |
              v           v           v
          Ingestion   OCR/Text    Classification
                          |
                          v
                  LLM Extraction
                          |
                          v
                 Pydantic Validation
                          |
                          v
              Deterministic Validation
                          |
                          v
                 Financial Analysis
                          |
                          v
                   Reconciliation
                          |
                          v
             Confidence / Human Review
```

### Processing principle

``` text
Document
   ↓
File Validation
   ↓
Text Extraction / OCR
   ↓
Classification
   ↓
AI Structured Extraction
   ↓
Schema Validation
   ↓
Numeric / Cross-field Validation
   ↓
Financial Analysis
   ↓
Reconciliation
   ↓
Confidence + Explainability
```

See:

-   `ARCHITECTURE.md`
-   `API.md`
-   `SECURITY.md`
-   `DECISIONS.md`
-   `LIMITATIONS.md`
-   `DEMO.md`

for detailed project documentation.

------------------------------------------------------------------------

# 5. Technology Stack

## Backend

-   Python
-   FastAPI
-   Pydantic v2
-   Pydantic Settings
-   Uvicorn
-   Pytest
-   OCR/document-processing libraries
-   Configurable LLM provider

## Frontend

-   Angular 22
-   TypeScript
-   Angular HttpClient
-   SCSS
-   Vitest / Angular testing tooling

## Development

-   Git
-   GitHub
-   Linux
-   Python virtual environment
-   npm

## Planned / Optional Infrastructure

-   Docker
-   Docker Compose
-   CI/CD

The prototype intentionally avoids unnecessary infrastructure such as
Kafka, Redis, Kubernetes, and microservices unless a clear technical
requirement emerges.

------------------------------------------------------------------------

# 6. Repository Structure

``` text
financial-document-analyzer/
│
├── backend/
│   ├── app/
│   │   ├── api/
│   │   │   └── routes/
│   │   ├── core/
│   │   ├── schemas/
│   │   ├── services/
│   │   │   ├── ingestion/
│   │   │   ├── classification/
│   │   │   ├── ocr/
│   │   │   ├── extraction/
│   │   │   ├── validation/
│   │   │   ├── analysis/
│   │   │   └── reconciliation/
│   │   └── main.py
│   │
│   ├── tests/
│   ├── requirements.txt
│   └── .env
│
├── frontend/
│   ├── src/
│   │   └── app/
│   │       └── core/
│   ├── package.json
│   └── angular.json
│
├── samples/
│   ├── salary/
│   ├── bank/
│   └── invalid/
│
├── tests/
├── docs/
│
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

Some directories and services are introduced progressively during
implementation.

------------------------------------------------------------------------

# 7. Prerequisites

Install the following before starting:

### Required

-   Git
-   Python 3.11+
-   Node.js 24.x
-   npm
-   Angular CLI
-   Tesseract OCR for OCR-based processing

Check versions:

``` bash
git --version
python3 --version
node --version
npm --version
ng version
tesseract --version
```

The current development environment targets Node.js 24.x and Angular 22.

------------------------------------------------------------------------

# 8. Clone the Repository

``` bash
git clone git@github.com:SAHILDAS/financial-document-analyzer.git
cd financial-document-analyzer
```

If using HTTPS instead:

``` bash
git clone https://github.com/SAHILDAS/financial-document-analyzer.git
cd financial-document-analyzer
```

------------------------------------------------------------------------

# 9. Backend Setup

Move into the backend:

``` bash
cd backend
```

Create a virtual environment:

``` bash
python3 -m venv .venv
```

Activate it:

``` bash
source .venv/bin/activate
```

Install dependencies:

``` bash
pip install -r requirements.txt
```

If the requirements file is updated during development, run:

``` bash
pip install -r requirements.txt
```

again.

------------------------------------------------------------------------

# 10. Backend Environment Configuration

Create the local environment file:

``` bash
cp .env.example .env
```

If `.env.example` is not yet available, create `.env` using the
configuration documented in the project.

Typical development configuration:

``` env
APP_NAME=Financial Document Analyzer
APP_ENV=development
APP_DEBUG=true

BACKEND_HOST=127.0.0.1
BACKEND_PORT=8000

FRONTEND_URL=http://localhost:4200

LLM_PROVIDER=
LLM_API_KEY=

OCR_PROVIDER=tesseract

MAX_FILE_SIZE_MB=20
```

### Important

Never commit:

``` text
.env
```

to Git.

Use:

``` text
.env.example
```

for non-secret configuration templates.

------------------------------------------------------------------------

# 11. Run the Backend

From:

``` text
backend/
```

activate the environment:

``` bash
source .venv/bin/activate
```

Start FastAPI:

``` bash
uvicorn app.main:app --reload
```

The development server should be available at:

``` text
http://127.0.0.1:8000
```

------------------------------------------------------------------------

# 12. Verify the Backend

Health endpoint:

``` bash
curl http://127.0.0.1:8000/api/health
```

Expected response:

``` json
{
  "status": "ok",
  "service": "Financial Document Analyzer",
  "environment": "development"
}
```

Root endpoint:

``` bash
curl http://127.0.0.1:8000/
```

API documentation:

``` text
http://127.0.0.1:8000/docs
```

OpenAPI schema:

``` text
http://127.0.0.1:8000/openapi.json
```

------------------------------------------------------------------------

# 13. Run Backend Tests

From `backend/`:

``` bash
source .venv/bin/activate
pytest -v
```

The foundation currently includes health and domain schema tests.

The test suite will grow as ingestion, OCR, extraction, validation,
analysis, and reconciliation are implemented.

------------------------------------------------------------------------

# 14. Frontend Setup

Open another terminal.

From the project root:

``` bash
cd frontend
```

Install dependencies:

``` bash
npm install
```

Start Angular:

``` bash
npm start
```

The development application should be available at:

``` text
http://localhost:4200
```

------------------------------------------------------------------------

# 15. Verify Frontend ↔ Backend Connectivity

With both applications running:

``` text
Angular
http://localhost:4200

FastAPI
http://127.0.0.1:8000
```

The Angular application calls:

``` text
GET http://127.0.0.1:8000/api/health
```

The starter page should display:

``` text
● Backend Connected

Financial Document Analyzer — development
```

This confirms:

``` text
Angular
   ↓
HttpClient
   ↓
FastAPI
   ↓
/api/health
   ↓
HTTP 200
   ↓
Angular UI
```

------------------------------------------------------------------------

# 16. Build the Frontend

From `frontend/`:

``` bash
npm run build
```

A successful build should report:

``` text
Application bundle generation complete.
```

------------------------------------------------------------------------

# 17. Development Workflow

Use two terminals.

### Terminal 1 --- Backend

``` bash
cd financial-document-analyzer/backend
source .venv/bin/activate
uvicorn app.main:app --reload
```

### Terminal 2 --- Frontend

``` bash
cd financial-document-analyzer/frontend
npm start
```

Then open:

``` text
http://localhost:4200
```

------------------------------------------------------------------------

# 18. Implementation Roadmap

The project is implemented incrementally.

## Day 1 --- Foundation

Completed:

-   Repository setup
-   FastAPI foundation
-   Angular foundation
-   Domain contracts
-   Health endpoint
-   Angular/backend connectivity
-   Architecture documentation
-   API documentation
-   Security documentation
-   Architecture decisions
-   Limitations
-   Demo guide

------------------------------------------------------------------------

## Day 2 --- Document Ingestion & OCR

Planned:

-   File validation
-   File type validation
-   File size validation
-   Temporary file lifecycle
-   PDF text extraction
-   Image handling
-   OCR fallback
-   Text normalization
-   Extraction quality metadata
-   Graceful ingestion errors
-   Initial document classification

Target flow:

``` text
PDF / JPG / JPEG / PNG
          ↓
    File Validation
          ↓
 Temporary Processing
          ↓
 PDF Text Extraction
          ↓
 OCR Fallback
          ↓
 Normalized Text
```

------------------------------------------------------------------------

## Day 3 --- Salary Extraction

Planned:

-   Salary-slip classification
-   Structured LLM extraction
-   Salary schema validation
-   Numeric normalization
-   Gross/deduction/net validation
-   Confidence
-   Salary analysis UI

------------------------------------------------------------------------

## Day 4 --- Bank Extraction & Analysis

Planned:

-   Bank statement extraction
-   Multipage transaction handling
-   Transaction validation
-   Credit/debit totals
-   Large transaction detection
-   Salary credit candidates
-   Recurring transaction detection
-   EMI/loan indicators
-   Bank analysis UI

------------------------------------------------------------------------

## Day 5 --- Reconciliation

Planned:

-   Salary-to-bank reconciliation
-   Candidate generation
-   Candidate scoring
-   Amount tolerance
-   Date tolerance
-   Narration similarity
-   Periodicity
-   Multiple candidate handling
-   No-match handling
-   Explainable results
-   Full frontend integration

------------------------------------------------------------------------

## Day 6 --- Reliability & Security

Planned:

-   Error handling
-   Edge cases
-   Unit tests
-   Integration tests
-   Security review
-   PII masking
-   Structured logging
-   Docker
-   CI
-   Feature freeze

------------------------------------------------------------------------

## Day 7 --- Deployment & QA

Planned:

-   Deployment preparation
-   End-to-end QA
-   Documentation review
-   Demo validation
-   Screenshots
-   Presentation preparation

------------------------------------------------------------------------

## Day 8 --- Final Verification

Final day is reserved for:

-   Regression testing
-   Demo rehearsal
-   Final bug fixes
-   Repository cleanup
-   Documentation verification
-   Presentation

No major new features should be introduced on the final day.

------------------------------------------------------------------------

# 19. API Surface

Current foundation endpoints:

``` text
GET /api/health
GET /
```

Planned core endpoints:

``` text
POST /api/documents/analyze
POST /api/documents/salary-slip
POST /api/documents/bank-statement
POST /api/documents/reconcile
GET  /api/documents/{document_id}
```

See `API.md` for the complete API contract and processing behavior.

------------------------------------------------------------------------

# 20. Testing Strategy

Tests should focus on business behavior rather than only implementation
details.

Important test areas:

### Ingestion

-   Supported file types
-   Unsupported file types
-   File size limits
-   Invalid files
-   Password-protected files
-   Unreadable files

### Classification

-   Salary slip
-   Bank statement
-   Unknown document

### Salary

-   Schema validation
-   Missing fields
-   Gross salary
-   Deductions
-   Net salary
-   Calculation consistency
-   Invalid numeric values

### Bank

-   Transaction parsing
-   Credit/debit totals
-   Large transactions
-   Duplicate transactions
-   Salary credit candidates
-   Recurring transactions
-   EMI candidates

### Reconciliation

-   Exact match
-   Date tolerance
-   Amount tolerance
-   Narration differences
-   Multiple candidates
-   No match
-   Low confidence

### API

-   Successful requests
-   Invalid uploads
-   Processing failures
-   Graceful error responses

Run:

``` bash
cd backend
source .venv/bin/activate
pytest -v
```

------------------------------------------------------------------------

# 21. Sample Data

Use synthetic financial data only.

Recommended structure:

``` text
samples/
├── salary/
│   ├── salary_clean.pdf
│   ├── salary_missing_fields.pdf
│   ├── salary_inconsistent.pdf
│   └── salary_scan.pdf
│
├── bank/
│   ├── bank_clean.pdf
│   ├── bank_multipage.pdf
│   ├── bank_duplicate_transactions.pdf
│   └── bank_no_salary.pdf
│
└── invalid/
    ├── unknown_document.pdf
    └── unsupported.txt
```

Do not add real salary slips, bank statements, PAN numbers, or account
information to the repository.

------------------------------------------------------------------------

# 22. Security & Privacy

Financial documents contain sensitive information.

The project therefore follows these principles:

-   Do not log complete financial documents.
-   Do not log raw OCR text unnecessarily.
-   Do not commit API keys.
-   Do not commit `.env`.
-   Mask PAN and account numbers in user-facing output where
    appropriate.
-   Use temporary storage for document processing.
-   Clean temporary files after processing.
-   Document external OCR/LLM data exposure.
-   Use synthetic sample data.
-   Do not expose internal stack traces to users.

See `SECURITY.md` for detailed security requirements and production
considerations.

------------------------------------------------------------------------

# 23. Important Design Principles

### 1. AI is not the source of truth

The LLM performs extraction.

Application code performs:

-   calculations
-   validation
-   financial analysis
-   reconciliation scoring
-   thresholds
-   status decisions

------------------------------------------------------------------------

### 2. Validate at multiple layers

``` text
LLM Output
    ↓
Pydantic Schema
    ↓
Field Validation
    ↓
Cross-field Validation
    ↓
Deterministic Financial Rules
```

------------------------------------------------------------------------

### 3. Explain uncertain results

The system should surface:

``` text
Confidence
Warnings
Validation results
Reconciliation reasons
Human review requirements
```

rather than silently accepting uncertain data.

------------------------------------------------------------------------

### 4. Prefer graceful failure

Unsupported or malformed documents should produce useful errors such as:

``` text
Unsupported file type
Unreadable document
OCR failed
Document classification failed
Extraction failed
No matching salary credit found
Human review required
```

rather than stack traces.

------------------------------------------------------------------------

### 5. Avoid premature infrastructure

The prototype does not require:

-   Kafka
-   Redis
-   Kubernetes
-   Microservices
-   CQRS
-   Event sourcing

unless a concrete requirement emerges.

The priority is:

``` text
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

------------------------------------------------------------------------

# 24. Confidence Model

Confidence is intended to communicate extraction/reconciliation
uncertainty.

Prototype implementation thresholds:

``` text
0.85 – 1.00   High
0.65 – 0.84   Medium
0.00 – 0.64   Low
```

These thresholds are implementation choices, not statistical guarantees.

Low-confidence results should be eligible for:

``` text
NEEDS_REVIEW
```

------------------------------------------------------------------------

# 25. Financial Analysis

Financial calculations are deterministic.

Examples:

``` text
Total Credits = Σ credit transactions

Total Debits = Σ debit transactions

Expected Net Salary =
Gross Salary - Total Deductions
```

Large transactions:

``` text
Transaction Amount > ₹50,000
```

Recurring transactions can consider:

-   normalized narration
-   similar amounts
-   repeated occurrence
-   approximate intervals

EMI/loan indicators can consider:

-   EMI keywords
-   loan keywords
-   NACH/ECS indicators
-   recurring debit
-   similar amount
-   monthly periodicity

These are indicators and heuristics, not definitive classifications.

------------------------------------------------------------------------

# 26. Demo

A recommended demo sequence is:

``` text
1. Introduce the problem
2. Show architecture
3. Upload salary slip
4. Show classification
5. Show extracted salary information
6. Show deterministic salary validation
7. Upload bank statement
8. Show transactions
9. Show financial analysis
10. Show salary credit detection
11. Show recurring transactions
12. Show EMI indicator
13. Reconcile salary with bank credit
14. Demonstrate low-confidence input
15. Demonstrate graceful error handling
16. Explain security and production evolution
```

See `DEMO.md` for the complete presentation script.

------------------------------------------------------------------------

# 27. Troubleshooting

## Backend does not start

Check:

``` bash
python3 --version
```

Activate the virtual environment:

``` bash
source backend/.venv/bin/activate
```

Install dependencies:

``` bash
pip install -r backend/requirements.txt
```

Run:

``` bash
uvicorn app.main:app --reload
```

------------------------------------------------------------------------

## Port 8000 is already in use

Find the process:

``` bash
ss -ltnp | grep :8000
```

or:

``` bash
lsof -i :8000
```

Stop the old process if appropriate, then restart the backend.

------------------------------------------------------------------------

## Angular does not start

Check:

``` bash
node --version
npm --version
```

Install dependencies:

``` bash
cd frontend
npm install
```

Start:

``` bash
npm start
```

------------------------------------------------------------------------

## Angular cannot connect to backend

Verify:

``` bash
curl http://127.0.0.1:8000/api/health
```

Check:

``` text
backend/.env
```

for:

``` env
FRONTEND_URL=http://localhost:4200
```

Then make sure Angular is opened using:

``` text
http://localhost:4200
```

not a different origin unless that origin has been explicitly configured
in FastAPI CORS settings.

------------------------------------------------------------------------

## CORS error

The backend currently allows the configured frontend origin.

Verify:

``` env
FRONTEND_URL=http://localhost:4200
```

Restart FastAPI after changing environment configuration.

------------------------------------------------------------------------

## OCR does not work

Verify Tesseract:

``` bash
tesseract --version
```

If it is missing, install it using your operating system's package
manager.

OCR behavior is documented further in `LIMITATIONS.md`.

------------------------------------------------------------------------

# 28. Git Workflow

Use focused commits.

Examples:

``` bash
git add .
git commit -m "chore: initialize financial document analyzer"
```

``` bash
git commit -m "feat: add FastAPI application foundation"
```

``` bash
git commit -m "feat: add Angular frontend foundation"
```

``` bash
git commit -m "feat: define document analysis contracts"
```

Future examples:

``` text
feat: add document ingestion
feat: add PDF text extraction
feat: add OCR fallback
feat: add document classification
feat: add salary extraction
feat: add salary validation
feat: add bank statement extraction
feat: add transaction analysis
feat: add salary reconciliation
test: add reconciliation coverage
feat: add analysis dashboard
chore: add Docker configuration
ci: add backend and frontend checks
docs: update demo workflow
```

Before committing:

``` bash
git status
git diff --check
git diff --stat
```

After committing:

``` bash
git log --oneline --decorate -10
```

Push:

``` bash
git push origin main
```

------------------------------------------------------------------------

# 29. Development Rules

While implementing the project:

1.  Work incrementally.
2.  Do not build the entire application in one step.
3.  Verify each major component before depending on it.
4.  Keep business rules deterministic.
5.  Keep provider-specific AI/OCR code behind service interfaces where
    practical.
6.  Keep routes thin.
7.  Keep domain schemas explicit.
8.  Write tests with each important business rule.
9.  Do not commit secrets or real financial data.
10. Prefer simple architecture unless complexity is justified.
11. Document significant architectural decisions.
12. Keep the final demo reproducible.

------------------------------------------------------------------------

# 30. Prototype vs Production

This repository is a prototype.

A production version would require additional capabilities such as:

-   Authentication
-   Authorization
-   Persistent storage
-   Encrypted object storage
-   Audit logging
-   Stronger PII controls
-   Rate limiting
-   Asynchronous processing
-   Worker infrastructure
-   Retry and failure handling
-   Provider failover
-   Monitoring
-   Alerting
-   High availability
-   Disaster recovery
-   Data retention enforcement
-   Compliance controls
-   Multi-tenant isolation

These are intentionally separated from the initial prototype scope.

------------------------------------------------------------------------

# 31. Current Status

### Foundation

-   [x] Repository initialized
-   [x] FastAPI application
-   [x] Angular application
-   [x] Health API
-   [x] Angular → FastAPI connectivity
-   [x] Domain schemas
-   [x] Initial backend tests
-   [x] Architecture documentation

### Document Processing

-   [ ] File ingestion
-   [ ] File validation
-   [ ] PDF extraction
-   [ ] OCR
-   [ ] Classification

### Salary

-   [ ] LLM extraction
-   [ ] Salary validation
-   [ ] Confidence
-   [ ] Salary UI

### Bank

-   [ ] Bank extraction
-   [ ] Transaction analysis
-   [ ] Salary detection
-   [ ] Recurring detection
-   [ ] EMI detection
-   [ ] Bank UI

### Reconciliation

-   [ ] Candidate matching
-   [ ] Scoring
-   [ ] Tolerance handling
-   [ ] Explainability
-   [ ] Human review

### Engineering

-   [ ] Complete test suite
-   [ ] Docker
-   [ ] CI
-   [ ] Deployment
-   [ ] Final QA

------------------------------------------------------------------------

# 32. Start Here

If you are continuing development from a clean checkout:

``` bash
git clone git@github.com:SAHILDAS/financial-document-analyzer.git
cd financial-document-analyzer
```

### Start backend

``` bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --reload
```

### Start frontend

In a second terminal:

``` bash
cd financial-document-analyzer/frontend
npm install
npm start
```

Open:

``` text
http://localhost:4200
```

Verify:

``` text
Backend Connected
```

Then run the tests:

``` bash
cd financial-document-analyzer/backend
source .venv/bin/activate
pytest -v
```

Build the frontend:

``` bash
cd ../frontend
npm run build
```

------------------------------------------------------------------------

# 33. Documentation

Project documentation:

-   `ARCHITECTURE.md` --- system and component architecture
-   `API.md` --- API contracts and endpoint behavior
-   `SECURITY.md` --- security and privacy considerations
-   `DECISIONS.md` --- architectural decisions
-   `LIMITATIONS.md` --- prototype limitations
-   `DEMO.md` --- demonstration and presentation workflow

------------------------------------------------------------------------

# 34. Final Objective

The finished prototype should demonstrate a reliable end-to-end
workflow:

``` text
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

The project should demonstrate that AI can handle the difficult
unstructured-document understanding problem while conventional software
engineering remains responsible for validation, calculations, business
rules, reconciliation, and system reliability.

> **AI extracts. Engineering validates. Deterministic rules analyze.
> Explainability builds trust.**
