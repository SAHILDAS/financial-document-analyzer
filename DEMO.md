
````markdown
# Financial Document Analyzer Prototype — Demo Guide

## 1. Purpose

This document defines the demonstration flow for the Financial Document Analyzer Prototype.

The goal of the demo is to show that the system can:

1. Accept financial documents.
2. Validate the uploaded file.
3. Extract text from digital or scanned documents.
4. Automatically classify the document.
5. Extract structured financial information using AI.
6. Validate the extracted information deterministically.
7. Analyze bank transactions using deterministic rules.
8. Identify likely salary credits, recurring transactions, and EMI/loan indicators.
9. Reconcile salary-slip net salary with bank salary credits.
10. Clearly communicate confidence, warnings, errors, and cases requiring human review.

The demo should emphasize the project's core engineering principle:

> **The AI extracts information, but deterministic engineering controls decide whether the extracted information is trustworthy.**

---

# 2. Demo Objective

The final demonstration should tell a clear technical story rather than simply showing a UI.

The intended flow is:

```text
Upload Document
       |
       v
File Validation
       |
       v
Text Extraction / OCR
       |
       v
Document Classification
       |
       v
Structured AI Extraction
       |
       v
Schema Validation
       |
       v
Deterministic Validation
       |
       v
Financial Analysis
       |
       v
Confidence + Warnings
       |
       v
Reconciliation
       |
       v
Human Review when Required
````

The demonstration should show both:

* successful processing
* graceful handling of imperfect input

---

# 3. Recommended Demo Scenario

The preferred demo uses synthetic financial documents.

No real personal financial information should be used.

Recommended demo set:

```text
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

If some fixtures are unavailable, use the closest available synthetic documents.

---

# 4. Demo Environment

The prototype should run locally during development and demonstration.

Expected components:

```text
Angular Frontend
       |
       | HTTP REST
       v
FastAPI Backend
       |
       +------------------+
       |                  |
       v                  v
Document Processing    LLM Provider
       |
       +------------------+
       |
       v
OCR / Text Extraction
```

Expected local URLs:

### Frontend

```text
http://localhost:4200
```

### Backend

```text
http://localhost:8000
```

### Backend health

```text
http://localhost:8000/api/health
```

### API documentation

```text
http://localhost:8000/docs
```

The actual port configuration should be taken from the project configuration if it changes.

---

# 5. Pre-Demo Checklist

Before starting the presentation, verify:

* [ ] Backend starts successfully.
* [ ] Frontend starts successfully.
* [ ] Backend health endpoint responds successfully.
* [ ] Frontend can communicate with backend.
* [ ] Required environment variables are configured.
* [ ] LLM provider/API configuration is working.
* [ ] OCR/text extraction dependencies are available.
* [ ] Sample documents are available.
* [ ] Database is not required for the demo unless explicitly introduced later.
* [ ] No real PII is present in sample documents.
* [ ] Browser console has no unexpected errors.
* [ ] Backend logs contain no secrets or sensitive document contents.
* [ ] Main happy-path flow has been tested immediately before the demo.

---

# 6. Demo Flow

## Step 1 — Introduce the Problem

Start with the problem rather than the implementation.

### Suggested explanation

Financial documents are usually semi-structured.

A salary slip from one organization may have a completely different layout from another organization's salary slip.

Bank statements can also vary significantly between banks.

The challenge is therefore not simply reading text.

The system needs to:

* understand the document type
* extract structured information
* validate the extracted information
* perform financial calculations
* identify relevant transactions
* reconcile information across documents
* communicate uncertainty

---

# 7. Step 2 — Show the Architecture

Open:

```text
ARCHITECTURE.md
```

Show the high-level architecture diagram.

Explain:

```text
Angular
   |
   v
FastAPI
   |
   +--> File Validation
   |
   +--> Text Extraction / OCR
   |
   +--> Classification
   |
   +--> AI Extraction
   |
   +--> Pydantic Validation
   |
   +--> Deterministic Validation
   |
   +--> Financial Analysis
   |
   +--> Reconciliation
```

### Key point

The LLM does not directly decide financial correctness.

The system separates:

```text
AI responsibilities
```

from:

```text
Deterministic business responsibilities
```

---

# 8. Step 3 — Upload a Salary Slip

Upload:

```text
samples/salary/salary_clean.pdf
```

The UI should display processing progress or status.

Expected processing stages:

```text
Uploading
   ↓
Validating file
   ↓
Extracting text
   ↓
Classifying document
   ↓
Extracting salary information
   ↓
Validating extracted data
   ↓
Analysis complete
```

---

# 9. Step 4 — Show Document Classification

The system should classify the document as:

```text
Salary Slip
```

Show:

```text
Document Type: Salary Slip
Confidence: High
```

If the implementation exposes classification confidence, display it.

The classification confidence should not be presented as a guarantee of correctness.

---

# 10. Step 5 — Show Extracted Salary Information

Display the extracted information in logical groups.

## Employee Information

Example:

```text
Employee Name
Employee ID
Employer
Salary Month
PAN
```

## Earnings

```text
Basic Salary
HRA
Allowances
Bonus / Incentive
Other Earnings
Gross Salary
```

## Deductions

```text
PF
Professional Tax
TDS
Other Deductions
Total Deductions
```

## Net Salary

```text
Net Salary
```

## Bank Information

If available:

```text
Bank Account Number
```

Sensitive information should be masked in the UI where appropriate.

For example:

```text
XXXXXXXX1234
```

rather than:

```text
123456789012
```

---

# 11. Step 6 — Demonstrate Deterministic Salary Validation

Show the salary calculation.

Example:

```text
Gross Salary
     -
Total Deductions
     =
Expected Net Salary
```

For example:

```text
Gross Salary        ₹75,000
Total Deductions     ₹8,500
                    -------
Expected Net        ₹66,500

Extracted Net       ₹66,500
```

The system should report:

```text
Validation: Passed
```

or an appropriate warning if the values are inconsistent.

### Important

This calculation must be performed by application logic.

The LLM should not be trusted to perform the final financial calculation.

---

# 12. Step 7 — Show Confidence and Validation

Display both:

```text
Confidence
```

and:

```text
Validation
```

These represent different concepts.

For example:

```text
Extraction Confidence: Medium

Validation:
✓ Required fields available
✓ Gross salary identified
✓ Deductions identified
✓ Net salary calculation consistent
```

Or:

```text
Extraction Confidence: Low

Validation:
⚠ Employee ID missing
⚠ Net salary does not reconcile with gross salary
⚠ Some deduction values were unclear
```

---

# 13. Step 8 — Upload a Bank Statement

Upload:

```text
samples/bank/bank_clean.pdf
```

Expected classification:

```text
Bank Statement
```

---

# 14. Step 9 — Show Bank Account Information

Display:

```text
Account Holder
Bank
Account Number
IFSC
Statement Start Date
Statement End Date
Opening Balance
Closing Balance
```

Mask sensitive account information where appropriate.

Example:

```text
Account Number: XXXXXXXX4321
```

---

# 15. Step 10 — Show Transactions

Display a transaction table.

Recommended columns:

| Date       | Narration       |   Debit |  Credit | Balance |
| ---------- | --------------- | ------: | ------: | ------: |
| 01/09/2026 | Opening Balance |       — |       — | ₹20,000 |
| 02/09/2026 | Salary Credit   |       — | ₹66,500 | ₹86,500 |
| 05/09/2026 | EMI PAYMENT     | ₹18,000 |       — | ₹68,500 |
| 10/09/2026 | Utility Payment |  ₹2,500 |       — | ₹66,000 |

The exact values should come from the synthetic sample.

---

# 16. Step 11 — Demonstrate Transaction Analysis

Show deterministic financial metrics.

## Total Credits

```text
Total Credits = Sum of all credit transactions
```

## Total Debits

```text
Total Debits = Sum of all debit transactions
```

## Large Transactions

Display transactions above:

```text
₹50,000
```

Example:

```text
Large Transactions

₹75,000 credit
₹1,00,000 debit
```

The threshold should be configurable.

---

# 17. Step 12 — Demonstrate Salary Credit Detection

The system should identify possible salary credits.

Example:

```text
Possible Salary Credit

Date: 02/09/2026
Amount: ₹66,500
Narration: SALARY ABC COMPANY
Confidence: High
```

The detection can use signals such as:

* narration keywords
* transaction amount
* recurring monthly pattern
* proximity to expected salary amount
* credit direction

The system should describe this as:

```text
Likely Salary Credit
```

rather than an absolute fact when the evidence is heuristic.

---

# 18. Step 13 — Demonstrate Recurring Transactions

Show recurring transaction candidates.

Example:

```text
Recurring Transactions

1. Rent
   Amount: approximately ₹20,000
   Frequency: Monthly

2. Insurance
   Amount: approximately ₹2,500
   Frequency: Monthly
```

The detection is heuristic.

Signals may include:

* normalized narration
* similar transaction amount
* repeated occurrences
* approximate time interval

---

# 19. Step 14 — Demonstrate EMI / Loan Detection

Show a likely EMI transaction.

Example:

```text
Likely EMI / Loan Transaction

Amount: ₹18,000
Narration: ABC BANK EMI
Frequency: Monthly
Confidence: Medium
```

Potential signals:

* EMI keywords
* loan keywords
* NACH/ECS indicators
* recurring debit
* similar amounts
* monthly periodicity

The UI should use language such as:

```text
Likely EMI
```

or:

```text
Possible Loan Repayment
```

rather than claiming certainty.

---

# 20. Step 15 — Demonstrate Reconciliation

This is one of the most important parts of the demonstration.

Use:

```text
Salary Slip
+
Bank Statement
```

The system compares:

```text
Salary Slip Net Salary
```

against:

```text
Bank Credit Transactions
```

---

# 21. Reconciliation Example

Suppose:

```text
Salary Slip Net Salary:
₹66,500
```

Bank statement contains:

```text
02/09/2026
SALARY ABC COMPANY
₹66,500 Credit
```

The system should produce something similar to:

```text
Reconciliation Result

Status: MATCHED

Salary Slip Amount: ₹66,500
Bank Credit Amount: ₹66,500

Date Difference: 0 days

Amount Difference: ₹0

Confidence: High
```

---

# 22. Reconciliation Explanation

Show an explainable reason.

Example:

```text
Why this matched:

✓ Amount matches exactly
✓ Transaction is a credit
✓ Transaction date is within tolerance
✓ Narration contains salary-related information
✓ Transaction pattern is consistent with salary payment
```

This is important because the user should understand why the system reached the result.

---

# 23. Reconciliation Scoring

If the UI exposes the score, show the components.

Example:

```text
Amount Match       50%
Date Match         25%
Narration Match    15%
Periodicity        10%
------------------------
Total Score       100%
```

These weights are implementation choices for the prototype.

They should be configurable rather than treated as universal financial standards.

---

# 24. Multiple Candidate Scenario

Demonstrate a case where multiple bank credits could potentially match the salary.

Example:

```text
Salary Slip Net Salary:
₹66,500
```

Bank statement:

```text
02/09/2026   SALARY COMPANY       ₹66,500
15/09/2026   TRANSFER             ₹66,500
```

The system should not silently choose a transaction without considering the available evidence.

Expected behavior:

```text
Multiple Possible Matches

Candidate 1
Score: High

Candidate 2
Score: Medium

Recommendation:
Human Review Required
```

The exact UI representation may vary.

---

# 25. No-Match Scenario

Demonstrate a salary slip where no corresponding bank credit exists.

Example:

```text
Salary Slip Net Salary:
₹66,500
```

Bank statement:

```text
No matching credit found
```

Expected result:

```text
Status: NOT_MATCHED

Reason:
No bank credit satisfied the configured reconciliation criteria.

Action:
Human review recommended.
```

The system should not fabricate a match.

---

# 26. Low-Confidence Scenario

Upload:

```text
samples/salary/salary_scan.pdf
```

or another difficult/poor-quality document.

Expected behavior:

```text
Document Type: Salary Slip

Confidence: Low

Warnings:
⚠ Some text could not be confidently extracted.
⚠ Several salary fields require review.

Status:
NEEDS_REVIEW
```

The important behavior is graceful degradation.

The application should not pretend that uncertain extraction is reliable.

---

# 27. Missing Fields Scenario

Upload:

```text
samples/salary/salary_missing_fields.pdf
```

Expected behavior:

```text
Salary Information

Employee Name: Available
Employee ID: Missing
Employer: Available
Gross Salary: Available
Net Salary: Available
PAN: Not Available
```

Warnings:

```text
⚠ Employee ID was not found.
⚠ PAN was not found.
```

Missing optional fields should not necessarily fail the entire document.

---

# 28. Inconsistent Salary Scenario

Upload:

```text
samples/salary/salary_inconsistent.pdf
```

Expected behavior:

```text
Validation Warning

Gross Salary:
₹75,000

Total Deductions:
₹8,500

Expected Net:
₹66,500

Extracted Net:
₹65,500

Difference:
₹1,000
```

The application should mark the result appropriately:

```text
NEEDS_REVIEW
```

or another configured validation status.

This demonstrates that the system does not blindly trust AI output.

---

# 29. Duplicate Transaction Scenario

Upload:

```text
samples/bank/bank_duplicate_transactions.pdf
```

The system should identify potential duplicate transactions if duplicate detection is implemented.

Example:

```text
Potential Duplicate

Date: 10/09/2026
Amount: ₹5,000
Narration: ABC PAYMENT

Similar transaction:
Date: 10/09/2026
Amount: ₹5,000
Narration: ABC PAYMENT
```

The UI should describe this as:

```text
Potential Duplicate
```

rather than definitively declaring fraud or an accounting error.

---

# 30. Unknown Document Scenario

Upload:

```text
samples/invalid/unknown_document.pdf
```

Expected behavior:

```text
Document Type:
Unknown / Unsupported

Message:
The uploaded document could not be confidently classified as a supported financial document.
```

The application should provide a useful user-facing error or warning.

---

# 31. Unsupported File Scenario

Upload:

```text
samples/invalid/unsupported.txt
```

Expected result:

```text
Unsupported File

Supported formats:
PDF
JPG / JPEG
PNG
```

The application should reject the file before unnecessary processing.

---

# 32. Error Handling Demo

Demonstrate at least one graceful error.

Possible scenarios:

```text
Unsupported file
```

or:

```text
Unreadable document
```

or:

```text
OCR failure
```

or:

```text
LLM provider unavailable
```

Expected UI:

```text
Unable to process this document.

Error Code:
DOCUMENT_PROCESSING_FAILED

Please verify the document and try again.
```

The UI should not display:

```text
Traceback ...
```

or internal stack traces.

---

# 33. Security / Privacy Demonstration

Briefly show:

```text
SECURITY.md
```

Explain:

* financial documents contain sensitive information
* temporary files should have a controlled lifecycle
* raw OCR text should not be unnecessarily logged
* PAN and account numbers should be masked
* API keys must be stored in environment variables
* external AI/OCR providers may receive document-derived data
* retention and deletion behavior must be documented
* production deployments require stronger authentication and authorization

Do not display real financial data during the presentation.

---

# 34. API Demonstration

Open:

```text
http://localhost:8000/docs
```

Show the available endpoints.

Expected core endpoints:

```text
GET  /api/health
POST /api/documents/analyze
POST /api/documents/salary-slip
POST /api/documents/bank-statement
POST /api/documents/reconcile
```

If only the health endpoint is currently implemented during an intermediate development stage, demonstrate the implemented endpoint and explain the remaining planned endpoints.

---

# 35. Backend Demonstration

If additional technical depth is appropriate, show the backend structure.

Example:

```text
backend/app/

api/
core/
schemas/
services/
    ingestion/
    classification/
    ocr/
    extraction/
    validation/
    analysis/
    reconciliation/
utils/
```

Explain the separation of responsibilities.

The important architectural point is:

```text
Routes
   ↓
Services
   ↓
Domain Schemas / Rules
```

rather than putting the entire workflow inside one API controller.

---

# 36. Frontend Demonstration

The Angular application should demonstrate:

```text
Upload
  ↓
Processing
  ↓
Document Overview
  ↓
Extracted Information
  ↓
Validation
  ↓
Financial Analysis
  ↓
Reconciliation
```

Recommended UI sections:

```text
Dashboard / Overview

Document Classification
Confidence

Extracted Information

Validation Results

Financial Summary

Transactions

Salary Credit Detection

Recurring Transactions

EMI / Loan Indicators

Reconciliation

Warnings / Human Review
```

---

# 37. Recommended Demo Screen Layout

A useful final analysis screen can be structured as:

```text
+------------------------------------------------------+
| Document Analysis                                    |
+------------------------------------------------------+
| Document Type | Confidence | Processing Status       |
+------------------------------------------------------+
| Extracted Information                                |
|                                                      |
| Employee / Account Information                       |
|                                                      |
+------------------------------------------------------+
| Validation                                            |
| ✓ Gross salary validated                             |
| ✓ Net salary calculation consistent                  |
+------------------------------------------------------+
| Financial Summary                                    |
|                                                      |
| Total Credits | Total Debits | Large Transactions    |
+------------------------------------------------------+
| Transactions                                         |
|                                                      |
| Date | Narration | Debit | Credit | Balance          |
+------------------------------------------------------+
| Insights                                             |
|                                                      |
| Salary Credit | Recurring | EMI / Loan              |
+------------------------------------------------------+
| Reconciliation                                       |
|                                                      |
| Salary | Bank Credit | Match | Confidence            |
+------------------------------------------------------+
```

The exact visual design can evolve.

---

# 38. Recommended Presentation Narrative

The presentation should follow this sequence:

### 1. Problem

```text
Financial documents are semi-structured and difficult to process consistently.
```

### 2. Solution

```text
A document intelligence pipeline converts documents into structured,
validated financial information.
```

### 3. AI Usage

```text
AI is used for classification and extraction.
```

### 4. Engineering Controls

```text
Pydantic validation and deterministic business rules validate the result.
```

### 5. Financial Analysis

```text
The system analyzes transactions and derives explainable indicators.
```

### 6. Reconciliation

```text
Salary-slip information is reconciled against bank transactions.
```

### 7. Confidence

```text
Uncertain results are surfaced instead of silently accepted.
```

### 8. Reliability

```text
The application handles unsupported, malformed, incomplete, and
low-quality documents gracefully.
```

### 9. Security

```text
Financial data is treated as sensitive information.
```

### 10. Future Evolution

```text
The prototype can evolve into an asynchronous production architecture
with authentication, persistence, object storage, workers,
observability, and auditability.
```

---

# 39. What the Demo Should Prove

The demo should prove the following capabilities:

| Capability          | Demonstration                 |
| ------------------- | ----------------------------- |
| File upload         | Upload PDF/image              |
| File validation     | Reject unsupported files      |
| OCR                 | Process scanned document      |
| Classification      | Salary vs Bank vs Unknown     |
| Salary extraction   | Structured salary information |
| Bank extraction     | Account + transactions        |
| Schema validation   | Pydantic/domain validation    |
| Salary validation   | Gross - deductions ≈ net      |
| Transaction totals  | Credits/debits                |
| Large transactions  | > ₹50,000                     |
| Salary detection    | Possible salary credit        |
| Recurring detection | Repeated transactions         |
| EMI detection       | Likely EMI/loan               |
| Reconciliation      | Salary ↔ bank credit          |
| Explainability      | Match reasons                 |
| Confidence          | High/Medium/Low               |
| Human review        | Low-confidence cases          |
| Error handling      | Graceful failures             |
| Security            | PII/logging/privacy controls  |

---

# 40. Demo Success Criteria

The prototype should be considered demo-ready when the following are true:

* [ ] A salary document can be uploaded.
* [ ] A bank statement can be uploaded.
* [ ] Documents are classified.
* [ ] Structured data is extracted.
* [ ] Extracted data passes schema validation.
* [ ] Salary calculations are deterministic.
* [ ] Bank transaction totals are deterministic.
* [ ] Large transactions are identified.
* [ ] Possible salary credits are identified.
* [ ] Recurring transactions are identified.
* [ ] EMI/loan indicators are identified.
* [ ] Salary and bank information can be reconciled.
* [ ] Reconciliation provides an explainable result.
* [ ] Confidence is visible.
* [ ] Low-confidence cases can be flagged for review.
* [ ] Unsupported documents fail gracefully.
* [ ] Invalid input does not expose stack traces.
* [ ] Sensitive values are appropriately masked.
* [ ] Backend tests pass.
* [ ] Frontend builds successfully.
* [ ] End-to-end happy path works.
* [ ] Documentation is complete enough for the evaluator to understand the architecture.

---

# 41. Demo Failure Recovery

If an external LLM/OCR provider fails during the presentation:

1. Show the error handling behavior.
2. Explain that external AI services are dependencies.
3. Switch to a known-good local/sample flow if available.
4. Do not manually fabricate results.
5. Do not hide a failed processing step.

Recommended fallback:

```text
Demo sample → prevalidated synthetic document
```

The fallback should still execute the application's normal processing path whenever possible.

---

# 42. What Not to Demonstrate

Avoid spending presentation time on:

* Kubernetes
* Kafka
* Redis
* microservice orchestration
* complex cloud infrastructure
* unnecessary DevOps infrastructure
* excessive UI animation
* internal implementation details that do not support the problem
* unsupported production claims

These are outside the primary prototype objective unless they become necessary later.

---

# 43. Technical Questions the Evaluator May Ask

## Why use an LLM?

Because financial documents are semi-structured and their layouts vary.

An LLM can help map extracted document text into a normalized schema.

However, the LLM is not trusted for final financial calculations or reconciliation decisions.

---

## Why not use the LLM for calculations?

Financial calculations should be deterministic and reproducible.

For example:

```text
gross_salary - total_deductions
```

can and should be calculated by application code.

This reduces the risk of arithmetic errors and makes the behavior testable.

---

## How do you validate LLM output?

Use multiple layers:

```text
LLM Output
    ↓
Pydantic Schema Validation
    ↓
Field Validation
    ↓
Cross-field Validation
    ↓
Deterministic Financial Rules
```

---

## How do you handle poor OCR?

The system should:

1. detect extraction quality problems
2. lower confidence
3. generate validation warnings
4. avoid presenting uncertain data as authoritative
5. flag the result for human review

---

## How do you reconcile salary with a bank statement?

Compare the salary-slip net amount against candidate bank credits using multiple signals:

```text
Amount
Date
Narration
Periodicity
```

Candidates are scored using configurable prototype weights.

The result should include an explanation and confidence.

---

## What happens when there are multiple matching transactions?

The system should retain multiple candidates rather than silently selecting one when the evidence is ambiguous.

If the difference is not sufficiently clear:

```text
NEEDS_REVIEW
```

---

## What happens if no transaction matches?

Return:

```text
NOT_MATCHED
```

and explain that no transaction satisfied the configured reconciliation criteria.

Do not fabricate a match.

---

## Can this detect fraud?

Not reliably.

The prototype may identify suspicious or unusual patterns, but this is not equivalent to a fraud determination.

Fraud detection would require additional data, domain-specific rules, historical behavior, and potentially dedicated models and investigation workflows.

---

## Can this be used in production?

The prototype demonstrates the core processing and analysis workflow.

A production system would require additional controls such as:

* authentication
* authorization
* persistent storage
* encrypted object storage
* audit logging
* stronger PII controls
* rate limiting
* asynchronous processing
* monitoring
* alerting
* retry mechanisms
* provider failover
* data retention policies
* compliance controls
* high availability
* disaster recovery

---

# 44. Final Demo Message

End the demonstration with the core engineering principle:

> **The goal is not to make the LLM decide everything.**
>
> **The goal is to use AI where unstructured understanding is valuable, and deterministic engineering where correctness matters.**

The resulting architecture is:

```text
AI
 ↓
Extraction

Deterministic Engineering
 ↓
Validation
 ↓
Analysis
 ↓
Reconciliation
 ↓
Confidence
 ↓
Human Review
```

This separation makes the prototype:

* explainable
* testable
* easier to debug
* safer for financial workflows
* easier to evolve toward production

---

# 45. Final Presentation Checklist

Before presenting:

## Application

* [ ] Backend running
* [ ] Frontend running
* [ ] Health endpoint working
* [ ] Upload working
* [ ] Salary flow working
* [ ] Bank flow working
* [ ] Reconciliation working

## AI / Document Processing

* [ ] Classification tested
* [ ] Extraction tested
* [ ] OCR tested
* [ ] Low-confidence behavior tested
* [ ] Unknown document tested

## Financial Logic

* [ ] Salary validation tested
* [ ] Credit/debit totals tested
* [ ] Large transaction detection tested
* [ ] Salary credit detection tested
* [ ] Recurring transaction detection tested
* [ ] EMI detection tested
* [ ] Reconciliation tested
* [ ] Multiple candidate case tested
* [ ] No-match case tested

## Security

* [ ] No real PII in samples
* [ ] Secrets not committed
* [ ] Sensitive logging disabled/masked
* [ ] Account numbers masked
* [ ] PAN masked if displayed
* [ ] Temporary files cleaned up

## Quality

* [ ] Backend tests passing
* [ ] Frontend build passing
* [ ] No obvious browser errors
* [ ] No obvious backend errors
* [ ] Error states tested
* [ ] Documentation reviewed

## Presentation

* [ ] Architecture diagram ready
* [ ] Demo documents ready
* [ ] Main happy path rehearsed
* [ ] Failure path rehearsed
* [ ] Reconciliation explanation rehearsed
* [ ] Security explanation rehearsed
* [ ] Production evolution explanation rehearsed
* [ ] No major feature changes immediately before presentation

---

# 46. Recommended 8–10 Minute Demo

If the evaluator gives limited time, use this sequence:

```text
00:00 - 01:00
Problem + architecture

01:00 - 02:30
Upload salary slip

02:30 - 04:00
Show extraction + validation

04:00 - 05:30
Upload bank statement

05:30 - 07:00
Show transaction analysis

07:00 - 08:30
Show salary-bank reconciliation

08:30 - 09:30
Show low-confidence / error handling

09:30 - 10:00
Security + production evolution
```

The most important portion should be:

```text
Extraction
    +
Validation
    +
Financial Analysis
    +
Reconciliation
```

rather than visual UI polish.

---

# 47. Final Prototype Story

The complete story of the project is:

```text
Financial Document
        |
        v
     Ingestion
        |
        v
 Text Extraction / OCR
        |
        v
  Classification
        |
        v
 AI Structured Extraction
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
 Confidence + Explainability
        |
        v
 Human Review
```

The prototype demonstrates how AI and conventional software engineering can be combined without allowing an LLM to become the source of truth for financial correctness.

````
