import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import * as L from 'leaflet';
import { ReplaySubject } from 'rxjs';
import { map } from 'rxjs/operators';

@Injectable({ providedIn: 'root' })
export class PortfolioService {
  private map;

  private layers: { [portfolioName: string]: any } = {};

  private analyzesSubject = new ReplaySubject<any>(1);
  public analyses$ = this.analyzesSubject
    .asObservable()
    .pipe(map((data) => data.analyze));

  private _filter = {};

  constructor(private http: HttpClient) {}

  list() {
    return this.http.get<{ portfolios: string[] }>('api/portfolios');
  }

  setFilter(argName: string, value: any) {
    if (this._filter[argName] && this._filter[argName] === value) {
      delete this._filter[argName];
    } else {
      this._filter[argName] = value;
    }

    this.refresh();
  }

  showCluster(map, portfolioName) {
    this.setMap(map);

    const clusterLayer = this.createClusterLayer();
    this.layers[portfolioName] = clusterLayer;
    clusterLayer.addTo(this.map);

    this.refresh();
  }

  private refresh() {
    for (const item in this.layers) {
      this.refreshLayer(item);
      this.requestAnalyze(item);
    }
  }

  requestAnalyze(portfolioName: string) {
    const params = new HttpParams().append('portfolio', portfolioName);

    this.http
      .post('api/analyze', { filter: this._filter }, { params })
      .subscribe((data) => {
        this.analyzesSubject.next(data);
      });
  }

  private refreshLayer(portfolioName) {
    const clusterLayer = this.layers[portfolioName];
    clusterLayer.clearLayers();

    const request = this.requestClusterData(portfolioName).subscribe((data) => {
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

      clusterLayer.addLayer(geoJsonLayer);
    });
  }

  private requestClusterData(portfolioName) {
    const params = this.getClusterParams(portfolioName);

    return this.http.post('api/cluster', { filter: this._filter }, { params });
  }

  private createClusterLayer() {
    const clusterLayer = L.markerClusterGroup({
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

    return clusterLayer;
  }

  private getClusterParams(portfolioName) {
    const params = new HttpParams()
      .append('portfolio', portfolioName)
      .append('zoom', this.map.getZoom())
      .append('extent', this.map.getBounds().toBBoxString())
      .append('scale', this.getScale() + '');

    return params;
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

  private setMap(map) {
    if (!this.map) {
      this.map = map;

      //   this.map.on('zoomend', (d) => {
      //     this.refresh();
      //   });

      this.map.on('moveend', (d) => {
        this.refresh();
      });
    }
  }
}
