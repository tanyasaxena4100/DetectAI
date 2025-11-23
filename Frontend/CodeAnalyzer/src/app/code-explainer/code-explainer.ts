import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { FormsModule } from '@angular/forms';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router } from '@angular/router';
import { DetectAIService } from '../../services/detectai.service';

interface SummarizationResult {
  summary: string;
  detailed_explanation: string;
  key_points: string[];
}

interface SummarizationResponse {
  summarization?: SummarizationResult;
  errorMsg?: string;
}

@Component({
  selector: 'app-code-explainer',
  standalone: true,
  imports: [CommonModule,
    HttpClientModule,
    FormsModule,
    MatToolbarModule,
    MatButtonModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './code-explainer.html',
  styleUrl: './code-explainer.scss'
})
export class CodeExplainerComponent {

  @ViewChild('codeBox') codeBox!: ElementRef<HTMLTextAreaElement>;

  codeInput: string = '';
  responseReceived: boolean = false;
  loading: boolean = false;
  result: SummarizationResult | null = null;
  backendResponse: SummarizationResponse = {};
  invalidInput: boolean = false;

  selectedFile: File | null = null;
  selectedFileName: string | null = null;

  constructor(private detectAI: DetectAIService, private router: Router) {}

  goHome() {
    this.router.navigate(['/']);
  }

  summarizeCode(userCode: string) {
    if (!userCode || !userCode.trim()) return;
    this.loading = true;
    this.responseReceived = false;

    this.detectAI.summarizeCode(userCode).subscribe({
      next: (res) => {
        console.log('Summarizer response:', res);
        this.loading = false;
        this.backendResponse = res;
        if(res.errorMsg) {
          console.log('Invalid input detected - ' + this.backendResponse.errorMsg);
          this.invalidInput = true;
        } else {
          this.result = res.summarization ?? null;
          this.responseReceived = true;
          this.invalidInput = false;
        }
      },
      error: (err) => {
        console.error('Error summarizing code:', err);
        this.loading = false;
      }
    });
  }

  // optional file upload (calls a /upload or /summarize-file route if you add it)
  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.selectedFileName = event.target.files[0]?.name || null;
  }

  uploadFileToSummarize() {
    this.responseReceived = false;
    this.loading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.detectAI.uploadFileToSummarize(formData)
      .subscribe({
        next: (response) => {
          this.backendResponse = response;
          this.result = response.summarization ?? null;
          this.loading = false;
          this.responseReceived = true;
        },
        error: (error) => {
          console.error("Upload error:", error);
          this.loading = false;
        }
    });
  }

  reset(): void {
    if (this.codeBox) {
      this.codeBox.nativeElement.value = '';
    }
    this.result = null;
    this.responseReceived = false;
    this.invalidInput = false;
    this.selectedFileName = null;
  }
}
