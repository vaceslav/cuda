import { ComponentFixture, TestBed } from '@angular/core/testing';

import { AdvanceItemComponent } from './advance-item.component';

describe('AdvanceItemComponent', () => {
  let component: AdvanceItemComponent;
  let fixture: ComponentFixture<AdvanceItemComponent>;

  beforeEach(async () => {
    await TestBed.configureTestingModule({
      declarations: [ AdvanceItemComponent ]
    })
    .compileComponents();
  });

  beforeEach(() => {
    fixture = TestBed.createComponent(AdvanceItemComponent);
    component = fixture.componentInstance;
    fixture.detectChanges();
  });

  it('should create', () => {
    expect(component).toBeTruthy();
  });
});
