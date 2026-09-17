
````markdown
# Financial Document Analyzer — Architecture & Engineering Decisions

## 1. Purpose

This document records the major architectural and engineering decisions made while building the Financial Document Analyzer prototype.

The goal is to make important design choices:

- Explicit
- Explainable
- Reviewable
- Reproducible
- Easy to change later

The project intentionally favors a simple, modular architecture over unnecessary infrastructure complexity.

---

# 2. Decision Summary

| Area | Decision |
|---|---|
| Backend | Python + FastAPI |
| Frontend | Angular + TypeScript |
| API style | REST |
| Document formats | PDF, JPG/JPEG, PNG |
| Document classification | AI-assisted |
| OCR | Pluggable OCR service |
| Extraction | LLM structured extraction |
| Structured validation | Pydantic |
| Financial calculations | Deterministic Python logic |
| Reconciliation | Deterministic scoring |
| Persistence | Not required for initial prototype |
| Temporary document storage | Local temporary storage |
| Authentication | Out of prototype scope |
| Deployment | Simple prototype deployment |
| Containerization | Docker |
| Testing | Pytest + Angular tests |
| Documentation | Markdown + Mermaid |
| Messaging infrastructure | Not required |
| Redis | Not required |
| Kafka | Not required |
| Kubernetes | Not required |

---

# 3. ADR-001: Use Python for the Backend

## Decision

Use Python as the backend implementation language.

The API framework is:

```text
Python
   +
FastAPI
````

## Why

The project is document-intelligence and AI focused.

Python provides a strong ecosystem for:

* OCR
* PDF processing
* Image processing
* LLM SDKs
* Machine learning
* Data validation
* Numerical processing
* Document parsing

FastAPI also provides:

* Type hints
* Pydantic integration
* Automatic OpenAPI generation
* Async support
* Good developer experience
* Straightforward testing

## Alternatives Considered

### Node.js

Node.js is a strong choice for general backend systems and is familiar within the project ecosystem.

However, Python provides a more natural ecosystem for this particular document/AI workload.

### Java Spring Boot

Spring Boot would be appropriate for a large enterprise backend.

However, it would introduce additional complexity for the prototype without providing a significant advantage for the core document-intelligence functionality.

## Consequence

The backend is optimized for document and AI processing rather than demonstrating a particular enterprise Java stack.

---

# 4. ADR-002: Use Angular for the Frontend

## Decision

Use Angular with TypeScript.

Current foundation:

```text
Angular 22
TypeScript
SCSS
Standalone Components
```

## Why

The assignment requires a structured frontend capable of displaying:

* Document upload
* Processing status
* Extracted information
* Validation results
* Confidence
* Transactions
* Financial analysis
* Reconciliation
* Human-review states

Angular provides:

* Strong TypeScript integration
* Structured application architecture
* Routing
* Forms
* HTTP client
* Component-based UI
* Good maintainability for enterprise applications

## Alternatives Considered

### React

React would also be a suitable choice.

However, Angular provides more built-in application structure and is appropriate for demonstrating enterprise frontend engineering.

### Vue

Vue is also capable of implementing the required UI, but Angular was selected for the project requirements and intended enterprise context.

## Consequence

The frontend will be structured around Angular components, services, models, and routes.

---

# 5. ADR-003: Use REST Instead of GraphQL

## Decision

Use REST APIs for the prototype.

Primary API namespace:

```text
/api
```

Examples:

```text
GET  /api/health
POST /api/documents/analyze
POST /api/documents/salary-slip
POST /api/documents/bank-statement
POST /api/documents/reconcile
```

## Why

The frontend mainly performs explicit operations:

```text
Upload document
Analyze document
Display result
Reconcile data
```

These operations map naturally to REST endpoints.

FastAPI also provides excellent automatic OpenAPI documentation.

## Alternatives Considered

### GraphQL

GraphQL would be useful for highly dynamic client-driven data access.

However, the prototype does not require that flexibility.

### gRPC

gRPC would be useful for internal service-to-service communication.

The prototype does not require multiple independently deployed services.

## Consequence

The API remains simple and easy to test using:

* Swagger UI
* curl
* Postman
* Angular HttpClient

---

# 6. ADR-004: Use a Modular Monolith

## Decision

Build the application as a modular monolith.

Conceptually:

```text
FastAPI Application
       |
       +-- Ingestion
       +-- OCR
       +-- Classification
       +-- Extraction
       +-- Validation
       +-- Analysis
       +-- Reconciliation
```

These are logical modules rather than independently deployed microservices.

## Why

The assignment is a prototype with a short implementation timeline.

A modular monolith provides:

* Clear separation of responsibilities
* Simple deployment
* Simple local development
* Low operational overhead
* Easy debugging
* Easy testing

## Alternatives Considered

### Microservices

Microservices would introduce:

* Multiple deployments
* Service discovery
* Network communication
* Distributed tracing
* Configuration management
* More complicated local development

These are unnecessary for the prototype.

## Consequence

The architecture can later be decomposed into services if real scale or organizational requirements justify it.

---

# 7. ADR-005: Separate AI Extraction from Business Logic

## Decision

The LLM is used for extraction and interpretation, not as the source of truth for financial calculations.

Pipeline:

```text
Document
   |
   v
Text / OCR
   |
   v
LLM
   |
   v
Structured Data
   |
   v
Pydantic Validation
   |
   v
Deterministic Business Logic
```

## Why

LLMs are useful at interpreting semi-structured documents but should not be trusted for exact financial calculations.

For example:

```text
Gross Salary = ₹65,000
Deductions   = ₹6,000
Net Salary   = ₹59,000
```

The application should calculate:

```text
65000 - 6000 = 59000
```

rather than asking the LLM to calculate the result.

## Consequence

The system has a clear trust boundary:

```text
AI
  |
  | Extract
  v
Application
  |
  | Validate + Calculate
  v
Financial Result
```

This is one of the core architectural decisions of the project.

---

# 8. ADR-006: Use Pydantic for Structured Validation

## Decision

Use Pydantic models for structured financial data.

Examples:

```text
SalarySlip
BankStatement
Transaction
FinancialAnalysis
ReconciliationResult
ValidationResult
```

## Why

Pydantic provides:

* Runtime validation
* Type safety
* Explicit contracts
* JSON serialization
* FastAPI integration
* Clear validation errors

LLM output therefore has a defined contract before entering business logic.

## Consequence

Malformed extraction output can be rejected before it reaches financial analysis.

---

# 9. ADR-007: Use Schema Validation Before Financial Analysis

## Decision

Extracted data must pass schema validation before deterministic financial processing.

Pipeline:

```text
LLM Output
    |
    v
Pydantic
    |
    +---- Invalid ----> Validation Error
    |
    v
Valid Structured Data
    |
    v
Financial Analysis
```

## Why

Financial analysis assumes that the underlying data has a valid structure.

For example, a transaction should not simultaneously contain:

```text
debit = 10000
credit = 10000
```

The schema layer should reject such invalid structures.

---

# 10. ADR-008: Deterministic Financial Analysis

## Decision

Financial calculations and rule-based analysis are implemented in application code.

Examples:

```text
Total credits
Total debits
Large transactions
Salary-credit candidates
Recurring transactions
EMI candidates
```

## Why

These operations require predictable and testable behavior.

For example:

```text
total_credits = sum(transaction.credit)
```

can be unit tested exactly.

## Consequence

The system can explain how a financial result was derived.

---

# 11. ADR-009: Deterministic Reconciliation Scoring

## Decision

Salary-bank reconciliation uses deterministic scoring rather than asking an LLM to decide the match.

Conceptual weighting:

```text
Amount        50%
Date          25%
Narration     15%
Periodicity   10%
```

Formula:

```text
score =
    amount_score * 0.50
  + date_score * 0.25
  + narration_score * 0.15
  + periodicity_score * 0.10
```

## Why

Reconciliation should be:

* Explainable
* Repeatable
* Testable
* Configurable

## Consequence

The system can explain why a transaction was considered a candidate.

Example:

```text
Exact amount match
+
Date within tolerance
+
Salary-related narration
=
High-confidence candidate
```

The weights are implementation choices for this prototype and are not intended as a universal financial standard.

---

# 12. ADR-010: Do Not Force Unknown Documents Into Supported Categories

## Decision

The classifier may return:

```text
unknown
```

when a document cannot be confidently classified.

## Why

Forcing every document into:

```text
salary_slip
```

or:

```text
bank_statement
```

would create false positives.

## Consequence

The system can safely tell the user:

```text
Document could not be confidently classified.
```

instead of producing potentially misleading financial information.

---

# 13. ADR-011: Support Both Text-Based PDFs and Scanned Documents

## Decision

The processing pipeline supports:

```text
Text-based PDF
Scanned PDF
Image
```

with OCR used when required.

Pipeline:

```text
Document
   |
   +--> Extractable Text?
   |        |
   |        +--> Yes --> Text Extraction
   |        |
   |        +--> No ---> OCR
   |
   v
Classification
```

## Why

Real financial documents are not consistently machine-readable.

Some salary slips and bank statements are:

* Native PDFs
* Scanned documents
* Screenshots
* Image-based PDFs

## Consequence

OCR becomes a fallback/processing capability rather than the only extraction mechanism.

---

# 14. ADR-012: Provider Abstraction for OCR and LLM

## Decision

OCR and LLM integrations should be isolated behind service boundaries.

Conceptually:

```text
Application
    |
    +--> OCR Service
    |
    +--> LLM Extraction Service
```

Provider-specific code should not be spread throughout API routes and business logic.

## Why

This allows providers to be changed without rewriting the entire application.

For example:

```text
LLM Provider A
       |
       v
Extraction Service
       ^
       |
LLM Provider B
```

## Consequence

Provider configuration remains an infrastructure concern rather than a domain concern.

---

# 15. ADR-013: Temporary Document Processing

## Decision

The prototype uses temporary document storage rather than implementing a persistent document-management system.

## Why

The core assignment is document analysis, not document storage.

Temporary processing is sufficient for:

```text
Upload
   |
Process
   |
Return result
   |
Delete
```

## Consequence

The prototype has:

* Lower complexity
* Lower privacy exposure
* Easier local development
* Less infrastructure

A production implementation can introduce object storage and persistent metadata if required.

---

# 16. ADR-014: No Database for the Initial Processing Flow

## Decision

The minimum prototype does not require a database.

## Why

The core workflow can be executed synchronously:

```text
Upload
   |
Process
   |
Return result
```

A database would introduce:

* Schema management
* Migrations
* Persistent PII
* Backup requirements
* Access-control requirements

without being necessary for the initial demonstration.

## Future

A production implementation may persist:

```text
Document metadata
Processing status
Analysis results
Review decisions
Audit events
User information
```

---

# 17. ADR-015: Synchronous Processing for Prototype

## Decision

The initial implementation uses synchronous request processing.

Example:

```text
POST /api/documents/analyze
        |
        v
Process document
        |
        v
Return response
```

## Why

The prototype needs a simple end-to-end flow that is easy to demonstrate.

## Alternatives Considered

### Asynchronous Queue

A production architecture could use:

```text
API
 |
 v
Queue
 |
 v
Worker
 |
 v
Result Store
```

Potential technologies include:

```text
Redis
Kafka
RabbitMQ
Cloud queues
```

However, introducing a queue before it is required increases implementation complexity.

## Future

Async processing should be introduced if:

* Documents become large.
* OCR becomes slow.
* LLM processing becomes long-running.
* Concurrent processing increases.
* Users require progress tracking.

---

# 18. ADR-016: No Kafka or Redis in the Prototype

## Decision

Kafka and Redis are intentionally not part of the initial architecture.

## Why

Neither is required to demonstrate the core value of the application.

Adding infrastructure only because it is familiar would increase:

```text
Deployment complexity
Configuration
Debugging effort
Resource requirements
Development time
```

## Future

Kafka could become appropriate for:

```text
Document processing events
Audit events
Analytics pipelines
Asynchronous workflows
```

Redis could become appropriate for:

```text
Job state
Caching
Rate limiting
Distributed locks
Temporary processing state
```

These should be introduced only when justified by a concrete requirement.

---

# 19. ADR-017: No Kubernetes for Prototype Deployment

## Decision

Kubernetes is not required for the prototype.

## Why

The expected deployment footprint is small.

A simpler deployment can use:

```text
Angular
   +
FastAPI
```

with Docker where appropriate.

## Future

Kubernetes could become appropriate when the system requires:

* Multiple replicas
* Autoscaling
* Multi-service deployment
* Service discovery
* High availability
* Advanced rollout strategies

---

# 20. ADR-018: Use Docker for Reproducible Deployment

## Decision

Docker is planned for application packaging and reproducible deployment.

Conceptually:

```text
Docker
 |
 +--> Frontend
 |
 +--> Backend
```

## Why

Docker provides:

* Consistent runtime
* Reproducible builds
* Easier deployment
* Easier environment setup

The prototype does not require a complex container orchestration platform.

---

# 21. ADR-019: Use Environment Variables for Configuration

## Decision

Application configuration is provided through environment variables.

Examples:

```text
APP_NAME
APP_ENV
APP_DEBUG
BACKEND_HOST
BACKEND_PORT
FRONTEND_URL
LLM_PROVIDER
LLM_API_KEY
OCR_PROVIDER
MAX_FILE_SIZE_MB
```

## Why

Environment variables allow the same codebase to run in:

```text
Development
Testing
Staging
Production
```

without hard-coding environment-specific values.

---

# 22. ADR-020: Never Commit Secrets

## Decision

Secrets are excluded from source control.

Examples:

```text
.env
LLM API keys
OCR API keys
Database passwords
Private keys
Cloud credentials
```

The repository contains:

```text
.env.example
```

with safe placeholder configuration.

## Consequence

Developers can understand the required configuration without exposing credentials.

---

# 23. ADR-021: Synthetic Financial Data

## Decision

Only synthetic financial documents should be used for repository samples and automated tests.

## Why

The project processes sensitive financial information.

Using real salary slips or bank statements would create unnecessary privacy and security risk.

## Sample Data

Examples should use synthetic entities such as:

```text
Example Employee
Example Technologies
Example Bank
```

No real individual's financial information should be committed.

---

# 24. ADR-022: Structured Error Responses

## Decision

Expected failures use structured error responses.

Example:

```json
{
  "success": false,
  "error": {
    "code": "OCR_FAILED",
    "message": "The document could not be read."
  }
}
```

## Why

The frontend should not need to parse arbitrary exception messages.

Stable error codes allow Angular to implement predictable UI behavior.

---

# 25. ADR-023: Do Not Expose Internal Stack Traces

## Decision

Internal exceptions are logged appropriately but sanitized before being returned to clients.

Unsafe:

```text
Traceback...
/home/user/project/...
```

Safe:

```text
The document could not be processed.
```

## Why

Stack traces can expose:

* Filesystem paths
* Library versions
* Internal implementation
* Sensitive document content
* Configuration details

---

# 26. ADR-024: Explicit Human Review State

## Decision

The system supports a `needs_review` concept.

## Why

AI/document processing cannot always produce sufficiently reliable results.

Instead of forcing an answer:

```text
Low confidence
      |
      v
Human Review
```

## Examples

Human review may be appropriate when:

```text
Ambiguous classification
Missing salary values
Inconsistent salary arithmetic
Multiple reconciliation candidates
Weak salary-bank match
Poor OCR quality
```

## Consequence

The system acknowledges uncertainty rather than hiding it.

---

# 27. ADR-025: Explainable Analysis

## Decision

Important analytical results should include reasons where practical.

For example:

```json
{
  "candidate": "2026-08-31",
  "score": 0.94,
  "reasons": [
    "Exact salary amount match.",
    "Date is within configured tolerance.",
    "Narration contains salary-related indicator."
  ]
}
```

## Why

Financial analysis should not appear to be a black box.

Explainability is particularly important for:

* Reconciliation
* Salary detection
* Recurring transactions
* EMI candidates
* Validation warnings

---

# 28. ADR-026: Use Heuristics for Recurring Transactions

## Decision

Recurring transaction detection uses deterministic heuristics.

Signals include:

```text
Normalized narration
Similar amount
Repeated occurrences
Approximate intervals
Monthly periodicity
```

## Why

The task requires identifying recurring financial patterns, but a full machine-learning model is unnecessary for the prototype.

## Consequence

The implementation is:

* Explainable
* Testable
* Easy to modify

Results are described as probable patterns rather than absolute classifications.

---

# 29. ADR-027: Use Heuristics for EMI Detection

## Decision

EMI/loan candidates are identified using rule-based signals.

Examples:

```text
EMI keyword
Loan keyword
NACH
ECS
Recurring debit
Similar amount
Monthly frequency
Lender name
```

## Why

A deterministic prototype is sufficient to demonstrate the capability.

## Consequence

The API should use language such as:

```text
Likely EMI
Potential loan payment
EMI candidate
```

rather than claiming certainty.

---

# 30. ADR-028: Configurable Thresholds

## Decision

Important thresholds should be configurable where practical.

Example:

```text
MAX_FILE_SIZE_MB
```

Financial analysis thresholds such as:

```text
Large transaction threshold
Reconciliation date tolerance
Amount tolerance
Confidence thresholds
```

should not be unnecessarily hard-coded throughout business logic.

## Why

Business rules may change.

Centralizing configuration makes the system easier to maintain and test.

---

# 31. ADR-029: Confidence Is an Application Signal

## Decision

Confidence is represented as a normalized application-level score.

Suggested levels:

```text
0.85–1.00 -> High
0.65–0.84 -> Medium
0.00–0.64 -> Low
```

## Why

Users need a way to understand whether an extracted result requires additional review.

## Important Limitation

The confidence value is not a mathematically calibrated probability.

It is an implementation signal based on available evidence.

---

# 32. ADR-030: Field-Level Confidence as a Future Enhancement

## Decision

Overall confidence is implemented first.

Field-level confidence is a planned enhancement.

Example future structure:

```json
{
  "net_salary": {
    "value": 59000,
    "confidence": 0.97
  },
  "employee_name": {
    "value": "Example Employee",
    "confidence": 0.99
  }
}
```

## Why

Field-level confidence can help identify exactly which extracted values require review.

It is useful but not required for the minimum end-to-end prototype.

---

# 33. ADR-031: Source-Page Traceability as a Future Enhancement

## Decision

Source-page references are considered a bonus capability.

Future extraction output could include:

```json
{
  "field": "net_salary",
  "value": 59000,
  "source": {
    "page": 1
  }
}
```

## Why

Traceability would allow reviewers to quickly verify extracted values against the source document.

However, implementing reliable page-level provenance can add complexity to the initial extraction pipeline.

---

# 34. ADR-032: Testing Strategy

## Decision

Use automated tests at multiple levels.

Backend:

```text
pytest
```

Frontend:

```text
Angular test runner / Vitest
```

Testing priorities:

```text
Schema validation
File validation
Classification
Financial analysis
Reconciliation
API behavior
Error handling
```

## Why

The assignment requires demonstrating reliability rather than only producing a working happy path.

---

# 35. ADR-033: Test Financial Rules Independently

## Decision

Financial rules should be unit-testable without invoking the LLM.

Examples:

```text
calculate_total_credits()
calculate_total_debits()
find_large_transactions()
detect_recurring_transactions()
detect_salary_candidates()
detect_emi_candidates()
reconcile_salary_credit()
```

## Why

Tests should be:

* Fast
* Deterministic
* Cheap
* Reproducible

LLM calls should not be required to test arithmetic and business rules.

---

# 36. ADR-034: Documentation as Part of the Product

## Decision

Architecture and operational documentation are maintained inside the repository.

Core documentation:

```text
README.md
ARCHITECTURE.md
API.md
SECURITY.md
DECISIONS.md
LIMITATIONS.md
DEMO.md
```

Additional architecture documentation:

```text
docs/architecture/
docs/decisions/
docs/screenshots/
```

## Why

The assignment evaluates engineering ownership, not only code.

Documentation demonstrates:

* Design reasoning
* System boundaries
* Tradeoffs
* Security awareness
* Operational understanding

---

# 37. ADR-035: Mermaid for Architecture Diagrams

## Decision

Use Mermaid diagrams for architecture documentation where practical.

Example:

```mermaid
flowchart LR

    A[Angular] --> B[FastAPI]

    B --> C[Ingestion]
    C --> D[OCR / Text Extraction]
    D --> E[Classification]
    E --> F[LLM Extraction]
    F --> G[Pydantic Validation]
    G --> H[Financial Analysis]
    H --> I[Reconciliation]
```

## Why

Mermaid diagrams:

* Live in Git
* Are easy to edit
* Avoid binary diagram files
* Render on GitHub
* Keep architecture close to the code

---

# 38. ADR-036: No Premature Infrastructure

## Decision

Infrastructure should only be introduced when it solves a concrete requirement.

The prototype intentionally avoids introducing:

```text
Kafka
Redis
Kubernetes
CQRS
Event sourcing
Microservices
Distributed tracing
Complex service mesh
```

unless a clear technical reason emerges.

## Why

Complexity has a cost.

For this assignment, engineering quality is better demonstrated through:

```text
Correctness
Reliability
Explainability
Security
Testing
Maintainability
```

than through infrastructure quantity.

---

# 39. ADR-037: Prioritize End-to-End Functionality

## Decision

Implementation priority follows:

```text
1. Mandatory functionality
2. Extraction quality
3. Validation
4. Reconciliation
5. Error handling
6. Tests
7. Angular usability
8. Security/privacy
9. Documentation
10. Docker/CI/deployment
11. Bonus capabilities
12. Visual polish
```

## Why

A polished interface without a reliable backend does not demonstrate the core capability of the assignment.

---

# 40. ADR-038: Graceful Failure Over Fabricated Results

## Decision

When the system cannot reliably process a document, it should fail explicitly or request human review.

Examples:

```text
OCR failure
       |
       v
OCR_FAILED
```

```text
Unknown document
       |
       v
DOCUMENT_TYPE_UNKNOWN
```

```text
Ambiguous reconciliation
       |
       v
NEEDS_REVIEW
```

## Why

For financial documents, an explicit failure is safer than a plausible but incorrect answer.

---

# 41. ADR-039: Synchronous API First, Async Later

## Decision

Implement synchronous processing first.

The architecture should nevertheless keep processing responsibilities behind services so asynchronous processing can be introduced later.

Current:

```text
HTTP Request
     |
     v
Processing
     |
     v
HTTP Response
```

Possible future architecture:

```text
HTTP Request
     |
     v
Job Queue
     |
     v
Worker
     |
     v
Result Store
```

## Consequence

The prototype remains simple while preserving a path toward production scalability.

---

# 42. ADR-040: Keep Domain Models Independent of Provider Models

## Decision

Internal schemas such as:

```text
SalarySlip
BankStatement
Transaction
FinancialAnalysis
ReconciliationResult
```

are application-domain contracts.

They should not simply mirror an LLM provider's response format.

## Why

Provider APIs can change.

The application should own its domain model.

```text
LLM Provider Response
        |
        v
Adapter / Extraction Service
        |
        v
Application Domain Model
```

## Consequence

Changing LLM providers should not require changing the entire application.

---

# 43. ADR-041: API Routes Should Remain Thin

## Decision

FastAPI route handlers should coordinate requests rather than contain the complete processing logic.

Preferred:

```text
Route
  |
  v
Service
  |
  v
Domain Logic
```

Avoid:

```text
Route
  |
  +--> OCR
  +--> LLM
  +--> Validation
  +--> Financial calculations
  +--> Reconciliation
  +--> File cleanup
```

## Why

Thin routes improve:

* Testability
* Maintainability
* Separation of concerns
* Reusability

---

# 44. ADR-042: Business Rules Should Be Independently Testable

## Decision

Business logic should not depend directly on HTTP request objects.

For example:

```python
analyze_transactions(transactions)
```

should be testable without starting FastAPI.

Similarly:

```python
reconcile_salary(salary, transactions)
```

should be testable without uploading a document.

## Consequence

The system can have a strong unit-test suite around its most important financial behavior.

---

# 45. ADR-043: Avoid Persisting Raw OCR Text by Default

## Decision

Raw OCR output should remain transient unless there is an explicit requirement to retain it.

## Why

OCR output may contain:

```text
PAN
Account numbers
Salary
Transactions
Names
Addresses
```

Persisting it increases privacy and security exposure.

## Consequence

The prototype favors:

```text
OCR
 |
 v
Extraction
 |
 v
Structured result
 |
 v
Discard raw OCR
```

---

# 46. ADR-044: API Contract Before Full Implementation

## Decision

Core domain schemas and API contracts are defined before implementing the full processing pipeline.

## Why

This establishes a stable boundary between:

```text
Backend services
```

and:

```text
Angular frontend
```

It also allows backend and frontend work to proceed with known contracts.

## Consequence

The application can evolve internally while preserving a predictable external API.

---

# 47. ADR-045: Frontend Consumes API Contracts

## Decision

Angular should consume backend responses through typed frontend models/services rather than directly depending on backend implementation details.

Conceptually:

```text
Angular Component
       |
       v
Angular Service
       |
       v
HTTP API
       |
       v
FastAPI
```

## Why

This keeps components focused on presentation.

---

# 48. ADR-046: Health Endpoint for Operational Verification

## Decision

The backend provides:

```text
GET /api/health
```

## Why

It provides a simple way to verify:

```text
Backend running
API reachable
Frontend/backend connectivity
```

It is also useful for future deployment health checks.

---

# 49. ADR-047: Frontend-Backend Connectivity Before Feature UI

## Decision

The Angular application should establish backend connectivity before implementing the complete dashboard.

Current development flow:

```text
Angular
   |
   | GET /api/health
   v
FastAPI
   |
   v
Health Response
```

## Why

This validates the integration boundary early.

It prevents discovering basic networking/CORS/API issues after the complete UI has been built.

---

# 50. ADR-048: Feature Freeze Before Presentation

## Decision

A feature freeze should occur before the final presentation.

Target:

```text
September 21, 2026
```

After feature freeze:

```text
No major architectural changes
No major new features
```

Focus shifts to:

```text
Bug fixing
Testing
Deployment
Documentation
Demo preparation
Presentation rehearsal
```

## Why

Late architectural changes create unnecessary risk before the hiring-task presentation.

---

# 51. ADR-049: Optimize for Demonstrability

## Decision

The architecture should make the complete processing flow easy to demonstrate.

The final demo should be able to show:

```text
Upload
  ↓
Classification
  ↓
Extraction
  ↓
Validation
  ↓
Financial Analysis
  ↓
Reconciliation
  ↓
Confidence
  ↓
Human Review when necessary
```

## Why

The reviewer should be able to understand the value of the system during a short demonstration.

---

# 52. ADR-050: Core Engineering Principle

The most important architectural decision in this project is the separation between AI extraction and deterministic financial engineering.

```text
                  FINANCIAL DOCUMENT
                          |
                          v
                    OCR / TEXT
                          |
                          v
                    AI EXTRACTION
                          |
                          v
                  STRUCTURED DATA
                          |
                          v
                  SCHEMA VALIDATION
                          |
                          v
              DETERMINISTIC VALIDATION
                          |
                          v
                FINANCIAL ANALYSIS
                          |
                          v
                   RECONCILIATION
                          |
                          v
                 CONFIDENCE / REVIEW
```

The principle is:

> **The AI extracts information, but deterministic engineering controls decide whether the extracted information is trustworthy.**

This principle drives the architecture, validation strategy, testing strategy, security model, and reconciliation design.

---

# 53. Decision Review Policy

Architectural decisions should be revisited when:

* A new requirement makes the current decision insufficient.
* Performance requirements change.
* Data volume increases significantly.
* Security requirements change.
* Deployment requirements change.
* A concrete production constraint appears.

Decisions should not be changed merely because a more complex technology is available.

---

# 54. Current Architecture Direction

The current prototype direction is:

```text
                 +----------------------+
                 |   Angular Frontend   |
                 |      TypeScript      |
                 +----------+-----------+
                            |
                            | REST
                            v
                 +----------------------+
                 |    FastAPI Backend   |
                 +----------+-----------+
                            |
          +-----------------+-----------------+
          |                 |                 |
          v                 v                 v
      Ingestion       Processing          Analysis
          |                 |                 |
          |          +------+-------+         |
          |          |              |         |
          |         OCR       Classification  |
          |                         |         |
          |                         v         |
          |                     LLM Extractor |
          |                         |         |
          |                         v         |
          |                    Pydantic       |
          |                    Validation     |
          |                         |         |
          +-------------------------+---------+
                                    |
                                    v
                           Financial Analysis
                                    |
                                    v
                             Reconciliation
                                    |
                                    v
                              API Response
```

---

# 55. Final Decision Philosophy

The project intentionally follows:

```text
Simple architecture
        +
Strong contracts
        +
AI where AI provides value
        +
Deterministic logic where precision matters
        +
Explicit validation
        +
Explainability
        +
Security awareness
        +
Automated testing
```

The objective is not to build the largest possible architecture.

The objective is to build a system that is:

```text
Correct
Reliable
Understandable
Secure
Testable
Maintainable
Demonstrable
```

while preserving a clear path toward production evolution.

````
