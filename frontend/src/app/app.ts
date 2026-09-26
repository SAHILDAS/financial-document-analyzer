import {
  Component,
  OnInit,
  inject,
  signal,
} from '@angular/core';

import { CommonModule } from '@angular/common';

import { ApiService } from './core/services/api.service';

import {
  AnalyzeResponse,
  BankAnalysisResult,
  BankTransaction,
  HealthResponse,
} from './core/models/api-response.model';

import {
  ReconciliationRequest,
  ReconciliationResponse,
  ReconciliationResult,
} from './core/models/reconciliation.model';

@Component({
  selector: 'app-root',
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly apiService = inject(ApiService);

  // ============================================================
  // Backend health
  // ============================================================

  readonly health = signal<HealthResponse | null>(null);

  // ============================================================
  // Global error
  // ============================================================

  readonly error = signal('');

  // ============================================================
  // Existing single-document analysis
  // ============================================================

  readonly selectedFile = signal<File | null>(null);

  readonly analyzing = signal(false);

  readonly analysis =
    signal<AnalyzeResponse | null>(null);

  // ============================================================
  // Reconciliation files
  // ============================================================

  readonly selectedSalaryFile =
    signal<File | null>(null);

  readonly selectedBankFile =
    signal<File | null>(null);

  // ============================================================
  // Reconciliation analysis results
  // ============================================================

  readonly salaryReconciliationAnalysis =
    signal<AnalyzeResponse | null>(null);

  readonly bankReconciliationAnalysis =
    signal<AnalyzeResponse | null>(null);

  // ============================================================
  // Reconciliation state
  // ============================================================

  readonly reconciling = signal(false);

  readonly reconciliation =
    signal<ReconciliationResult | null>(null);

  readonly reconciliationError =
    signal('');

  // ============================================================
  // Lifecycle
  // ============================================================

  ngOnInit(): void {
    this.checkHealth();
  }

  // ============================================================
  // Backend health
  // ============================================================

  checkHealth(): void {
    this.apiService.health().subscribe({
      next: (response) => {
        this.health.set(response);
      },

      error: (error) => {
        console.error(
          'Backend health check failed:',
          error,
        );

        this.error.set(
          'Unable to connect to the backend.',
        );
      },
    });
  }

  // ============================================================
  // Existing single-document workflow
  // ============================================================

  onFileSelected(event: Event): void {
    const input =
      event.target as HTMLInputElement;

    const file =
      input.files?.[0] ?? null;

    this.selectedFile.set(file);

    this.analysis.set(null);

    this.error.set('');
  }

  analyzeDocument(): void {
    const file =
      this.selectedFile();

    if (!file) {
      this.error.set(
        'Please select a document first.',
      );

      return;
    }

    this.analyzing.set(true);

    this.analysis.set(null);

    this.error.set('');

    this.apiService
      .analyzeDocument(file)
      .subscribe({
        next: (response) => {
          this.analysis.set(response);

          this.analyzing.set(false);
        },

        error: (error) => {
          console.error(
            'Document analysis failed:',
            error,
          );

          const message =
            error?.error?.errors?.[0]?.message ??
            'Unable to analyze the document.';

          this.error.set(message);

          this.analyzing.set(false);
        },
      });
  }

  clearAnalysis(): void {
    this.selectedFile.set(null);

    this.analysis.set(null);

    this.error.set('');
  }

  // ============================================================
  // Existing analysis helpers
  // ============================================================

  isSalaryAnalysis(): boolean {
    const result =
      this.analysis();

    return (
      result?.document_type ===
        'salary_slip' &&
      result.data?.salary !== null &&
      result.data?.salary !== undefined
    );
  }

  isBankAnalysis(): boolean {
    const result =
      this.analysis();

    return (
      result?.document_type ===
        'bank_statement' &&
      result.data?.bank !== null &&
      result.data?.bank !== undefined
    );
  }

  get bankAnalysis():
    | BankAnalysisResult
    | null {
    return (
      this.analysis()?.data?.bank ??
      null
    );
  }

  // ============================================================
  // Reconciliation file selection
  // ============================================================

  onSalaryReconciliationFileSelected(
    event: Event,
  ): void {
    const input =
      event.target as HTMLInputElement;

    const file =
      input.files?.[0] ?? null;

    this.selectedSalaryFile.set(file);

    this.salaryReconciliationAnalysis.set(
      null,
    );

    this.reconciliation.set(null);

    this.reconciliationError.set('');
  }

  onBankReconciliationFileSelected(
    event: Event,
  ): void {
    const input =
      event.target as HTMLInputElement;

    const file =
      input.files?.[0] ?? null;

    this.selectedBankFile.set(file);

    this.bankReconciliationAnalysis.set(
      null,
    );

    this.reconciliation.set(null);

    this.reconciliationError.set('');
  }

  // ============================================================
  // Analyze salary document for reconciliation
  // ============================================================

  analyzeSalaryForReconciliation(): void {
    const file =
      this.selectedSalaryFile();

    if (!file) {
      this.reconciliationError.set(
        'Please select a salary slip first.',
      );

      return;
    }

    this.reconciliationError.set('');

    this.salaryReconciliationAnalysis.set(
      null,
    );

    this.reconciliation.set(null);

    this.apiService
      .analyzeDocument(file)
      .subscribe({
        next: (response) => {
          if (
            !response.success ||
            response.document_type !==
              'salary_slip' ||
            !response.data?.salary
          ) {
            this.reconciliationError.set(
              'The selected salary document could not be identified as a valid salary slip.',
            );

            return;
          }

          this.salaryReconciliationAnalysis.set(
            response,
          );
        },

        error: (error) => {
          console.error(
            'Salary reconciliation analysis failed:',
            error,
          );

          const message =
            error?.error?.errors?.[0]?.message ??
            'Unable to analyze the salary document.';

          this.reconciliationError.set(
            message,
          );
        },
      });
  }

  // ============================================================
  // Analyze bank document for reconciliation
  // ============================================================

  analyzeBankForReconciliation(): void {
    const file =
      this.selectedBankFile();

    if (!file) {
      this.reconciliationError.set(
        'Please select a bank statement first.',
      );

      return;
    }

    this.reconciliationError.set('');

    this.bankReconciliationAnalysis.set(
      null,
    );

    this.reconciliation.set(null);

    this.apiService
      .analyzeDocument(file)
      .subscribe({
        next: (response) => {
          if (
            !response.success ||
            response.document_type !==
              'bank_statement' ||
            !response.data?.bank
          ) {
            this.reconciliationError.set(
              'The selected bank document could not be identified as a valid bank statement.',
            );

            return;
          }

          this.bankReconciliationAnalysis.set(
            response,
          );
        },

        error: (error) => {
          console.error(
            'Bank reconciliation analysis failed:',
            error,
          );

          const message =
            error?.error?.errors?.[0]?.message ??
            'Unable to analyze the bank statement.';

          this.reconciliationError.set(
            message,
          );
        },
      });
  }

  // ============================================================
  // Analyze both reconciliation documents
  // ============================================================

  analyzeReconciliationDocuments(): void {
    const salaryFile =
      this.selectedSalaryFile();

    const bankFile =
      this.selectedBankFile();

    if (!salaryFile) {
      this.reconciliationError.set(
        'Please select a salary slip.',
      );

      return;
    }

    if (!bankFile) {
      this.reconciliationError.set(
        'Please select a bank statement.',
      );

      return;
    }

    this.reconciliationError.set('');

    this.reconciliation.set(null);

    this.salaryReconciliationAnalysis.set(
      null,
    );

    this.bankReconciliationAnalysis.set(
      null,
    );

    let salaryCompleted = false;
    let bankCompleted = false;

    let salaryResponse:
      | AnalyzeResponse
      | null = null;

    let bankResponse:
      | AnalyzeResponse
      | null = null;

    const handleCompletion = (): void => {
      if (
        !salaryCompleted ||
        !bankCompleted
      ) {
        return;
      }

      if (
        !salaryResponse?.success ||
        salaryResponse.document_type !==
          'salary_slip' ||
        !salaryResponse.data?.salary
      ) {
        this.reconciliationError.set(
          'The selected salary document could not be identified as a valid salary slip.',
        );

        return;
      }

      if (
        !bankResponse?.success ||
        bankResponse.document_type !==
          'bank_statement' ||
        !bankResponse.data?.bank
      ) {
        this.reconciliationError.set(
          'The selected bank document could not be identified as a valid bank statement.',
        );

        return;
      }

      this.salaryReconciliationAnalysis.set(
        salaryResponse,
      );

      this.bankReconciliationAnalysis.set(
        bankResponse,
      );
    };

    this.apiService
      .analyzeDocument(salaryFile)
      .subscribe({
        next: (response) => {
          salaryResponse = response;

          salaryCompleted = true;

          handleCompletion();
        },

        error: (error) => {
          console.error(
            'Salary document analysis failed:',
            error,
          );

          this.reconciliationError.set(
            error?.error?.errors?.[0]
              ?.message ??
              'Unable to analyze the salary document.',
          );

          salaryCompleted = true;

          handleCompletion();
        },
      });

    this.apiService
      .analyzeDocument(bankFile)
      .subscribe({
        next: (response) => {
          bankResponse = response;

          bankCompleted = true;

          handleCompletion();
        },

        error: (error) => {
          console.error(
            'Bank statement analysis failed:',
            error,
          );

          this.reconciliationError.set(
            error?.error?.errors?.[0]
              ?.message ??
              'Unable to analyze the bank statement.',
          );

          bankCompleted = true;

          handleCompletion();
        },
      });
  }

  // ============================================================
  // Run reconciliation
  // ============================================================

  reconcileDocuments(): void {
    const salaryResponse =
      this.salaryReconciliationAnalysis();

    const bankResponse =
      this.bankReconciliationAnalysis();

    if (
      !salaryResponse?.data?.salary
    ) {
      this.reconciliationError.set(
        'Please analyze a valid salary slip first.',
      );

      return;
    }

    if (
      !bankResponse?.data?.bank
    ) {
      this.reconciliationError.set(
        'Please analyze a valid bank statement first.',
      );

      return;
    }

    const request:
      ReconciliationRequest = {
      salary:
        salaryResponse.data.salary,

      bank:
        bankResponse.data.bank,
    };

    this.reconciling.set(true);

    this.reconciliation.set(null);

    this.reconciliationError.set('');

    this.apiService
      .reconcileDocuments(request)
      .subscribe({
        next: (
          response: ReconciliationResponse,
        ) => {
          this.reconciling.set(false);

          if (
            !response.success ||
            !response.result
          ) {
            this.reconciliationError.set(
              response.error ??
                'Unable to reconcile the documents.',
            );

            return;
          }

          this.reconciliation.set(
            response.result,
          );
        },

        error: (error) => {
          console.error(
            'Document reconciliation failed:',
            error,
          );

          this.reconciling.set(false);

          this.reconciliationError.set(
            error?.error?.error ??
              error?.error?.detail ??
              'Unable to reconcile the documents.',
          );
        },
      });
  }

  // ============================================================
  // Reconciliation state helpers
  // ============================================================

  canReconcile(): boolean {
    return (
      this.salaryReconciliationAnalysis()
        ?.data?.salary !== null &&
      this.salaryReconciliationAnalysis()
        ?.data?.salary !== undefined &&
      this.bankReconciliationAnalysis()
        ?.data?.bank !== null &&
      this.bankReconciliationAnalysis()
        ?.data?.bank !== undefined
    );
  }

  hasReconciliationResult(): boolean {
    return (
      this.reconciliation() !== null
    );
  }

  get reconciliationStatus():
    | string
    | null {
    return (
      this.reconciliation()
        ?.status ?? null
    );
  }

  getReconciliationStatusLabel(
    status:
      | string
      | null
      | undefined,
  ): string {
    switch (status) {
      case 'matched':
        return 'Matched';

      case 'multiple_candidates':
        return 'Multiple Candidates';

      case 'needs_review':
        return 'Needs Review';

      case 'no_match':
        return 'No Match';

      default:
        return 'Unknown';
    }
  }

  getReconciliationStatusClass(
    status:
      | string
      | null
      | undefined,
  ): string {
    switch (status) {
      case 'matched':
        return 'reconciliation-matched';

      case 'multiple_candidates':
        return 'reconciliation-multiple';

      case 'needs_review':
        return 'reconciliation-review';

      case 'no_match':
        return 'reconciliation-no-match';

      default:
        return '';
    }
  }

  getCandidateScoreClass(
    score: number,
  ): string {
    if (score >= 0.85) {
      return 'score-high';
    }

    if (score >= 0.65) {
      return 'score-medium';
    }

    return 'score-low';
  }

  // ============================================================
  // Clear reconciliation
  // ============================================================

  clearReconciliation(): void {
    this.selectedSalaryFile.set(null);

    this.selectedBankFile.set(null);

    this.salaryReconciliationAnalysis.set(
      null,
    );

    this.bankReconciliationAnalysis.set(
      null,
    );

    this.reconciliation.set(null);

    this.reconciliationError.set('');

    this.reconciling.set(false);
  }

  // ============================================================
  // Formatting helpers
  // ============================================================

  formatAmount(
    value:
      | string
      | null
      | undefined,
  ): string {
    if (
      value === null ||
      value === undefined ||
      value === ''
    ) {
      return '—';
    }

    const amount = Number(value);

    if (Number.isNaN(amount)) {
      return value;
    }

    return new Intl.NumberFormat(
      'en-IN',
      {
        style: 'currency',
        currency: 'INR',
        maximumFractionDigits: 2,
      },
    ).format(amount);
  }

  formatPercentage(
    score: number,
  ): string {
    return `${Math.round(score * 100)}%`;
  }

  getConfidenceClass(
    level:
      | string
      | undefined,
  ): string {
    switch (level) {
      case 'high':
        return 'confidence-high';

      case 'medium':
        return 'confidence-medium';

      case 'low':
        return 'confidence-low';

      default:
        return '';
    }
  }

  formatDate(
    value:
      | string
      | null
      | undefined,
  ): string {
    if (!value) {
      return '—';
    }

    const date = new Date(
      `${value}T00:00:00`,
    );

    if (
      Number.isNaN(
        date.getTime(),
      )
    ) {
      return value;
    }

    return new Intl.DateTimeFormat(
      'en-IN',
      {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      },
    ).format(date);
  }

  getBankTransactionAmount(
    transaction: BankTransaction,
  ): string {
    if (transaction.credit) {
      return this.formatAmount(
        transaction.credit,
      );
    }

    if (transaction.debit) {
      return this.formatAmount(
        transaction.debit,
      );
    }

    return '—';
  }

  getTransactionType(
    transaction: BankTransaction,
  ): string {
    if (transaction.credit) {
      return 'Credit';
    }

    if (transaction.debit) {
      return 'Debit';
    }

    return '—';
  }

  getTransactionTypeClass(
    transaction: BankTransaction,
  ): string {
    if (transaction.credit) {
      return 'credit';
    }

    if (transaction.debit) {
      return 'debit';
    }

    return '';
  }
}