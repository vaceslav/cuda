import { Component, Input, OnInit } from '@angular/core';

@Component({
  selector: 'app-advance-item',
  templateUrl: './advance-item.component.html',
  styleUrls: ['./advance-item.component.scss'],
})
export class AdvanceItemComponent implements OnInit {
  @Input() item: any;
  counts: any[];

  colors = ['rgba(255, 99, 132, 0.3)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'];
  tsis: any[];
  lossess: any[];
  title: any;

  constructor() {}

  ngOnInit(): void {
    let sumCount = 0;
    let sumTsi = 0;
    let sumLosses = 0;
    for (const key in this.item) {
      const sumItem = this.item[key];
      sumCount = sumCount + sumItem.pcount;
      sumTsi = sumTsi + sumItem.tsi;
      sumLosses = sumLosses + sumItem.losses;
    }

    this.counts = [];
    this.tsis = [];
    this.lossess = [];

    let index = 0;
    for (const key in this.item) {
      const subItem = this.item[key];

      this.title = Object.keys(subItem)[0];

      const countProcent = (100 / sumCount) * subItem.pcount;
      const tsiProcent = (100 / sumTsi) * subItem.tsi;
      const lossesProcent = (100 / sumLosses) * subItem.losses;

      // debugger;

      this.counts.push({
        percent: countProcent,
        value: subItem.pcount,
        color: this.colors[+key - 1],
      });

      this.tsis.push({
        percent: tsiProcent,
        value: subItem.tsi,
        color: this.colors[+key - 1],
      });

      this.lossess.push({
        percent: lossesProcent,
        value: subItem.losses,
        color: this.colors[+key - 1],
      });

      index++;

      // sumCount = sumCount + sumItem.pcount;
      // sumTsi = sumTsi + sumItem.tsi;
      // sumLosses = sumLosses = sumItem.losses;
    }

    const t = this.item;
  }
}
