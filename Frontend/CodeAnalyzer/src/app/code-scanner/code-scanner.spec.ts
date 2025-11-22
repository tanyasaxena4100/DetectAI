import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeScannerComponent } from './code-scanner';

describe('CodeScanner', () => {
  let component: CodeScannerComponent;
  let fixture: ComponentFixture<CodeScannerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeScannerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeScannerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
