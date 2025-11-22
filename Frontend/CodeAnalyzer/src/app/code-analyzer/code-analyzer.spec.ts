import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeAnalyzerComponent } from './code-analyzer';

describe('CodeAnalyzer', () => {
  let component: CodeAnalyzerComponent;
  let fixture: ComponentFixture<CodeAnalyzerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeAnalyzerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeAnalyzerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
