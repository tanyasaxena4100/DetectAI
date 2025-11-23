import { Component, ElementRef, ViewChild } from '@angular/core';
import { DetectAIService } from '../../services/detectai.service';
import { Router } from '@angular/router';
import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';

interface OptimizationResult {
  optimized_code: string;
  explanation: string[];
  complexity_analysis: {
    before: string;
    after: string;
  };
  remarks: string;
}

interface OptimizationResponse {
  optimization?: OptimizationResult;
  errorMsg?: string;
}

@Component({
  selector: 'app-code-optimizer',
  standalone: true,
  imports: [CommonModule,
    HttpClientModule,
    MatToolbarModule,
    MatButtonModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './code-optimizer.html',
  styleUrl: './code-optimizer.scss'
})
export class CodeOptimizerComponent {
  @ViewChild('codeBox') codeBox!: ElementRef<HTMLTextAreaElement>;

  codeInput: string = '';
  responseReceived: boolean = false;
  loading: boolean = false;
  result: any = {};
  invalidInput: boolean = false;
  backendResponse: OptimizationResponse = {};
  analysisResult: OptimizationResponse = {};

  selectedFile: File | null = null;
  selectedFileName: string | null = null;

  constructor(private detectAI: DetectAIService, private router: Router) {}

  goHome() {
    this.router.navigate(['/']);
  }

  optimizeCode(userCode: string) {
    if (!userCode.trim()) return;
    this.loading = true;
    this.responseReceived = false;

    this.detectAI.optimizeCode(userCode).subscribe({
      next: (res) => {
        console.log('Optimizer response:', res);
        this.loading = false;
        this.backendResponse = res;
        if(res.errorMsg) {
          console.log('Invalid input detected');
          this.invalidInput = true;
        } else {
          this.result = res.optimization
          this.invalidInput = false;
          this.responseReceived = true;
        }
      },
      error: (err) => {
        console.error('Error analyzing code:', err);
        this.loading = false;
      }
    });
  }


  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.selectedFileName = event.target.files[0]?.name || null;
  }

  uploadFileToOptimize() {
    this.responseReceived = false;
    this.loading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.detectAI.uploadFileToOptimize(formData)
      .subscribe({
        next: (response) => {
          this.backendResponse = response;
          this.result = response.optimization
          this.loading = false;
          this.responseReceived = true;
          // this.expandedSections = {}; 
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
    this.result = {};
    this.invalidInput = false;
    this.responseReceived = false;
    this.selectedFileName = null;
  }
}
