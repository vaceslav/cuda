import { HttpClient, HttpParams } from '@angular/common/http';
import { AfterViewInit, Component, ElementRef, OnInit, ViewChild } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.markercluster';
import { Observable } from 'rxjs';
import { PortfolioService } from './portfolio.service';
import { map } from 'rxjs/operators';
import { Chart } from 'chart.js';
import { MatCheckboxChange } from '@angular/material/checkbox';
import { TREE_DATA } from './chart.options';
import { MatTreeNestedDataSource } from '@angular/material/tree';
import { NestedTreeControl } from '@angular/cdk/tree';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements AfterViewInit, OnInit {
  private map;

  @ViewChild('earthquake') myEarthquakeChartRef: ElementRef;
  @ViewChild('hail') myHailChartRef: ElementRef;
  @ViewChild('tornado') myTornadoChartRef: ElementRef;
  @ViewChild('heat') myHeatChartRef: ElementRef;

  @ViewChild('hCanvas') diagrammChartRef: ElementRef;

  selectedPortfolio: string = 'FAB_SampleLocations_100k_0';

  title = 'leafapp';
  layer: any;
  long: number;
  lat: number;
  portfolios$: Observable<string[]>;
  earthquakeChart: Chart;
  hailChart: Chart;
  tornadoChart: Chart;
  heatChart: Chart;
  countires$: Observable<any>;
  buildings$: Observable<any[]>;
  clusterDuration$: Observable<number>;
  analyzeDuration$: Observable<number>;
  locationCount$: Observable<number>;
  tsiSum$: Observable<number>;
  lossesSum$: Observable<number>;
  modelDuration: any;

  advancedata$: Observable<any>;

  constructor(private http: HttpClient, private portfolioService: PortfolioService) {}

  ngOnInit(): void {
    this.portfolios$ = this.portfolioService.list().pipe(map((d) => d.portfolios));

    this.portfolioService.setPortfolio(this.selectedPortfolio);

    this.countires$ = this.portfolioService.countires$;

    this.buildings$ = this.portfolioService.buildings$;

    this.clusterDuration$ = this.portfolioService.clusterDuration$;

    this.advancedata$ = this.portfolioService.advancedata$;

    this.portfolioService.analyses$.pipe(map((data) => data.earthquake)).subscribe((earthquake) => {
      const data = this.getCounts(earthquake, 4);
      // const data = [earthquake['1']['pcount'], earthquake['2']['pcount'], earthquake['3']['pcount'], earthquake['4']['pcount']];
      this.earthquakeChart.data.datasets[0].data = data;
      this.earthquakeChart.update();
    });

    this.portfolioService.analyses$.pipe(map((data) => data.hail)).subscribe((hail) => {
      const data = this.getCounts(hail, 6);
      // const data = [hail['1']['pcount'], hail['2']['pcount'], hail['3']['pcount'], hail['4']['pcount'], hail['5']['pcount'], hail['6']['pcount']];
      this.hailChart.data.datasets[0].data = data;
      this.hailChart.update();
    });

    this.portfolioService.analyses$.pipe(map((data) => data.tornado)).subscribe((tornado) => {
      const data = this.getCounts(tornado, 5);
      // const data = [tornado['1']['pcount'], tornado['2']['pcount'], tornado['3']['pcount'], tornado['4']['pcount'], tornado['5']['pcount']];
      this.tornadoChart.data.datasets[0].data = data;
      this.tornadoChart.update();
    });

    this.portfolioService.analyses$.pipe(map((data) => data.heat_wave)).subscribe((heat) => {
      const data = this.getCounts(heat, 3);
      // const data = [heat['1']['pcount'], heat['2']['pcount'], heat['3']['pcount']];
      this.heatChart.data.datasets[0].data = data;
      this.heatChart.update();
    });

    this.analyzeDuration$ = this.portfolioService.analyses$.pipe(map((data) => data.duration));

    this.locationCount$ = this.portfolioService.analyses$.pipe(map((data) => data.count));

    this.tsiSum$ = this.portfolioService.analyses$.pipe(map((data) => data.tsiSum));

    this.lossesSum$ = this.portfolioService.analyses$.pipe(map((data) => data.lossesSum));
  }

  private getCounts(data, count) {
    const result = [];
    for (let i = 1; i <= count; i++) {
      if (data[i]) {
        result.push(data[i]['pcount']);
      } else {
        result.push(0);
      }
    }

    return result;
  }

  ngAfterViewInit(): void {
    this.createCharts();

    this.map = L.map('map', {
      center: [39.8282, -98.5795],
      zoom: 3,
    });

    L.control.scale().addTo(this.map);

    const tiles = L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
      maxZoom: 19,
      attribution: '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
    });

    tiles.addTo(this.map);
    this.addLatLongControl();

    this.portfolioService.setMap(this.map);
  }

  addImageLayer() {
    this.portfolioService.showImage();
  }

  addLatLongControl() {
    this.map.addEventListener('mousemove', (event) => {
      let lat = Math.round(event.latlng.lat * 100000) / 100000;
      let lng = Math.round(event.latlng.lng * 100000) / 100000;
      this.long = lng;
      this.lat = lat;
    });

    var drawnItems = new L.FeatureGroup();
    this.map.addLayer(drawnItems);
    var drawControl = new L.Control.Draw({
      draw: {
        marker: undefined,
        circle: undefined,
        circlemarker: undefined,
        polyline: undefined,
      },
      edit: {
        featureGroup: drawnItems,
      },
    });
    this.map.addControl(drawControl);

    this.map.on(L.Draw.Event.CREATED, (e) => {
      const layer = e.layer;

      drawnItems.addLayer(layer);
      this.portfolioService.setFilterPolygon(layer);
    });
  }

  showClick() {
    this.portfolioService.showCluster();
  }

  createCharts() {
    this.earthquakeChart = this.createChartInternal(this.myEarthquakeChartRef, 'Earthquake', 'earthquake', 4);

    this.hailChart = this.createChartInternal(this.myHailChartRef, 'Hail', 'hail', 6);

    this.tornadoChart = this.createChartInternal(this.myTornadoChartRef, 'Tornado', 'tornado', 5);

    this.heatChart = this.createChartInternal(this.myHeatChartRef, 'Heat waves', 'heat_wave', 3);
  }

  private createChartInternal(elemenRef: ElementRef, title: string, hazardName: string, count: number) {
    const ctx = elemenRef.nativeElement.getContext('2d');

    const labels = ['Zone 1', 'Zone 2', 'Zone 3', 'Zone 4', 'Zone 5', 'Zone 6'];
    labels.length = count;

    const chart: Chart = new Chart(ctx, {
      type: 'doughnut',
      data: {
        labels: labels,
        datasets: [
          {
            data: [],
            backgroundColor: ['rgba(255, 99, 132, 0.3)', 'rgba(54, 162, 235, 0.2)', 'rgba(255, 206, 86, 0.2)', 'rgba(75, 192, 192, 0.2)', 'rgba(153, 102, 255, 0.2)', 'rgba(255, 159, 64, 0.2)'],
            borderColor: ['rgba(255, 99, 132, 1)', 'rgba(54, 162, 235, 1)', 'rgba(255, 206, 86, 1)', 'rgba(75, 192, 192, 1)', 'rgba(153, 102, 255, 1)', 'rgba(255, 159, 64, 1)'],
            borderWidth: 1,
          },
        ],
      },
      options: {
        title: {
          display: true,
          text: title,
        },
        legend: {
          position: 'left',
        },
      },
    });

    const canvas = elemenRef.nativeElement;
    canvas.onclick = (evt) => {
      const hit = chart.getElementAtEvent(evt);
      if (hit && hit[0]) {
        const index = hit[0]['_index'];
        // const value = chart.data.datasets[0].data[index];
        this.portfolioService.setFilter(hazardName, index + 1);
      }
    };

    return chart;
  }

  earthQuakeChange($event) {
    this.portfolioService.setFilter('earthquake', $event);
  }

  countryClick($event: MatCheckboxChange, c) {
    this.portfolioService.setFilterCountry(c.country, $event.checked);
  }

  buildingClick($event: MatCheckboxChange, c) {
    this.portfolioService.setFilterBuilding(c.name, $event.checked);
  }

  portfolioChange($event) {
    this.selectedPortfolio = $event.value;
    this.portfolioService.setPortfolio($event.value);
  }

  treeControl = new NestedTreeControl<any>((node) => node.children);
  dataSource = new MatTreeNestedDataSource<any>();
  hasChild = (_: number, node: any) => !!node.children && node.children.length > 0;

  addDiagramm() {
    this.portfolioService.getHierarchicalData().subscribe((data) => {
      const items = JSON.parse(data.hierarchical);
      const duration = items['duration'];
      this.modelDuration = duration;
      this.dataSource.data = [items];
    });
    // this.dataSource.data = TREE_DATA;
  }
}
