import { CommonModule } from '@angular/common';
import { Component } from '@angular/core';
import { MatButtonModule } from '@angular/material/button';
import { MatGridListModule } from '@angular/material/grid-list';
import { MatProgressSpinnerModule } from '@angular/material/progress-spinner';
import { MatToolbarModule } from '@angular/material/toolbar';
import { Router, RouterOutlet } from '@angular/router';

@Component({
  selector: 'app-home-component',
  standalone: true,
  imports: [CommonModule,
    MatToolbarModule,
    MatButtonModule,
    MatGridListModule,
    MatProgressSpinnerModule
  ],
  templateUrl: './home-component.html',
  styleUrl: './home-component.scss'
})
export class HomeComponent {

  constructor(private router: Router) {}
  
  navigateTo(tabIndex: number) {
    if(tabIndex === 1) {
      this.router.navigate(['/code-analyzer']);
    }
    if(tabIndex === 2) {
      this.router.navigate(['/optimizer']);
    }
    if(tabIndex === 3) {
      this.router.navigate(['/summarize']);
    }
    if(tabIndex === 4) {
      this.router.navigate(['/security']);
    }
  }
}
