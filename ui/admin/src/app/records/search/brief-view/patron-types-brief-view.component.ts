import { Component, Input } from '@angular/core';
import { BriefView } from './brief-view';

@Component({
  selector: 'app-patron-types-brief-view',
  template: `
  <h5>{{record.metadata.name}}</h5>

  <span *ngIf="record.metadata.description">
  {{record.metadata.description}}
  </span>
  `,
  styles: []
})
export class PatronTypesBriefViewComponent implements BriefView {

  @Input() record: any;

}