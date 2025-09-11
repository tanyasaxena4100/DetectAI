import { CommonModule } from '@angular/common';
import { HttpClient } from '@angular/common/http';
import { Component } from '@angular/core';
import { MatToolbarModule } from '@angular/material/toolbar';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';

interface Analysis {
  errors?: { line: number; description: string }[];
  fixes?: string[];
  summary?: string;
  functionality?: string[];
  conclusion?: string;
}

@Component({
  selector: 'app-root',
  standalone: true,  // ✅ if standalone
  imports: [CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './app.html',
  styleUrl: './app.scss'
})
export class App {
  // protected readonly title = signal('CodeAnalyzer');

  codeInput: string = '';       // user enters code
  responseReceived : boolean = false;
  analysisResult: Analysis = {};
//   {
//   summary: '',
//   functionality: [],
//   errors: [],
//   improvements: [],
//   conclusion: ''
// };
  selectedFile: File | null = null;
  expandedSections: { [key: string]: boolean } = {};
  loading: boolean = false;

  constructor(private http: HttpClient) {}

  analyzeCode(userCode: string) {
    this.responseReceived = false;
    this.loading = true;
    this.codeInput = userCode;
    this.http.post<any>('http://127.0.0.1:8000/analyze', { code: this.codeInput })
      .subscribe({
        next: (res) => {
          this.analysisResult = res.analysis;
          this.loading = false;
          this.responseReceived = true;
          this.expandedSections = {}; // reset expand states
        },
        error: (err) => {
          console.error('Error analyzing code', err);
          // this.analysisResult = '⚠️ Error analyzing code. Check backend connection.';
        }
      });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
  }

  uploadFile() {
    this.responseReceived = false;
    this.loading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile, this.selectedFile.name);

    this.http.post<any>('http://127.0.0.1:8000/upload', formData).subscribe(
      (response) => {
        this.analysisResult = response.analysis as Analysis;
        this.loading = false;
        this.responseReceived = true;
        this.expandedSections = {}; // reset expand states
      },
      (error) => {
        console.error("Upload error:", error);
      }
    );
  }

  toggleSection(section: string) {
    this.expandedSections[section] = !this.expandedSections[section];
  }
}
