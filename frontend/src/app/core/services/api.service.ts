import { Injectable, inject } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

import {
  AnalyzeResponse,
  HealthResponse,
} from '../models/api-response.model';

@Injectable({
  providedIn: 'root',
})
export class ApiService {
  private readonly http = inject(HttpClient);

  private readonly baseUrl = 'http://127.0.0.1:8000/api';

  health(): Observable<HealthResponse> {
    return this.http.get<HealthResponse>(
      `${this.baseUrl}/health`,
    );
  }

  analyzeDocument(file: File): Observable<AnalyzeResponse> {
    const formData = new FormData();

    formData.append('file', file);

    return this.http.post<AnalyzeResponse>(
      `${this.baseUrl}/documents/analyze`,
      formData,
    );
  }
}