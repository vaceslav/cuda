import { HttpClient, HttpParams } from '@angular/common/http';
import { Injectable } from '@angular/core';
import { DivIcon, geoJSON, imageOverlay, Marker, marker, Point, Polygon, Polyline } from 'leaflet';
import { ReplaySubject, Subscription } from 'rxjs';
import { map } from 'rxjs/operators';
import * as WKT from 'terraformer-wkt-parser';
import { ClusterResult } from './typings';

@Injectable({ providedIn: 'root' })
export class PortfolioService {
  private map;

  private _clusterLayer: any;
  private _imageLayer: any;

  private analyzesSubject = new ReplaySubject<any>(1);

  private clusterDurationSubject = new ReplaySubject<number>(1);

  public clusterDuration$ = this.clusterDurationSubject.asObservable();

  public analyses$ = this.analyzesSubject.asObservable().pipe(map((data) => data.analyze));

  public countires$ = this.analyses$.pipe(
    map((data) => data.countries),
    map((countries) => {
      const result = [];
      for (const item in countries) {
        result.push({
          country: item,
          data: countries[item],
          checked: this._filter.countries.indexOf(item) !== -1,
        });
      }

      result.sort((a, b) => b.data.pcount - a.data.pcount);

      return result;
    })
  );

  buildings$ = this.analyses$.pipe(
    map((data) => data.building),
    map((building) => {
      const result = [];
      for (const item in building) {
        result.push({
          name: item,
          data: building[item],
          checked: this._filter.buildings.indexOf(item) !== -1,
        });
      }

      result.sort((a, b) => b.data.pcount - a.data.pcount);

      return result;
    })
  );

  advancedata$ = this.analyses$.pipe(
    map((data) => {
      return [data.earthquake, data.hail, data.heat_wave, data.tornado];
    })
  );

  private _filter = {
    countries: [],
    buildings: [],
    polygons: [],
  };

  private _portfolioRequests: Subscription[] = [];
  private _portfolio: string;

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

    this.drawLayers();
    this.requestAnalyze();
  }

  setFilterCountry(country: string, checked: boolean) {
    if (!checked) {
      const index = this._filter.countries.indexOf(country);
      this._filter.countries.splice(index, 1);
    } else {
      this._filter.countries.push(country);
    }

    this.drawLayers();
    this.requestAnalyze();
  }

  setFilterBuilding(name: any, checked: boolean) {
    if (!checked) {
      const index = this._filter.buildings.indexOf(name);
      this._filter.buildings.splice(index, 1);
    } else {
      this._filter.buildings.push(name);
    }

    this.drawLayers();
    this.requestAnalyze();
  }

  showCluster() {
    const clusterLayer = this.createClusterLayer();
    this._clusterLayer = clusterLayer;
    clusterLayer.addTo(this.map);

    this.drawPortfolio();
    this.requestAnalyze();
  }

  private drawLayers() {
    for (const sub of this._portfolioRequests) {
      sub.unsubscribe();
    }
    this._portfolioRequests.length = 0;

    if (this._clusterLayer) {
      this.drawPortfolio();
    }

    if (this._imageLayer) {
      this.rerenderImageLayer();
    }
  }

  private requestAnalyze() {
    this.requestPortfolioAnalyze();
  }

  requestPortfolioAnalyze() {
    const params = new HttpParams().append('portfolio', this._portfolio);

    this.http.post('api/analyze', { filter: this._filter }, { params }).subscribe((data) => {
      this.analyzesSubject.next(data);
    });
  }

  private drawPortfolio() {
    this._clusterLayer.clearLayers();

    const request = this.requestClusterData().subscribe((data) => {
      this._portfolioRequests.splice(this._portfolioRequests.indexOf(request), 1);

      this.clusterDurationSubject.next(data.duration);

      const geoJsonLayer = geoJSON(data.items as any, {
        pointToLayer: (geoJsonPoint, latlng) => {
          const props = geoJsonPoint.geometry['properties'];
          delete geoJsonPoint.geometry['properties'];

          const myMarker = marker(latlng);
          myMarker['count'] = props.count;
          myMarker['tsi'] = props.tsi;
          return myMarker;
        },
      });
      this, this._clusterLayer.addLayer(geoJsonLayer);
    });

    this._portfolioRequests.push(request);
  }

  private requestClusterData() {
    const params = this.getClusterParams();

    return this.http.post<ClusterResult>('api/cluster', { filter: this._filter }, { params });
  }

  private createClusterLayer() {
    const L: any = window.L as any;
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

        return new DivIcon({
          html: '<div><span>' + childCount + '</span></div>',
          className: 'marker-cluster' + c,
          iconSize: new Point(40, 40),
        });

        // return L.divIcon({ html: '<b>' + myCustomCount + '</b>' });
      },
    });

    return clusterLayer;
  }

  private getClusterParams() {
    const params = new HttpParams()
      .append('portfolio', this._portfolio)
      .append('zoom', this.map.getZoom())
      .append('extent', this.map.getBounds().toBBoxString())
      .append('scale', this.getScale() + '');

    return params;
  }

  public getScale() {
    // code from leaflet --> component scale
    const y = this.map.getSize().y / 2;

    var maxMeters = this.map.distance(this.map.containerPointToLatLng([0, y]), this.map.containerPointToLatLng([100, y]));

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

  public setMap(map) {
    if (!this.map) {
      this.map = map;

      //   this.map.on('zoomend', (d) => {
      //     this.refresh();
      //   });

      this.map.on('moveend', (d) => {
        this.drawLayers();
      });
    }
  }

  showImage() {
    this.rerenderImageLayer();
    this.requestAnalyze();
  }

  rerenderImageLayer() {
    let params = this.getClusterParams();

    const size = this.map.getSize();
    params = params.append('width', size.x).append('height', size.y);

    const subscription = this.http.post('api/image', { filter: this._filter }, { params, responseType: 'blob' }).subscribe((blob) => {
      var urlCreator = window.URL || window.webkitURL;
      var imageUrl = urlCreator.createObjectURL(blob);
      if (!this._imageLayer) {
        this._imageLayer = imageOverlay(imageUrl, this.map.getBounds());
        this._imageLayer.addTo(this.map);
      } else {
        this._imageLayer.setUrl(imageUrl);
        this._imageLayer.setBounds(this.map.getBounds());
      }
      // L.imageOverlay(imageUrl, this.map.getBounds()).addTo(this.map);
    });

    this._portfolioRequests.push(subscription);
  }

  setPortfolio(portfolio: string) {
    this._portfolio = portfolio;
    this.drawLayers();
    this.requestAnalyze();
  }

  setFilterPolygon(layer: any) {
    var geojson = layer.toGeoJSON();
    var wkt = WKT.convert(geojson.geometry);
    this._filter.polygons.push(wkt);
    this.drawLayers();
    this.requestAnalyze();
  }

  getHierarchicalData() {
    const params = new HttpParams().append('portfolio', this._portfolio);

    return this.http.post<any>('api/hierarchical', { filter: this._filter }, { params });
  }
}
