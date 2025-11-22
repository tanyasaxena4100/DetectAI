import { CommonModule } from '@angular/common';
import { HttpClientModule } from '@angular/common/http';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { DetectAIService } from '../../services/detectai.service';
import { Router } from '@angular/router';

interface Vulnerability {
  line: number;
  description: string;
  vulnerability_type: string;
  severity: 'Critical' | 'High' | 'Medium' | 'Low';
  fix_suggestion: string;
}

interface ScanResult {
  vulnerabilities: Vulnerability[];
  summary: string;
  recommendations: string[];
}

interface ScanResponse {
  scan?: ScanResult;
  errorMsg?: string;
}

@Component({
  selector: 'app-code-scanner',
  imports: [
    CommonModule,
    HttpClientModule,
    MatToolbarModule,
    MatButtonModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './code-scanner.html',
  styleUrl: './code-scanner.scss'
})
export class CodeScannerComponent {
  @ViewChild('codeBox') codeBox!: ElementRef<HTMLTextAreaElement>;

  responseReceived = false;
  loading = false;
  result: ScanResult | null = null;
  selectedFileName: string | null = null;
  selectedFile: File | null = null;

  constructor(private detectAI: DetectAIService, private router: Router) {}

  goHome() {
    this.router.navigate(['/']);
  }

  scanCode(userCode: string) {
    if (!userCode.trim()) return;
    this.loading = true;
    this.responseReceived = false;

    this.detectAI.scanSecurity(userCode).subscribe({
      next: (res) => {
        console.log('Scan response:', res);
        this.loading = false;
        this.result = res.scan ?? null;
        this.responseReceived = true;
      },
      error: (err) => {
        console.error('Error scanning code:', err);
        this.loading = false;
      }
    });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.selectedFileName = event.target.files[0]?.name || null;
  }

  uploadFileToScan() {
    this.responseReceived = false;
    this.loading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.detectAI.uploadFileToScan(formData)
      .subscribe({
        next: (response) => {
          this.result = response.scan ?? null;
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
    this.selectedFileName = null;
  }
}
