var mapstyles = require("./mapstyles.js");

import OLMap from "ol/map";
import OLView from "ol/view";
import OLFeature from "ol/feature";
import OLStyle from "ol/style/style";
import OLStroke from "ol/style/stroke";
import OLPoint from "ol/geom/point";
import olproj from "ol/proj";
import OLProjection from "ol/proj/projection";
import oltilegrid from "ol/tilegrid";
import OLGeoJSON from "ol/format/geojson";

import OLControl from "ol/control/control";
import OLControlFullScreen from "ol/control/fullscreen";

import OLSourceOSM from "ol/source/osm";
import OLSourceVector from "ol/source/vector";
import OLSourceVectorTile from "ol/source/vectortile";

import OLTile from "ol/layer/tile";
import OLLayerVector from "ol/layer/vector";
import OLLayerVectorTile from "ol/layer/vectortile";


// TILE SOURCES
//    osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png");  // needs an API key
//    osmSource.setUrl("https://a.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=52962bab91de4e789491bc1f5ed4956e");
//    osmSource.setUrl("https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png");
//    osmSource.setUrl("http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png");
//    osmSource.setUrl("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png");
//    osmSource.setUrl("https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png");


const TILE_URL = "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png";
const ZOOM_INITIAL = 8;


const ObservationMap = {
    ObservationMap: function() {
        this.osmLayer = null;
        this.map = this.createOpenLayersMap();
        return this;
    },

    createOpenLayersMap: function() {
        console.log('createOpenLayersMap', 'BEGIN');
        const map = new OLMap({target: 'map',});
        const lon = '5.5';
        const lat = '142.0';
        const view = new OLView({center: olproj.fromLonLat([lon, lat]), zoom: ZOOM_INITIAL, projection: 'EPSG:3857'});
        map.setView(view);
        const osmSource = new OLSourceOSM("OpenStreetMap");
        osmSource.setUrl(TILE_URL);
        this.osmLayer = new OLTile({source: osmSource});
        this.osmLayer.setOpacity(0.7);
        map.addLayer(this.osmLayer);
        map.addControl(new OLControlFullScreen());
        const contourLayerButtons = new OLControl({element: $(".btn-group-layers").get(0)});
        map.addControl(contourLayerButtons);
        this.urlsLoaded = [];
        console.log('createOpenLayersMap', 'END');
        return map;
    },

    createObservationsFeatureLayer: function(observations) {
        console.log('createObservationsFeatureLayer', 'BEGIN');

        function createObservationFeatures(observation, lonLat) {
            let title = observation.title;
            if (observation.name) {
                title += ' door ' + observation.name;
            }
            return new OLFeature({
                geometry: new OLPoint(olproj.fromLonLat(lonLat)),
                title: title,
                waarneming_url: observation.waarneming_url,
                number: observation.number
            });
        }

        const features = [];
        for (const observation of observations) {
            const lat = parseFloat(observation.lat) + 90.0;
            const lonLat = [observation.lon.toFixed(5), lat.toFixed(5)];
            const observationFeature = createObservationFeatures(observation, lonLat);
            features.push(observationFeature);
        }

        for (const feature of features) {
            feature.setStyle(mapstyles.observationFeatureStyle);
        }

        const source = new OLSourceVector({
            features: features
        });

        const layer = new OLLayerVector({
            source: source
        });

        layer.setZIndex(0);

        this.map.addLayer(layer);
        console.log(features.length, 'features created');
        console.log('createObservationsFeatureLayer()', 'END');
        return layer;
    },

    addContourTileLayer: function(geojsonUrl, onFinish) {

        if (this.urlsLoaded.indexOf(geojsonUrl) > -1) {
            console.log('already loading');
            return;
        }

        this.urlsLoaded.push(geojsonUrl);
        console.log('create contour layer for geojson_url', geojsonUrl);
        let replacer = function(key, value) {
            if (!value.geometry) {
                return value;
            }
            let type;
            const rawType = value.type;
            const geometry = value.geometry;

            if (rawType === 1) {
                type = geometry.length === 1 ? 'Point' : 'MultiPoint';
            } else if (rawType === 2) {
                type = geometry.length === 1 ? 'LineString' : 'MultiLineString';
            } else if (rawType === 3) {
                type = geometry.length === 1 ? 'Polygon' : 'MultiPolygon';
            }

            return {
                'type': 'Feature',
                'geometry': {
                    'type': 'MultiLineString',
                    'coordinates': geometry,
                },
                'properties': value.tags
            };
        };

        let tilePixels = new OLProjection({
            code: 'TILE_PIXELS',
            units: 'tile-pixels'
        });

        const mapCache = this.map;  // TODO: remove this and fix in a nice way

        return fetch(geojsonUrl).then(function(response) {
            return response.json();
        }).then(function(json) {

            const tileIndex = geojsonvt(json, {
                extent: 4096,
                debug: 1,
                indexMaxPoints: 500000
            });

            let vectorSource = new OLSourceVectorTile({
                format: new OLGeoJSON(),
                tileGrid: oltilegrid.createXYZ(),
                tilePixelRatio: 16,
                tileLoadFunction: function(tile) {
                    const format = tile.getFormat();
                    const tileCoord = tile.getTileCoord();
                    const data = tileIndex.getTile(tileCoord[0], tileCoord[1], -tileCoord[2] - 1);

                    const features = format.readFeatures(
                        JSON.stringify({
                            type: 'FeatureCollection',
                            features: data ? data.features : []
                        }, replacer));
                        tile.setLoader(function() {
                            tile.setFeatures(features);
                            tile.setProjection(tilePixels);
                        });
                    },
                url: 'data:' // arbitrary url, we don't use it in the tileLoadFunction
            });

            function lineStyleFunction(feature, resolution) {
                const strokeWidth = feature.get('stroke-width');
                const zoom = mapCache.getView().getZoom();
                const lineWidth = strokeWidth/3.0;
                const value = feature.get('level-value');
                const levelNr = 1 + feature.get('level-index');
                let zoomFactor = Math.pow(zoom, 1.0)/50.0;

                zoomFactor *= Math.pow(levelNr, 0.75);
                if (levelNr % 3 === 0) {
                    zoomFactor *= 3.0;
                }
                if (levelNr === 11) {
                    zoomFactor *= 1.5;
                }

                return new OLStyle({
                    stroke: new OLStroke({
                        color: feature.get('stroke'),
                        width: lineWidth * zoomFactor,
                    })
                });
            }

            const vectorLayer = new OLLayerVectorTile({
                source: vectorSource,
                style: lineStyleFunction,
                updateWhileInteracting: false,
                updateWhileAnimating: false,
                renderMode: 'vector',  // other options stop loading tiles after zooming on large resolutions (OL bug?)
                //preload: 2,
            });

            mapCache.addLayer(vectorLayer);
            vectorLayer.setVisible(true);
            onFinish(vectorLayer);
        });
    },
};


export function createObservationMap() {
    return Object.create(ObservationMap).ObservationMap();
}
