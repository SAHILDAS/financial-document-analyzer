import { Component, OnInit, inject, signal } from '@angular/core';

import { ApiService } from './core/services/api.service';
import { HealthResponse } from './core/models/api-response.model';

@Component({
  selector: 'app-root',
  templateUrl: './app.html',
  styleUrl: './app.scss',
})
export class App implements OnInit {
  private readonly apiService = inject(ApiService);

  readonly health = signal<HealthResponse | null>(null);
  readonly error = signal('');

  ngOnInit(): void {
    this.apiService.health().subscribe({
      next: (response) => {
        this.health.set(response);
      },
      error: (error) => {
        console.error('Backend health check failed:', error);
        this.error.set('Unable to connect to the backend.');
      },
    });
  }
}
