import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeExplainerComponent } from './code-explainer';

describe('CodeExplainer', () => {
  let component: CodeExplainerComponent;
  let fixture: ComponentFixture<CodeExplainerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeExplainerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeExplainerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
