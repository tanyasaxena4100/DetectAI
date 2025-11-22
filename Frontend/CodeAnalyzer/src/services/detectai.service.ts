import { Injectable } from '@angular/core';
import { HttpClient } from '@angular/common/http';
import { Observable } from 'rxjs';

@Injectable({ providedIn: 'root' })
export class DetectAIService {
  private baseUrl = 'http://127.0.0.1:8000';

  constructor(private http: HttpClient) {}

  analyzeBugs(code: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/analyze`, { code });
  }

  optimizeCode(code: string): Observable<any> {
    console.log('Optimizing code:', code);
    return this.http.post<any>(`${this.baseUrl}/optimize`, { code });
  }

  summarizeCode(code: string) {
    return this.http.post<any>(`${this.baseUrl}/summarize`, { code });
  }

  scanSecurity(code: string): Observable<any> {
    return this.http.post(`${this.baseUrl}/security-scan`, { code });
  }

  uploadFileToAnalyze(formData: FormData | { code: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/uploadFileToAnalyze`, formData);
  }

  uploadFileToOptimize(formData: FormData | { code: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/uploadFileToOptimize`, formData);
  }

  uploadFileToSummarize(formData: FormData | { code: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/uploadFileToSummarize`, formData);
  }

  uploadFileToScan(formData: FormData | { code: string }): Observable<any> {
    return this.http.post(`${this.baseUrl}/uploadFileToScan`, formData);
  }
}
