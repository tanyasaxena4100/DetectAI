import { CommonModule } from '@angular/common';
import { HttpClient, HttpClientModule } from '@angular/common/http';
import { Component, ElementRef, ViewChild } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router } from '@angular/router';
import { DetectAIService } from '../../services/detectai.service';

interface ErrorItem {
  line: number;
  description: string;
  code: string;
  fix_suggestion: string;
  corrected_code: string;
  severity: 'Critical' | 'Major' | 'Minor';
  category: string;
}

interface Analysis {
  errors?: ErrorItem[];
  errorMsg?: string;
}

@Component({
  selector: 'app-code-analyzer',
  standalone: true,  // ✅ if standalone
  imports: [CommonModule,
    HttpClientModule,
    MatToolbarModule,
    MatButtonModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './code-analyzer.html',
  styleUrls: ['./code-analyzer.scss']
})
export class CodeAnalyzerComponent {
  codeInput: string = '';
  responseReceived : boolean = false;
  analysisResult: Analysis = {};

  selectedFile: File | null = null;
  selectedFileName: string | null = null;
  expandedSections: { [key: string]: boolean } = {};
  loading: boolean = false;
  invalidInput: boolean = false;
  backendResponse: Analysis = {};
  @ViewChild('codeBox') codeBox!: ElementRef<HTMLTextAreaElement>;

  constructor(private detectAI: DetectAIService,private http: HttpClient, private router: Router) {}

  goHome() {
    this.router.navigate(['/']);
  }

  analyzeCode(userCode: string) {
    this.responseReceived = false;
    this.loading = true;
    this.codeInput = userCode;
    this.http.post<any>('http://127.0.0.1:8000/analyze', { code: this.codeInput })
      .subscribe({
        next: (res) => {
          this.loading = false;
          this.backendResponse = res;
          console.log('response from backend:', res);
          if(res.errorMsg) {
            console.log('Invalid input detected');
            this.invalidInput = true;
          } else { 
            console.log('Invalid input not detected');
            this.analysisResult = res.analysis;
            this.invalidInput = false;
            this.responseReceived = true;
            this.expandedSections = {}; // reset expand states
          }
        },
        error: (err) => {
          console.error('Error analyzing code', err);
          // this.analysisResult = '⚠️ Error analyzing code. Check backend connection.';
        }
      });
  }

  onFileSelected(event: any) {
    this.selectedFile = event.target.files[0];
    this.selectedFileName = event.target.files[0]?.name || null;
  }

  uploadFile() {
    this.responseReceived = false;
    this.loading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile, this.selectedFile.name);

    this.http.post<any>('http://127.0.0.1:8000/uploadFileToAnalyze', formData).subscribe(
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

  uploadFileToAnalyze() {
    this.responseReceived = false;
    this.loading = true;
    if (!this.selectedFile) return;

    const formData = new FormData();
    formData.append('file', this.selectedFile);

    this.detectAI.uploadFileToAnalyze(formData)
      .subscribe({
        next: (response) => {
          this.analysisResult = response.analysis;
          this.loading = false;
          this.responseReceived = true;
          this.expandedSections = {}; 
        },
        error: (error) => {
          console.error("Upload error:", error);
          this.loading = false;
        }
      });
  }


  toggleSection(section: string) {
    this.expandedSections[section] = !this.expandedSections[section];
  }

  reset(): void {
    if (this.codeBox) {
      this.codeBox.nativeElement.value = '';  // ✅ clear the textbox
    }
    this.analysisResult = {};
    this.responseReceived = false;
    this.invalidInput = false;
    this.selectedFileName = null; // optional, clears file name
  }
}
