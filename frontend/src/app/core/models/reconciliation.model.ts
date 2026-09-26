import {
  BankAnalysisResult,
  SalaryAnalysisResult,
} from './api-response.model';

export type ReconciliationStatus =
  | 'matched'
  | 'multiple_candidates'
  | 'no_match'
  | 'needs_review';

export interface ReconciliationCandidate {
  transaction_date: string;
  amount: string;
  narration: string;

  amount_score: number;
  date_score: number;
  narration_score: number;
  periodicity_score: number;

  overall_score: number;
  reasons: string[];
}

export interface ReconciliationResult {
  status: ReconciliationStatus;

  salary_net_amount: string;

  candidates: ReconciliationCandidate[];

  selected_candidate: ReconciliationCandidate | null;

  confidence: number;

  explanation: string;
}

export interface ReconciliationRequest {
  salary: SalaryAnalysisResult;
  bank: BankAnalysisResult;
}

export interface ReconciliationResponse {
  success: boolean;
  result: ReconciliationResult | null;
  error: string | null;
}
