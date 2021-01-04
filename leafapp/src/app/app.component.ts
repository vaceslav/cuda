import { HttpClient, HttpParams } from '@angular/common/http';
import { AfterViewInit, Component } from '@angular/core';
import * as L from 'leaflet';
import 'leaflet.markercluster';

@Component({
  selector: 'app-root',
  templateUrl: './app.component.html',
  styleUrls: ['./app.component.scss'],
})
export class AppComponent implements AfterViewInit {
  private map;

  title = 'leafapp';
  layer: any;

  constructor(private http: HttpClient) {}

  ngAfterViewInit(): void {
    this.map = L.map('map', {
      center: [39.8282, -98.5795],
      zoom: 3,
    });

    L.control.scale().addTo(this.map);

    this.map.on('zoomend', (d) => {
      console.log('zoom: ' + this.map.getZoom());
      this.requestJson();
    });

    const tiles = L.tileLayer(
      'https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png',
      {
        maxZoom: 19,
        attribution:
          '&copy; <a href="http://www.openstreetmap.org/copyright">OpenStreetMap</a>',
      }
    );

    tiles.addTo(this.map);
  }

  onClusterClick() {
    this.requestJson();
  }

  public  getScale(){

    // code from leaflet --> component scale
    const y = this.map.getSize().y / 2;

		var maxMeters = this.map.distance(
			this.map.containerPointToLatLng([0, y]),
      this.map.containerPointToLatLng([100, y]));
      
      var meters = this._getRoundNum(maxMeters),
        label = meters < 1000 ? meters + ' m' : (meters / 1000) + ' km';

        const ratio = meters / maxMeters;

        const pixel =  Math.round(100 * ratio);

        //normalize to 100 pixel

        const hundertPixelInMeter =  Math.round(meters / pixel * 100);

        return hundertPixelInMeter;
  }

  private _getRoundNum(num:number) {
		var pow10 = Math.pow(10, (Math.floor(num) + '').length - 1),
		    d = num / pow10;

		d = d >= 10 ? 10 :
		    d >= 5 ? 5 :
		    d >= 3 ? 3 :
		    d >= 2 ? 2 : 1;

		return pow10 * d;
	}

  private requestJson(){


    if(this.layer) {
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

      this.layer  = L.markerClusterGroup({
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
      
          return new L.DivIcon({ html: '<div><span>' + childCount + '</span></div>', className: 'marker-cluster' + c, iconSize: new L.Point(40, 40) });


          // return L.divIcon({ html: '<b>' + myCustomCount + '</b>' });
        }
      });
      const geoJsonLayer = L.geoJSON(data, {
        pointToLayer: (geoJsonPoint, latlng) => {
          geoJsonPoint.properties = geoJsonPoint.geometry.properties;
          delete geoJsonPoint.geometry.properties;
          const marker =  L.marker(latlng);
          marker.count = geoJsonPoint.properties.count;
          return marker;
        }
      });
      this.layer.addLayer(geoJsonLayer);

      

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
}
