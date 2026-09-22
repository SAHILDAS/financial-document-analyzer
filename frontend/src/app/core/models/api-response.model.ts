export interface HealthResponse {
  status: string;
  service: string;
  environment: string;
}

export type DocumentType =
  | 'salary_slip'
  | 'bank_statement'
  | 'unknown';

export type ConfidenceLevel =
  | 'high'
  | 'medium'
  | 'low';

export interface ValidationIssue {
  code: string;
  message: string;
  severity: 'info' | 'warning' | 'error';
  field: string | null;
}

export interface ValidationResult {
  is_valid: boolean;
  issues: ValidationIssue[];
}

export interface ConfidenceResult {
  score: number;
  level: ConfidenceLevel;
  needs_review: boolean;
  reasons: string[];
}

export interface SalaryEmployee {
  name: string | null;
  employee_id: string | null;
  employer: string | null;
  salary_month: string | null;
  pan: string | null;
}

export interface SalaryEarnings {
  basic: string | null;
  hra: string | null;
  allowances: string | null;
  bonus: string | null;
  other: string | null;
  gross: string | null;
}

export interface SalaryDeductions {
  pf: string | null;
  professional_tax: string | null;
  tds: string | null;
  other: string | null;
  total: string | null;
}

export interface SalaryBankAccount {
  account_number: string | null;
}

export interface SalarySlip {
  employee: SalaryEmployee;
  earnings: SalaryEarnings;
  deductions: SalaryDeductions;
  net_salary: string | null;
  bank_account: SalaryBankAccount | null;
  field_confidence: Record<string, number | null> | null;
}

export interface SalaryCalculationResult {
  calculated_earnings: string | null;
  reported_gross: string | null;
  earnings_difference: string | null;
  calculated_net: string | null;
  reported_net: string | null;
  net_difference: string | null;
  can_calculate_earnings: boolean;
  can_calculate_net: boolean;
}

export interface SalaryAnalysisResult {
  salary: SalarySlip;
  calculation: SalaryCalculationResult;
  validation: ValidationResult;
  confidence: ConfidenceResult;
}

export interface AnalyzeFileInfo {
  filename: string;
  extension: string;
  size_bytes: number;
}

export interface AnalyzeProcessingInfo {
  source: 'native_text' | 'ocr' | 'mixed';
  methods: Array<'pdf_text' | 'image_ocr' | 'pdf_ocr'>;
  page_count: number;
  text_quality_score: number;
}

export interface AnalyzeData {
  classification_reason: string | null;
  file: AnalyzeFileInfo;
  salary: SalaryAnalysisResult | null;
  extra: Record<string, unknown> | null;
}

export interface ProcessingError {
  code: string;
  message: string;
  retryable: boolean;
}

export interface AnalyzeResponse {
  success: boolean;
  document_id: string | null;
  document_type: DocumentType | null;
  confidence: number;
  data: AnalyzeData | null;
  validation: ValidationResult | null;
  processing: AnalyzeProcessingInfo | null;
  errors: ProcessingError[];
}