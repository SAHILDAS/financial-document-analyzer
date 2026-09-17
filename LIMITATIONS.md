````markdown
# Financial Document Analyzer — Limitations

## 1. Purpose

This document describes the known limitations of the Financial Document Analyzer prototype.

The purpose is to clearly distinguish:

- Implemented prototype capabilities
- Known limitations
- Assumptions
- Areas requiring human review
- Production requirements
- Future enhancements

The application is designed to demonstrate an end-to-end financial document intelligence workflow.

It is **not** intended to be a production banking, accounting, lending, fraud-detection, or regulatory-compliance system.

---

# 2. Prototype Scope

The prototype focuses on:

```text
Document Upload
       |
       v
Text Extraction / OCR
       |
       v
Document Classification
       |
       v
Structured Extraction
       |
       v
Validation
       |
       v
Financial Analysis
       |
       v
Salary-Bank Reconciliation
       |
       v
Confidence / Human Review
````

The prototype prioritizes correctness, explainability, and demonstrability over enterprise-scale infrastructure.

---

# 3. Document Format Limitations

Currently supported formats are:

```text
PDF
JPG
JPEG
PNG
```

The prototype does not target every possible financial document format.

Examples outside the initial scope include:

```text
DOC
DOCX
XLS
XLSX
CSV
ZIP
Encrypted archives
Specialized banking formats
```

Support for additional formats may be added later.

---

# 4. Document Layout Limitations

Financial institutions use many different document layouts.

Salary slips may vary in:

* Field names
* Table structure
* Position of values
* Fonts
* Headers
* Employer-specific terminology
* Earnings categories
* Deduction categories

Bank statements may vary in:

* Transaction table structure
* Date formats
* Debit/credit representation
* Balance representation
* Narration formatting
* Multi-page layout
* Column ordering

The extraction system may therefore perform differently across previously unseen layouts.

---

# 5. OCR Limitations

OCR accuracy depends on document quality.

Potential problems include:

```text
Low-resolution scans
Blurred documents
Skewed pages
Poor lighting
Small fonts
Handwritten information
Overlapping text
Stamps
Watermarks
Complex tables
Low-contrast documents
```

OCR may produce incorrect characters or numbers.

For financial documents, even a single incorrect character can be significant.

Examples:

```text
59000
```

being interpreted as:

```text
590000
```

or:

```text
123456789012
```

being interpreted incorrectly.

Therefore OCR output should never automatically be considered authoritative.

---

# 6. Scanned PDF Limitations

A scanned PDF may contain only images rather than machine-readable text.

The system can use OCR as a fallback, but:

```text
OCR quality
+
Document quality
+
Table complexity
```

can affect extraction quality.

Very poor scans may require manual review.

---

# 7. Password-Protected Document Limitation

Password-protected documents may not be processable without the required password.

The application should return a controlled error such as:

```text
PASSWORD_PROTECTED_DOCUMENT
```

rather than attempting to bypass document protection.

---

# 8. Classification Limitations

The initial classifier focuses on:

```text
salary_slip
bank_statement
unknown
```

This means the system is not designed to distinguish every type of financial document.

Examples outside the primary classification scope include:

```text
Tax forms
Invoices
Credit-card statements
Loan statements
Investment statements
Insurance documents
Mutual-fund statements
Property documents
```

Such documents may be classified as:

```text
unknown
```

or otherwise rejected.

---

# 9. Classification Confidence Limitation

Classification confidence is an application-level signal.

It is not a mathematically calibrated probability.

For example:

```text
0.94
```

should not be interpreted as:

```text
"There is exactly a 94% probability that this document is a salary slip."
```

It represents the application's confidence based on the available evidence and implementation logic.

---

# 10. LLM Extraction Limitations

LLMs are probabilistic systems.

Possible extraction problems include:

```text
Missing fields
Incorrect field mapping
Incorrect numbers
Incorrect dates
Incorrect interpretation of labels
Hallucinated values
Malformed structured output
Confusion between similar fields
```

Therefore:

> LLM output is treated as an extraction proposal, not financial truth.

---

# 11. LLM Does Not Determine Financial Truth

The architecture deliberately avoids using the LLM as the final authority for financial calculations.

For example:

```text
Gross Salary
       -
Total Deductions
       =
Expected Net Salary
```

is calculated by deterministic application logic.

The same principle applies to:

```text
Total credits
Total debits
Large transactions
Reconciliation scores
```

This reduces the impact of model calculation errors.

---

# 12. Salary Extraction Limitations

Salary slips can contain employer-specific structures.

The prototype may not reliably recognize every possible:

```text
Earning component
Deduction component
Allowance
Bonus
Reimbursement
Tax component
Employer contribution
Employee contribution
```

If a field cannot be reliably extracted, the system should represent it as missing or uncertain rather than inventing a value.

---

# 13. Salary Validation Limitations

The basic salary validation checks relationships such as:

```text
Gross - Total Deductions ≈ Net Salary
```

However, real payroll calculations can contain additional components.

For example:

```text
Employer contributions
Arrears
Adjustments
Reimbursements
Tax corrections
Rounding
Other payroll-specific calculations
```

Therefore a mathematically inconsistent salary slip is not automatically proof that the source document is fraudulent or incorrect.

It indicates that the extracted information requires investigation.

---

# 14. Approximate Financial Matching

Some financial relationships naturally involve tolerances.

For example:

```text
Salary Slip Net = ₹59,000
Bank Credit    = ₹59,000
```

is an exact match.

But:

```text
Salary Slip Net = ₹59,000
Bank Credit    = ₹58,950
```

may still require consideration depending on the business context.

The prototype therefore uses configurable matching logic rather than requiring every amount to be identical.

---

# 15. Bank Statement Limitations

Bank statements can use different representations for:

```text
Debit
Credit
Balance
Transaction date
Value date
Posting date
Narration
Reference number
```

The prototype's normalized transaction model may not capture every field available in a real bank statement.

The core transaction model focuses on:

```text
date
narration
debit
credit
balance
```

Additional banking metadata may be added later.

---

# 16. Transaction Parsing Limitations

Complex transaction tables can be difficult to parse.

Potential problems include:

```text
Rows split across pages
Wrapped narrations
Repeated headers
Missing balances
Merged columns
Different debit/credit conventions
Transactions spanning multiple lines
```

These conditions can result in incomplete or incorrectly reconstructed transactions.

Such results should be surfaced through validation or confidence signals.

---

# 17. Duplicate Transaction Limitation

Bank statements may contain duplicated-looking transactions.

Two transactions can legitimately have:

```text
Same date
Same amount
Similar narration
```

Therefore identical-looking transactions should not automatically be treated as duplicates.

A more advanced duplicate-detection system would consider additional attributes such as:

```text
Reference number
Transaction identifier
Exact timestamp
Sequence
Source-page position
```

The prototype may only provide basic duplicate indicators.

---

# 18. Recurring Transaction Limitations

Recurring transaction detection uses heuristics.

Signals may include:

```text
Similar narration
Similar amount
Repeated occurrences
Approximate intervals
Monthly periodicity
```

This does not prove that a transaction represents a contractual recurring payment.

For example, repeated:

```text
₹10,000
```

transactions could represent:

```text
Rent
Transfer
Investment
Family support
Loan payment
Savings movement
```

Therefore the system should describe recurring patterns as potential or likely patterns.

---

# 19. EMI / Loan Detection Limitations

EMI detection is heuristic.

Possible signals include:

```text
EMI
LOAN
NACH
ECS
Recurring debit
Similar amount
Monthly frequency
Lender name
```

However, a transaction containing the word:

```text
EMI
```

does not by itself prove that it is a valid loan repayment.

Similarly, a recurring debit does not necessarily represent an EMI.

The output should therefore use language such as:

```text
Likely EMI
Potential loan payment
EMI candidate
```

rather than definitive statements.

---

# 20. Salary Credit Detection Limitations

Salary-credit detection is also heuristic.

Possible signals include:

```text
Salary-related narration
Amount similarity
Employer-name similarity
Recurring monthly pattern
Expected salary date
Credit transaction type
```

However, other transactions can resemble salary credits.

For example:

```text
Freelance payment
Business income
Family transfer
Bonus
Refund
Large personal transfer
```

may look similar to salary income.

Therefore the system identifies **salary-credit candidates**, not confirmed salary payments.

---

# 21. Reconciliation Limitations

The reconciliation engine compares salary information with bank transactions.

The conceptual factors are:

```text
Amount
Date
Narration
Periodicity
```

with prototype weighting:

```text
Amount        50%
Date          25%
Narration     15%
Periodicity   10%
```

These weights are implementation choices for the prototype.

They are not a universal financial standard.

---

# 22. Multiple Candidate Limitation

A salary slip may match multiple bank transactions.

Example:

```text
Salary = ₹59,000

Transaction A = ₹59,000
Transaction B = ₹59,000
Transaction C = ₹58,950
```

The system should not arbitrarily hide the ambiguity.

Possible result:

```text
multiple_candidates
```

or:

```text
needs_review
```

A human may need to determine which transaction represents the salary payment.

---

# 23. No-Match Limitation

A salary slip may not have a matching transaction in the supplied bank statement.

Possible reasons include:

```text
Statement does not cover salary date
Salary paid into another account
Salary amount changed
Salary credit has different narration
Salary credit is outside tolerance
Bank statement is incomplete
Salary was paid manually
Document extraction is incorrect
```

Therefore:

```text
no_match
```

does not prove that salary was not received.

It means that no sufficiently strong candidate was identified within the available data.

---

# 24. Confidence Limitations

Confidence is not certainty.

A high confidence result can still be incorrect.

Similarly, a low confidence result can sometimes be correct.

The confidence system exists to:

```text
Prioritize review
Communicate uncertainty
Support explainability
```

It should not be interpreted as a guarantee.

---

# 25. Human Review Limitation

The prototype can identify cases requiring review, but it does not implement a complete enterprise human-review workflow.

A production system could include:

```text
Review queue
Reviewer assignment
Approval/rejection
Correction of extracted values
Reviewer comments
Audit trail
Review history
Escalation
```

These are future capabilities.

---

# 26. No Fraud Determination

The application may identify:

```text
Inconsistent salary arithmetic
Unusual transactions
Large transactions
Duplicate-looking transactions
Unexpected patterns
Low-confidence extraction
```

However, these signals do **not** establish fraud.

The prototype should not claim:

```text
"This document is fraudulent."
```

based solely on heuristic analysis.

A proper fraud-detection system would require additional:

```text
Evidence
Rules
Historical data
Tamper detection
Identity verification
Domain-specific controls
Human investigation
```

---

# 27. No Tamper Detection

The prototype does not provide a complete document-authenticity system.

It does not guarantee detection of:

```text
Photoshop edits
PDF modifications
Screenshot manipulation
Font replacement
Image manipulation
Metadata manipulation
Digital forgery
```

A future implementation could introduce dedicated document-forensics capabilities.

---

# 28. No Regulatory Certification

The prototype is not certified for:

```text
Banking compliance
Accounting compliance
Financial reporting
KYC
AML
Credit underwriting
Regulatory reporting
```

It should not be used as a compliance decision engine without additional validation and controls.

---

# 29. No Accounting Advice

The application extracts and analyzes document information.

It does not provide professional:

```text
Accounting advice
Tax advice
Investment advice
Legal advice
Financial planning
```

Results should be interpreted within the intended application context.

---

# 30. No Production Authentication

The prototype does not implement a complete authentication system.

A production deployment should add:

```text
User authentication
Session management
Authorization
Role-based access control
Token management
Account lifecycle
```

---

# 31. No Production Authorization Model

The prototype does not implement granular access control for:

```text
Documents
Processing results
Financial information
Review decisions
Administrative functions
```

A production system should ensure that users can access only the documents and results they are authorized to access.

---

# 32. No Persistent Audit Trail

The prototype does not provide a complete immutable audit trail.

A production implementation may need to record:

```text
Who uploaded a document
When it was uploaded
Who viewed the result
Who modified extracted data
Who approved a review
What changed
When it changed
```

The audit system must itself avoid unnecessary exposure of sensitive financial data.

---

# 33. No Long-Term Document Storage

The prototype favors temporary processing.

The initial workflow is:

```text
Upload
   |
Process
   |
Return Result
   |
Delete Temporary File
```

A production application may require persistent storage.

If so, it must define:

```text
Retention policy
Encryption
Access control
Backup policy
Deletion policy
Data residency
Audit requirements
```

---

# 34. No Database Requirement

The core prototype does not require persistent database storage.

This limits capabilities such as:

```text
Document history
User history
Persistent processing jobs
Review history
Long-term analytics
Historical reconciliation
```

These can be added when persistence becomes a requirement.

---

# 35. Synchronous Processing Limitation

The initial prototype uses synchronous processing.

Conceptually:

```text
Request
   |
   v
Process Document
   |
   v
Return Response
```

This is simple but has scalability limitations.

Large documents or slow OCR/LLM operations can result in longer request times.

---

# 36. Async Processing as Future Enhancement

A production-scale implementation may use:

```text
Client
   |
   v
API
   |
   v
Job Queue
   |
   v
Worker
   |
   +--> OCR
   +--> LLM
   +--> Analysis
   |
   v
Result Store
```

This would enable:

```text
Background processing
Progress tracking
Retries
Horizontal scaling
Long-running jobs
```

---

# 37. No Guaranteed Processing SLA

The prototype does not guarantee:

```text
Maximum processing time
Availability SLA
Throughput SLA
Concurrent-user SLA
Provider response SLA
```

Processing time depends on:

```text
Document size
Page count
OCR complexity
LLM provider
Network conditions
Machine resources
```

---

# 38. External Provider Dependency

If external OCR or LLM providers are used, processing can depend on their:

```text
Availability
Latency
Rate limits
API changes
Pricing
Model behavior
Data policies
```

Provider failures should be handled gracefully.

---

# 39. External Provider Data Exposure

When a third-party OCR or LLM provider is used, document information may be transmitted outside the application's local environment.

This creates additional considerations around:

```text
Privacy
Data retention
Data residency
Provider policies
Security
Compliance
Contractual requirements
```

The prototype documents this boundary but does not provide enterprise-level provider governance.

---

# 40. No Offline AI Guarantee

The prototype architecture may use external AI/OCR providers.

Therefore it should not be assumed that the system can operate completely offline.

A future private deployment could use:

```text
Local OCR
Local LLM
Private inference infrastructure
```

if required by privacy or regulatory constraints.

---

# 41. LLM Provider Switching

The architecture isolates provider-specific code where practical.

However, switching providers can still require:

```text
Prompt changes
Schema adaptation
Output validation changes
Performance evaluation
Confidence recalibration
Cost evaluation
```

Provider abstraction reduces coupling but does not eliminate migration work.

---

# 42. No Guaranteed Semantic Understanding

The system may extract structured fields from a document without fully understanding every business-specific meaning.

For example:

```text
Special allowance
Adjustment
Arrear
Reimbursement
Employer contribution
```

may have organization-specific meanings.

The prototype normalizes information into its supported domain model rather than attempting to model every payroll or banking concept.

---

# 43. Currency Limitation

The primary prototype use case assumes Indian financial documents and INR amounts.

Examples:

```text
₹
INR
```

The current financial rules are therefore designed primarily around INR-style financial data.

International currencies and locale-specific formats may require additional normalization.

---

# 44. Date Format Limitations

Financial documents can use different date formats.

Examples:

```text
31/08/2026
31-08-2026
2026-08-31
Aug 31, 2026
31 Aug 2026
```

Normalization is required before financial comparisons.

Ambiguous dates may require human review.

---

# 45. Number Formatting Limitations

Financial documents may represent numbers differently.

Examples:

```text
59,000
₹59,000
59000.00
59 000
59K
```

Indian numbering conventions can also appear:

```text
1,00,000
10,00,000
```

Extraction and normalization must account for supported formats.

Unexpected number formatting can reduce extraction confidence.

---

# 46. Large Document Limitation

The prototype is not optimized for extremely large documents.

Large statements can introduce:

```text
Memory usage
OCR cost
Processing latency
LLM token limits
Large API responses
```

Production systems should consider:

```text
Streaming
Page-level processing
Chunking
Batch processing
Async workers
Pagination
Result persistence
```

---

# 47. Token / Context Limitations

When document text is sent to an LLM, model context limits may affect extraction.

Large documents may need:

```text
Chunking
Page batching
Relevant-section extraction
Summarization
Multi-pass extraction
```

The prototype may impose practical document-size or page-count limits.

---

# 48. No Guaranteed Extraction Completeness

A successful API response does not mean every field was extracted.

For example:

```text
Employee Name       ✓
Employer            ✓
Gross Salary        ✓
Net Salary          ✓
PAN                 -
Bank Account        -
```

Optional or unavailable fields should remain absent or null rather than being fabricated.

---

# 49. No Guaranteed Source Traceability

The initial prototype does not necessarily provide page-level source references for every extracted field.

Future enhancement:

```json
{
  "field": "net_salary",
  "value": 59000,
  "source": {
    "page": 1
  }
}
```

This would improve reviewer verification.

---

# 50. Field-Level Confidence Limitation

Overall confidence is prioritized first.

Field-level confidence may not initially be available for every field.

Future capability:

```json
{
  "net_salary": {
    "value": 59000,
    "confidence": 0.97
  }
}
```

This would make human review more targeted.

---

# 51. Frontend Limitations

The Angular frontend is initially focused on demonstrating the core workflow.

It may not initially provide:

```text
Advanced filtering
Complex dashboards
Persistent user history
Advanced review queues
Bulk processing
Advanced accessibility controls
Internationalization
Offline operation
```

These are potential future improvements.

---

# 52. Browser Upload Limitations

The browser is responsible for selecting and uploading documents.

Very large files can be affected by:

```text
Browser memory
Network speed
Request timeout
Server limits
```

The backend remains responsible for enforcing authoritative file-size and validation rules.

---

# 53. No Guaranteed Network Reliability

The frontend depends on the backend being reachable.

Possible failures include:

```text
Backend unavailable
Network interruption
Request timeout
CORS configuration error
Provider failure
Server overload
```

The Angular application should provide clear error states instead of appearing to hang indefinitely.

---

# 54. No Multi-Tenant Isolation

The prototype does not implement a multi-tenant architecture.

A production SaaS deployment would need strong tenant isolation for:

```text
Documents
Users
Processing results
Storage
Database records
Logs
Audit data
```

---

# 55. No High Availability

The prototype is not designed for high availability.

It does not guarantee:

```text
Zero downtime
Automatic failover
Multi-region deployment
Database failover
Provider failover
```

These are production infrastructure concerns.

---

# 56. No Disaster Recovery

The prototype does not implement a formal disaster-recovery strategy.

A production system with persistent data would need:

```text
Backups
Backup encryption
Recovery procedures
Recovery testing
RPO
RTO
```

---

# 57. No Advanced Observability

The prototype provides basic operational visibility.

Production deployments may require:

```text
Metrics
Distributed tracing
Centralized logs
Alerting
Dashboards
Error tracking
Provider monitoring
Security monitoring
```

---

# 58. No Formal Performance Benchmark

The prototype does not establish production-grade benchmarks for:

```text
Documents per minute
Concurrent users
Pages per second
OCR throughput
LLM throughput
Maximum supported statement size
```

Performance measurements may change depending on:

```text
Hardware
Provider
Document type
Model
Network
Deployment architecture
```

---

# 59. No Cost Optimization Guarantee

External OCR and LLM calls may introduce variable costs.

The prototype does not guarantee minimum processing cost.

Production optimization may include:

```text
Local text extraction first
OCR only when necessary
Page-level filtering
Prompt optimization
Model selection
Caching
Batching
Token monitoring
Provider routing
```

---

# 60. No Model Accuracy Guarantee

Different LLMs and OCR engines can produce different results.

Changing the provider or model may change:

```text
Extraction quality
Latency
Token usage
Structured-output behavior
Confidence
Failure modes
```

Any production model change should therefore be evaluated against a representative document test set.

---

# 61. No Universal Financial Rules

Financial institutions and organizations can have different definitions for:

```text
Salary
Recurring transaction
EMI
Large transaction
Income
Deduction
Net salary
```

The prototype uses explicit rules designed for the assignment.

These rules should not automatically be treated as universal business rules.

---

# 62. No Automatic Decision Authority

The application is an analysis and extraction system.

It should not automatically make decisions such as:

```text
Loan approval
Loan rejection
Credit approval
Employment verification
Fraud conviction
Account blocking
Tax liability determination
```

without additional domain-specific controls and human or policy-based review.

---

# 63. Security Limitations

The prototype intentionally does not provide every enterprise security control.

Known limitations include:

```text
No production authentication
No production authorization
No enterprise identity provider
No enterprise secrets manager
No complete audit system
No SIEM integration
No formal penetration testing
No formal compliance certification
```

These should be addressed before production use with real financial documents.

---

# 64. Testing Limitations

Automated tests can verify implemented behavior but cannot prove that every possible financial document will be processed correctly.

Testing limitations include:

```text
Limited document corpus
Limited layout diversity
Limited OCR scenarios
Limited LLM variability
Limited real-world transaction patterns
```

A production implementation should maintain a larger representative evaluation dataset.

---

# 65. Synthetic Data Limitation

The repository should use synthetic financial documents.

Synthetic documents may not capture every complexity found in real financial documents.

Therefore successful tests against synthetic data do not guarantee equivalent performance on all real-world documents.

---

# 66. Human Review Is Still Necessary

The system is designed to reduce manual effort, not eliminate human responsibility.

Human review may still be necessary when:

```text
Document quality is poor
Classification is uncertain
Fields are missing
Salary arithmetic is inconsistent
Transactions are ambiguous
Multiple reconciliation candidates exist
Confidence is low
Document structure is unfamiliar
```

---

# 67. Recommended Production Evolution

A production implementation could evolve toward:

```text
                    Internet
                       |
                       v
                API Gateway
                       |
                       v
                Authentication
                       |
                       v
                Document API
                       |
                       v
                 Job Queue
                       |
                       v
                  Workers
                       |
          +------------+------------+
          |            |            |
          v            v            v
        OCR       Extraction    Validation
                       |
                       v
                Financial Engine
                       |
                       v
                 Reconciliation
                       |
                       v
                 Result Store
                       |
                       v
                 Review System
```

Additional infrastructure could include:

```text
Object Storage
PostgreSQL
Redis
Message Queue
Observability
Audit Store
Secrets Manager
```

Only the components justified by actual production requirements should be introduced.

---

# 68. Limitation Management Strategy

Limitations should be handled through:

```text
Validation
Confidence
Explicit error states
Human review
Clear documentation
Test coverage
```

The system should prefer:

```text
"Unable to confidently extract this field."
```

over:

```text
inventing a value
```

Similarly:

```text
"Multiple reconciliation candidates found."
```

is preferable to silently selecting an uncertain transaction.

---

# 69. What This Prototype Demonstrates

Despite the limitations above, the prototype demonstrates the core engineering workflow:

```text
                    Document
                       |
                       v
                File Validation
                       |
                       v
                 OCR / Text
                       |
                       v
                Classification
                       |
                       v
               AI Extraction
                       |
                       v
              Structured Schema
                       |
                       v
             Deterministic Rules
                       |
                       v
              Financial Analysis
                       |
                       v
               Reconciliation
                       |
                       v
            Confidence / Review
```

It demonstrates that AI can be integrated into a financial-document workflow without allowing generated output to become the sole source of truth.

---

# 70. Final Limitation Statement

The Financial Document Analyzer is a prototype intended to demonstrate:

* Document intelligence
* OCR integration
* AI-assisted extraction
* Structured validation
* Deterministic financial analysis
* Explainable reconciliation
* Human-review awareness
* Secure handling principles

It should **not** be interpreted as a production-ready financial decision system.

The most important limitation is:

> **Document extraction is inherently uncertain, and financial decisions should not be based solely on automated extraction without appropriate validation and, where required, human review.**

The architecture therefore deliberately favors:

```text
Explicit uncertainty
+
Deterministic validation
+
Explainability
+
Human review
```

over unsupported claims of complete automation or accuracy.

````