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

@Component({
  selector: 'app-root',
  imports: [CommonModule],
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly apiService = inject(ApiService);

  readonly health = signal<HealthResponse | null>(null);
  readonly error = signal('');

  readonly selectedFile = signal<File | null>(null);
  readonly analyzing = signal(false);
  readonly analysis = signal<AnalyzeResponse | null>(null);

  ngOnInit(): void {
    this.checkHealth();
  }

  checkHealth(): void {
    this.apiService.health().subscribe({
      next: (response) => {
        this.health.set(response);
      },
      error: (error) => {
        console.error('Backend health check failed:', error);

        this.error.set(
          'Unable to connect to the backend.',
        );
      },
    });
  }

  onFileSelected(event: Event): void {
    const input = event.target as HTMLInputElement;

    const file = input.files?.[0] ?? null;

    this.selectedFile.set(file);
    this.analysis.set(null);
    this.error.set('');
  }

  analyzeDocument(): void {
    const file = this.selectedFile();

    if (!file) {
      this.error.set(
        'Please select a document first.',
      );
      return;
    }

    this.analyzing.set(true);
    this.analysis.set(null);
    this.error.set('');

    this.apiService.analyzeDocument(file).subscribe({
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

  isSalaryAnalysis(): boolean {
    const result = this.analysis();

    return (
      result?.document_type === 'salary_slip' &&
      result.data?.salary !== null &&
      result.data?.salary !== undefined
    );
  }

  isBankAnalysis(): boolean {
    const result = this.analysis();

    return (
      result?.document_type === 'bank_statement' &&
      result.data?.bank !== null &&
      result.data?.bank !== undefined
    );
  }

  get bankAnalysis(): BankAnalysisResult | null {
    return this.analysis()?.data?.bank ?? null;
  }

  formatAmount(
    value: string | null | undefined,
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

    return new Intl.NumberFormat('en-IN', {
      style: 'currency',
      currency: 'INR',
      maximumFractionDigits: 2,
    }).format(amount);
  }

  formatPercentage(score: number): string {
    return `${Math.round(score * 100)}%`;
  }

  getConfidenceClass(
    level: string | undefined,
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
    value: string | null | undefined,
  ): string {
    if (!value) {
      return '—';
    }

    const date = new Date(
      `${value}T00:00:00`,
    );

    if (Number.isNaN(date.getTime())) {
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