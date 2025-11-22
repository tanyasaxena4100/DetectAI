import { ComponentFixture, TestBed } from '@angular/core/testing';

import { CodeOptimizerComponent } from './code-optimizer';

describe('CodeOptimizer', () => {
  let component: CodeOptimizerComponent;
  let fixture: ComponentFixture<CodeOptimizerComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      imports: [CodeOptimizerComponent]
    })
    .compileComponents();

    fixture = TestBed.createComponent(CodeOptimizerComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
