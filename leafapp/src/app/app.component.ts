import { HttpClient, HttpParams } from '@angular/common/http';
import {
  AfterViewInit,
  Component,
  ElementRef,
  OnInit,
  ViewChild,
} from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.markercluster';
import { Observable } from 'rxjs';
import { PortfolioService } from './portfolio.service';
import { map } from 'rxjs/operators';
import { Chart } from 'chart.js';

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

  selectedPortfolio: string = 'FAB_SampleLocations_100k_0';

  title = 'leafapp';
  layer: any;

  clusterTsi: number = undefined;
  clusterCount: number = undefined;
  long: number;
  lat: number;
  portfolios$: Observable<string[]>;
  earthquakeChart: Chart;
  hailChart: Chart;
  tornadoChart: Chart;
  heatChart: Chart;

  constructor(
    private http: HttpClient,
    private portfolioService: PortfolioService
  ) {}

  ngOnInit(): void {
    this.portfolios$ = this.portfolioService
      .list()
      .pipe(map((d) => d.portfolios));

    this.portfolioService.analyses$
      .pipe(map((data) => data.earthquake))
      .subscribe((earthquake) => {
        const data = [
          earthquake['1'],
          earthquake['2'],
          earthquake['3'],
          earthquake['4'],
        ];
        this.earthquakeChart.data.datasets[0].data = data;
        this.earthquakeChart.update();
      });

    this.portfolioService.analyses$
      .pipe(map((data) => data.hail))
      .subscribe((hail) => {
        const data = [
          hail['1'],
          hail['2'],
          hail['3'],
          hail['4'],
          hail['5'],
          hail['6'],
        ];
        this.hailChart.data.datasets[0].data = data;
        this.hailChart.update();
      });

    this.portfolioService.analyses$
      .pipe(map((data) => data.tornado))
      .subscribe((tornado) => {
        const data = [
          tornado['1'],
          tornado['2'],
          tornado['3'],
          tornado['4'],
          tornado['5'],
        ];
        this.tornadoChart.data.datasets[0].data = data;
        this.tornadoChart.update();
      });

    this.portfolioService.analyses$
      .pipe(map((data) => data.heat_wave))
      .subscribe((heat) => {
        const data = [heat['1'], heat['2'], heat['3']];
        this.heatChart.data.datasets[0].data = data;
        this.heatChart.update();
      });
  }

  ngAfterViewInit(): void {
    this.createCharts();

    this.map = L.map('map', {
      center: [39.8282, -98.5795],
      zoom: 3,
    });

    L.control.scale().addTo(this.map);

    const tiles = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }
    );

    tiles.addTo(this.map);

    this.addLatLongControl();
  }

  onClusterClick() {
    this.requestJson();
  }

  public getScale() {
    // code from leaflet --> component scale
    const y = this.map.getSize().y / 2;

    var maxMeters = this.map.distance(
      this.map.containerPointToLatLng([0, y]),
      this.map.containerPointToLatLng([100, y])
    );

    var meters = this._getRoundNum(maxMeters),
      label = meters < 1000 ? meters + ' m' : meters / 1000 + ' km';

    const ratio = meters / maxMeters;

    const pixel = Math.round(100 * ratio);

    //normalize to 100 pixel

    const hundertPixelInMeter = Math.round((meters / pixel) * 100);

    return hundertPixelInMeter;
  }

  private _getRoundNum(num: number) {
    var pow10 = Math.pow(10, (Math.floor(num) + '').length - 1),
      d = num / pow10;

    d = d >= 10 ? 10 : d >= 5 ? 5 : d >= 3 ? 3 : d >= 2 ? 2 : 1;

    return pow10 * d;
  }

  addImageLayer() {
    var nexrad = L.tileLayer.wms('http://localhost:8888/image', {
      layers: 'nexrad-n0r-900913',
      format: 'image/png',
      transparent: true,
      attribution: 'Weather data © 2012 IEM Nexrad',
    });

    // crs: L.CRS.EPSG4326

    nexrad.addTo(this.map);
  }

  addLatLongControl() {
    this.map.addEventListener('mousemove', (event) => {
      let lat = Math.round(event.latlng.lat * 100000) / 100000;
      let lng = Math.round(event.latlng.lng * 100000) / 100000;
      this.long = lng;
      this.lat = lat;
    });
  }

  private requestJson() {
    if (this.layer) {
      this.map.removeLayer(this.layer);
      this.layer = undefined;
    }

    const params = new HttpParams()
      .append('zoom', this.map.getZoom())
      .append('extent', this.map.getBounds().toBBoxString())
      .append('scale', this.getScale() + '');

    this.http.get('http://localhost:8888', { params }).subscribe((data) => {
      var geojsonMarkerOptions = {
        radius: 8,
        fillColor: '#ff7800',
        color: '#000',
        weight: 1,
        opacity: 1,
        fillOpacity: 0.8,
      };

      this.layer = L.markerClusterGroup({
        zoomToBoundsOnClick: false,
        iconCreateFunction: (cluster) => {
          const childMarkers = cluster.getAllChildMarkers();
          let childCount = 0;
          for (const childMarker of childMarkers) {
            childCount += childMarker.count; // or whatever computation you need
          }

          var c = ' marker-cluster-';
          if (childCount < 10) {
            c += 'small';
          } else if (childCount < 100) {
            c += 'medium';
          } else {
            c += 'large';
          }

          return new L.DivIcon({
            html: '<div><span>' + childCount + '</span></div>',
            className: 'marker-cluster' + c,
            iconSize: new L.Point(40, 40),
          });

          // return L.divIcon({ html: '<b>' + myCustomCount + '</b>' });
        },
      });
      const geoJsonLayer = L.geoJSON(data, {
        pointToLayer: (geoJsonPoint, latlng) => {
          geoJsonPoint.properties = geoJsonPoint.geometry.properties;
          delete geoJsonPoint.geometry.properties;
          const marker = L.marker(latlng);
          marker.count = geoJsonPoint.properties.count;
          marker.tsi = geoJsonPoint.properties.tsi;
          return marker;
        },
      });
      this.layer.addLayer(geoJsonLayer);

      this.layer.on('clusterclick', (a) => {
        const childMarkers = a.layer.getAllChildMarkers();
        let tsi = 0;
        let count = 0;

        for (const childMarker of childMarkers) {
          tsi += childMarker.tsi; // or whatever computation you need
          count += childMarker.count; // or whatever computation you need
        }

        this.clusterTsi = tsi;
        this.clusterCount = count;
      });

      // this.layer = L.geoJSON(data, {
      //   pointToLayer: (feature, latlng) => {
      //     feature.properties = feature.geometry.properties;
      //     delete feature.geometry.properties;

      //     var icon = L.divIcon({
      //       html: '<div class="txt">' + feature.properties.count + '</div>',
      //       className: 'circle-with-txt',
      //       iconSize: [40, 40]
      //     });

      //     var marker = L.marker(latlng, {
      //       icon: icon
      //     });

      //     const circle = L.circleMarker(latlng, {
      //       ...geojsonMarkerOptions,
      //       radius: (feature.properties.count + '').length * 6
      //     });

      //     var group = L.layerGroup([circle, marker]);
      //     return(group);
      //   },
      //   style: (feature) => {
      //     return {
      //       color: '#ff0000'
      //     }
      //   },
      // });

      this.layer.addTo(this.map);
    });
  }

  showClick() {
    this.portfolioService.showCluster(this.map, this.selectedPortfolio);
  }

  createCharts() {
    this.earthquakeChart = this.createChartInternal(
      this.myEarthquakeChartRef,
      'Earthquake',
      'earthquake',
      4
    );

    this.hailChart = this.createChartInternal(
      this.myHailChartRef,
      'Hail',
      'hail',
      6
    );

    this.tornadoChart = this.createChartInternal(
      this.myTornadoChartRef,
      'Tornado',
      'tornado',
      5
    );

    this.heatChart = this.createChartInternal(
      this.myHeatChartRef,
      'Heat waves',
      'heat_wave',
      3
    );
  }

  private createChartInternal(
    elemenRef: ElementRef,
    title: string,
    hazardName: string,
    count: number
  ) {
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
            backgroundColor: [
              'rgba(255, 99, 132, 0.3)',
              'rgba(54, 162, 235, 0.2)',
              'rgba(255, 206, 86, 0.2)',
              'rgba(75, 192, 192, 0.2)',
              'rgba(153, 102, 255, 0.2)',
              'rgba(255, 159, 64, 0.2)',
            ],
            borderColor: [
              'rgba(255, 99, 132, 1)',
              'rgba(54, 162, 235, 1)',
              'rgba(255, 206, 86, 1)',
              'rgba(75, 192, 192, 1)',
              'rgba(153, 102, 255, 1)',
              'rgba(255, 159, 64, 1)',
            ],
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
}
