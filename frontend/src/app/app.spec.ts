import {
  HttpTestingController,
  provideHttpClientTesting,
} from '@angular/common/http/testing';
import { provideHttpClient } from '@angular/common/http';
import { TestBed } from '@angular/core/testing';

import { App } from './app';
import {
  AnalyzeResponse,
} from './core/models/api-response.model';
import {
  ReconciliationResponse,
} from './core/models/reconciliation.model';

describe('App', () => {
  let httpTesting: HttpTestingController;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [App],
      providers: [
        provideHttpClient(),
        provideHttpClientTesting(),
      ],
    }).compileComponents();

    httpTesting = TestBed.inject(
      HttpTestingController,
    );
  });

  afterEach(() => {
    httpTesting.verify();
  });

  // ============================================================
  // Test helpers
  // ============================================================

  /**
   * Creates the App component and resolves the health
   * request automatically triggered by ngOnInit().
   */
  function createApp() {
    const fixture =
      TestBed.createComponent(App);

    const app =
      fixture.componentInstance;

    fixture.detectChanges();

    const healthRequest =
      httpTesting.expectOne(
        'http://127.0.0.1:8000/api/health',
    );

    expect(
      healthRequest.request.method,
    ).toBe('GET');

    healthRequest.flush({
      status: 'ok',
      service: 'Financial Document Analyzer',
      environment: 'test',
    });

    return {
      fixture,
      app,
    };
  }

  /**
   * Creates a complete AnalyzeResponse matching the
   * actual frontend API model.
   */
  function createAnalyzeResponse(
    documentType:
      | 'salary_slip'
      | 'bank_statement',
  ): AnalyzeResponse {
    if (documentType === 'salary_slip') {
      return {
        success: true,

        document_id:
          'salary-test-document',

        document_type:
          'salary_slip',

        confidence: 1,

        data: {
          classification_reason:
            'Test salary slip classification.',

          file: {
            filename:
              'salary-test.png',

            extension: '.png',

            size_bytes: 1024,
          },

          salary: {
            salary: {
              employee: {
                name: 'Sanjib Das',
                employee_id: 'EMP101',
                employer:
                  'DEMO COMPANY 101',
                salary_month:
                  'September 2026',
                pan: 'EZSPD1654L',
              },

              earnings: {
                basic: '45000',
                hra: '10000',
                allowances: '1000',
                bonus: '0',
                other: '0',
                gross: '56000',
              },

              deductions: {
                pf: '4500',
                professional_tax: '0',
                tds: '1000',
                other: '0',
                total: '5500',
              },

              net_salary: '50500',

              bank_account: {
                account_number:
                  '501234567890',
              },

              field_confidence: {
                employee_name: 1,
                employer: 1,
                gross: 1,
                total_deductions: 1,
                net_salary: 1,
              },
            },

            calculation: {
              calculated_earnings:
                '56000',

              reported_gross:
                '56000',

              earnings_difference:
                '0',

              calculated_net:
                '50500',

              reported_net:
                '50500',

              net_difference:
                '0',

              can_calculate_earnings:
                true,

              can_calculate_net:
                true,
            },

            validation: {
              is_valid: true,
              issues: [],
            },

            confidence: {
              score: 1,
              level: 'high',
              needs_review: false,
              reasons: [],
            },
          },

          bank: null,

          extra: null,
        },

        validation: {
          is_valid: true,
          issues: [],
        },

        processing: {
          source: 'native_text',

          methods: [
            'pdf_text',
          ],

          page_count: 1,

          text_quality_score: 1,
        },

        errors: [],
      };
    }

    return {
      success: true,

      document_id:
        'bank-test-document',

      document_type:
        'bank_statement',

      confidence: 1,

      data: {
        classification_reason:
          'Test bank statement classification.',

        file: {
          filename:
            'bank-test.png',

          extension: '.png',

          size_bytes: 2048,
        },

        salary: null,

        bank: {
          statement: {
            account: {
              holder_name:
                'Sanjib Das',

              bank_name:
                'DEMO BANK',

              account_number:
                '501234567890',

              ifsc:
                'DEMO0001234',
            },

            statement_period: {
              from_date:
                '2026-09-01',

              to_date:
                '2026-09-30',
            },

            opening_balance:
              '80000',

            closing_balance:
              '125500',

            transactions: [
              {
                date:
                  '2026-09-10',

                narration:
                  'NEFT CREDIT | DEMO COMPANY 101 SALARY',

                debit: null,

                credit:
                  '50500',

                balance:
                  '130500',
              },
            ],
          },

          analysis: {
            total_credits:
              '50500',

            total_debits:
              '0',

            average_monthly_credit:
              '50500',

            large_transactions: [],

            salary_credit_candidates: [],

            recurring_transactions: [],

            emi_candidates: [],
          },

          validation: {
            is_valid: true,
            issues: [],
          },
        },

        extra: null,
      },

      validation: {
        is_valid: true,
        issues: [],
      },

      processing: {
        source: 'ocr',

        methods: [
          'image_ocr',
        ],

        page_count: 1,

        text_quality_score: 1,
      },

      errors: [],
    };
  }

  // ============================================================
  // Basic application tests
  // ============================================================

  it('should create the app', () => {
    const { app } = createApp();

    expect(app).toBeTruthy();
  });

  it('should render the application title', () => {
    const { fixture } = createApp();

    expect(
      fixture.nativeElement.textContent,
    ).toContain(
      'Financial Document Analyzer',
    );
  });

  // ============================================================
  // Reconciliation status labels
  // ============================================================

  describe(
    'reconciliation status labels',
    () => {
      it(
        'should return the correct label for matched status',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusLabel(
              'matched',
            ),
          ).toBe('Matched');
        },
      );

      it(
        'should return the correct label for multiple candidates',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusLabel(
              'multiple_candidates',
            ),
          ).toBe(
            'Multiple Candidates',
          );
        },
      );

      it(
        'should return the correct label for no match',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusLabel(
              'no_match',
            ),
          ).toBe('No Match');
        },
      );

      it(
        'should return the correct label for needs review',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusLabel(
              'needs_review',
            ),
          ).toBe('Needs Review');
        },
      );

      it(
        'should return Unknown for an unknown status',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusLabel(
              'unknown',
            ),
          ).toBe('Unknown');
        },
      );
    },
  );

  // ============================================================
  // Reconciliation status classes
  // ============================================================

  describe(
    'reconciliation status classes',
    () => {
      it(
        'should return the matched CSS class',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusClass(
              'matched',
            ),
          ).toBe(
            'reconciliation-matched',
          );
        },
      );

      it(
        'should return the multiple candidates CSS class',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusClass(
              'multiple_candidates',
            ),
          ).toBe(
            'reconciliation-multiple',
          );
        },
      );

      it(
        'should return the needs review CSS class',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusClass(
              'needs_review',
            ),
          ).toBe(
            'reconciliation-review',
          );
        },
      );

      it(
        'should return the no match CSS class',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusClass(
              'no_match',
            ),
          ).toBe(
            'reconciliation-no-match',
          );
        },
      );

      it(
        'should return an empty class for an unknown status',
        () => {
          const { app } = createApp();

          expect(
            app.getReconciliationStatusClass(
              'unknown',
            ),
          ).toBe('');
        },
      );
    },
  );

  // ============================================================
  // Candidate score classes
  // ============================================================

  describe(
    'reconciliation candidate score classes',
    () => {
      it(
        'should classify a high score as high confidence',
        () => {
          const { app } = createApp();

          expect(
            app.getCandidateScoreClass(
              0.95,
            ),
          ).toBe('score-high');
        },
      );

      it(
        'should classify a medium score as medium confidence',
        () => {
          const { app } = createApp();

          expect(
            app.getCandidateScoreClass(
              0.75,
            ),
          ).toBe('score-medium');
        },
      );

      it(
        'should classify a low score as low confidence',
        () => {
          const { app } = createApp();

          expect(
            app.getCandidateScoreClass(
              0.40,
            ),
          ).toBe('score-low');
        },
      );

      it(
        'should classify the high boundary correctly',
        () => {
          const { app } = createApp();

          expect(
            app.getCandidateScoreClass(
              0.85,
            ),
          ).toBe('score-high');
        },
      );

      it(
        'should classify the medium boundary correctly',
        () => {
          const { app } = createApp();

          expect(
            app.getCandidateScoreClass(
              0.65,
            ),
          ).toBe('score-medium');
        },
      );
    },
  );

  // ============================================================
  // Reconciliation readiness
  // ============================================================

  describe(
    'reconciliation readiness',
    () => {
      it(
        'should not allow reconciliation before both analyses exist',
        () => {
          const { app } = createApp();

          expect(
            app.canReconcile(),
          ).toBe(false);
        },
      );

      it(
        'should allow reconciliation after both analyses exist',
        () => {
          const { app } = createApp();

          const salaryResponse =
            createAnalyzeResponse(
              'salary_slip',
            );

          const bankResponse =
            createAnalyzeResponse(
              'bank_statement',
            );

          app.salaryReconciliationAnalysis.set(
            salaryResponse,
          );

          app.bankReconciliationAnalysis.set(
            bankResponse,
          );

          expect(
            app.canReconcile(),
          ).toBe(true);
        },
      );
    },
  );

  // ============================================================
  // Reconciliation initial state
  // ============================================================

  describe(
    'reconciliation state',
    () => {
      it(
        'should initially have no reconciliation result',
        () => {
          const { app } = createApp();

          expect(
            app.hasReconciliationResult(),
          ).toBe(false);

          expect(
            app.reconciliation(),
          ).toBeNull();

          expect(
            app.reconciliationStatus,
          ).toBeNull();
        },
      );

      it(
        'should initially have no reconciliation error',
        () => {
          const { app } = createApp();

          expect(
            app.reconciliationError(),
          ).toBe('');
        },
      );

      it(
        'should clear reconciliation state',
        () => {
          const { app } = createApp();

          app.clearReconciliation();

          expect(
            app.reconciliation(),
          ).toBeNull();

          expect(
            app.reconciliationError(),
          ).toBe('');

          expect(
            app.reconciling(),
          ).toBe(false);

          expect(
            app.selectedSalaryFile(),
          ).toBeNull();

          expect(
            app.selectedBankFile(),
          ).toBeNull();

          expect(
            app.salaryReconciliationAnalysis(),
          ).toBeNull();

          expect(
            app.bankReconciliationAnalysis(),
          ).toBeNull();
        },
      );
    },
  );

  // ============================================================
  // Reconcile documents
  // ============================================================

  describe(
    'reconcileDocuments()',
    () => {
      it(
        'should send the extracted salary and bank data to the reconciliation API',
        () => {
          const { app } = createApp();

          const salaryResponse =
            createAnalyzeResponse(
              'salary_slip',
            );

          const bankResponse =
            createAnalyzeResponse(
              'bank_statement',
            );

          app.salaryReconciliationAnalysis.set(
            salaryResponse,
          );

          app.bankReconciliationAnalysis.set(
            bankResponse,
          );

          app.reconcileDocuments();

          expect(
            app.reconciling(),
          ).toBe(true);

          const request =
            httpTesting.expectOne(
              'http://127.0.0.1:8000/api/documents/reconcile',
            );

          expect(
            request.request.method,
          ).toBe('POST');

          expect(
            request.request.body,
          ).toEqual({
            salary:
              salaryResponse.data!.salary,

            bank:
              bankResponse.data!.bank,
          });

          request.flush({
            success: true,

            result: {
              status: 'matched',

              salary_net_amount:
                '50500',

              candidates: [],

              selected_candidate: null,

              confidence: 0.95,

              explanation:
                'Salary credit matched successfully.',
            },

            error: null,
          } satisfies ReconciliationResponse);

          expect(
            app.reconciling(),
          ).toBe(false);

          expect(
            app.reconciliation()?.status,
          ).toBe('matched');

          expect(
            app.reconciliation()?.confidence,
          ).toBe(0.95);

          expect(
            app.reconciliationError(),
          ).toBe('');
        },
      );

      // ========================================================
      // API error
      // ========================================================

      it(
        'should store the API error when reconciliation fails',
        () => {
          const { app } = createApp();

          const salaryResponse =
            createAnalyzeResponse(
              'salary_slip',
            );

          const bankResponse =
            createAnalyzeResponse(
              'bank_statement',
            );

          app.salaryReconciliationAnalysis.set(
            salaryResponse,
          );

          app.bankReconciliationAnalysis.set(
            bankResponse,
          );

          app.reconcileDocuments();

          expect(
            app.reconciling(),
          ).toBe(true);

          const request =
            httpTesting.expectOne(
              'http://127.0.0.1:8000/api/documents/reconcile',
            );

          request.flush(
            {
              error:
                'Unable to reconcile the documents.',
            },
            {
              status: 500,
              statusText:
                'Internal Server Error',
            },
          );

          expect(
            app.reconciling(),
          ).toBe(false);

          expect(
            app.reconciliation(),
          ).toBeNull();

          expect(
            app.reconciliationError(),
          ).toBe(
            'Unable to reconcile the documents.',
          );
        },
      );

      // ========================================================
      // Missing salary analysis
      // ========================================================

      it(
        'should reject reconciliation when salary analysis is missing',
        () => {
          const { app } = createApp();

          const bankResponse =
            createAnalyzeResponse(
              'bank_statement',
            );

          app.bankReconciliationAnalysis.set(
            bankResponse,
          );

          app.reconcileDocuments();

          expect(
            app.reconciling(),
          ).toBe(false);

          expect(
            app.reconciliation(),
          ).toBeNull();

          expect(
            app.reconciliationError(),
          ).toBe(
            'Please analyze a valid salary slip first.',
          );
        },
      );

      // ========================================================
      // Missing bank analysis
      // ========================================================

      it(
        'should reject reconciliation when bank analysis is missing',
        () => {
          const { app } = createApp();

          const salaryResponse =
            createAnalyzeResponse(
              'salary_slip',
            );

          app.salaryReconciliationAnalysis.set(
            salaryResponse,
          );

          app.reconcileDocuments();

          expect(
            app.reconciling(),
          ).toBe(false);

          expect(
            app.reconciliation(),
          ).toBeNull();

          expect(
            app.reconciliationError(),
          ).toBe(
            'Please analyze a valid bank statement first.',
          );
        },
      );
    },
  );

  // ============================================================
  // Formatting helpers
  // ============================================================

  describe(
    'formatAmount()',
    () => {
      it(
        'should format an INR amount',
        () => {
          const { app } = createApp();

          expect(
            app.formatAmount('50500'),
          ).toContain('50,500');
        },
      );

      it(
        'should return an em dash for an empty value',
        () => {
          const { app } = createApp();

          expect(
            app.formatAmount(null),
          ).toBe('—');

          expect(
            app.formatAmount(undefined),
          ).toBe('—');

          expect(
            app.formatAmount(''),
          ).toBe('—');
        },
      );

      it(
        'should return the original value for an invalid number',
        () => {
          const { app } = createApp();

          expect(
            app.formatAmount('invalid'),
          ).toBe('invalid');
        },
      );
    },
  );

  describe(
    'formatPercentage()',
    () => {
      it(
        'should format a decimal score as a percentage',
        () => {
          const { app } = createApp();

          expect(
            app.formatPercentage(0.95),
          ).toBe('95%');
        },
      );

      it(
        'should round percentage values',
        () => {
          const { app } = createApp();

          expect(
            app.formatPercentage(0.756),
          ).toBe('76%');
        },
      );
    },
  );

  describe(
    'getConfidenceClass()',
    () => {
      it(
        'should return the high confidence class',
        () => {
          const { app } = createApp();

          expect(
            app.getConfidenceClass('high'),
          ).toBe('confidence-high');
        },
      );

      it(
        'should return the medium confidence class',
        () => {
          const { app } = createApp();

          expect(
            app.getConfidenceClass('medium'),
          ).toBe('confidence-medium');
        },
      );

      it(
        'should return the low confidence class',
        () => {
          const { app } = createApp();

          expect(
            app.getConfidenceClass('low'),
          ).toBe('confidence-low');
        },
      );

      it(
        'should return an empty class for an unknown confidence level',
        () => {
          const { app } = createApp();

          expect(
            app.getConfidenceClass(
              'unknown',
            ),
          ).toBe('');
        },
      );
    },
  );

  describe(
    'formatDate()',
    () => {
      it(
        'should format an ISO date',
        () => {
          const { app } = createApp();

          expect(
            app.formatDate(
              '2026-09-10',
            ),
          ).toContain('10');

          expect(
            app.formatDate(
              '2026-09-10',
            ),
          ).toContain('2026');
        },
      );

      it(
        'should return an em dash for an empty date',
        () => {
          const { app } = createApp();

          expect(
            app.formatDate(null),
          ).toBe('—');

          expect(
            app.formatDate(undefined),
          ).toBe('—');
        },
      );

      it(
        'should return the original value for an invalid date',
        () => {
          const { app } = createApp();

          expect(
            app.formatDate(
              'invalid-date',
            ),
          ).toBe('invalid-date');
        },
      );
    },
  );
});