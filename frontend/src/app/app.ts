import { Component, OnInit, inject } from '@angular/core';

import { ApiService } from './core/services/api.service';
import { HealthResponse } from './core/models/api-response.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly apiService = inject(ApiService);

  health: HealthResponse | null = null;
  error = '';

  ngOnInit(): void {
    this.apiService.health().subscribe({
      next: (response) => {
        this.health = response;
      },
      error: (error) => {
        console.error('Backend health check failed:', error);
        this.error = 'Unable to connect to the backend.';
      },
    });
  }
}