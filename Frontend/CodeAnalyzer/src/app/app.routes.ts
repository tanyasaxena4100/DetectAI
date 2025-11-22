import { Routes } from '@angular/router';
import { HomeComponent } from './home-component/home-component';
import { CodeAnalyzerComponent } from './code-analyzer/code-analyzer';
import { CodeExplainerComponent } from './code-explainer/code-explainer';
import { CodeOptimizerComponent } from './code-optimizer/code-optimizer';
import { CodeScannerComponent } from './code-scanner/code-scanner';


export const routes: Routes = [
    { path: '', redirectTo: 'home', pathMatch: 'full' },
    { path: '', component: HomeComponent },
    { path: 'code-analyzer', component: CodeAnalyzerComponent },
    { path: 'summarize', component: CodeExplainerComponent },
    { path: 'optimizer', component: CodeOptimizerComponent },
    { path: 'security', component: CodeScannerComponent },
];
