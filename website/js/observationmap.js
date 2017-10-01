var mapstyles = require("./mapstyles.js");

// TILE SOURCES
//    osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png");  // needs an API key
//    osmSource.setUrl("https://a.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=52962bab91de4e789491bc1f5ed4956e");
//    osmSource.setUrl("https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png");
//    osmSource.setUrl("http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png");
//    osmSource.setUrl("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png");
//    osmSource.setUrl("https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png");


var TILE_URL = "https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png";
var ZOOM_INITIAL = 8;


var ObservationMap = {
    ObservationMap: function() {
        this.osmLayer = null;
        this.map = this.createOpenLayersMap();
        return this;
    },
    createOpenLayersMap: function() {
        console.log('createOpenLayersMap', 'BEGIN');
        var map = new ol.Map({target: 'map',});
        var lon = '5.5';
        var lat = '142.0';
        var view = new ol.View({center: ol.proj.fromLonLat([lon, lat]), zoom: ZOOM_INITIAL, projection: 'EPSG:3857'});
        map.setView(view);
        var osmSource = new ol.source.OSM("OpenStreetMap");
        osmSource.setUrl(TILE_URL);
        this.osmLayer = new ol.layer.Tile({source: osmSource});
        this.osmLayer.setOpacity(0.7);
        map.addLayer(this.osmLayer);
        map.addControl(new ol.control.FullScreen());
        var contourLayerButtons = new ol.control.Control({element: $(".btn-group-layers").get(0)});
        map.addControl(contourLayerButtons);
        this.urlsLoaded = [];
        console.log('createOpenLayersMap', 'END');
        return map;
    },
    createObservationsFeatureLayer: function(observations) {
        console.log('createObservationsFeatureLayer', 'BEGIN');

        function createObservationFeatures(observation, lonLat) {
            var title = observation.title;
            if (observation.name) {
                title += ' door ' + observation.name;
            }
            return new ol.Feature({
                geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
                title: title,
                waarneming_url: observation.waarneming_url,
                number: observation.number
            });
        }

        var features = [];
        for (var i in observations)
        {
            var observation = observations[i];
            var lat = parseFloat(observation.lat);
            lat = lat + 90.0;
            var epsilon = 0.001;
            var lonLat = [observation.lon.toFixed(5), lat.toFixed(5)];
            var observationFeature = createObservationFeatures(observation, lonLat);
            features.push(observationFeature);
        }

        for (var j in features)
        {
            features[j].setStyle(mapstyles.observationFeatureStyle);
        }

        var source = new ol.source.Vector({
            features: features
        });

        var layer = new ol.layer.Vector({
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
        var replacer = function(key, value) {
            if (value.geometry) {
                var type;
                var rawType = value.type;
                var geometry = value.geometry;

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
            } else {
                return value;
            }
        };

        var tilePixels = new ol.proj.Projection({
            code: 'TILE_PIXELS',
            units: 'tile-pixels'
        });

        var mapCache = this.map;  // TODO: remove this and fix in a nice way

        return fetch(geojsonUrl).then(function(response) {
            return response.json();
        }).then(function(json) {

            var tileIndex = geojsonvt(json, {
                extent: 4096,
                debug: 1,
                indexMaxPoints: 500000
            });

            var vectorSource = new ol.source.VectorTile({
                format: new ol.format.GeoJSON(),
                tileGrid: ol.tilegrid.createXYZ(),
                tilePixelRatio: 16,
                tileLoadFunction: function(tile) {
                    var format = tile.getFormat();
                    var tileCoord = tile.getTileCoord();
                    var data = tileIndex.getTile(tileCoord[0], tileCoord[1], -tileCoord[2] - 1);

                    var features = format.readFeatures(
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
                var strokeWidth = feature.get('stroke-width');
                var zoom = mapCache.getView().getZoom();
                var lineWidth = strokeWidth/3.0;
                var value = feature.get('level-value');
                var levelNr = 1 + feature.get('level-index');
                var zoomFactor = Math.pow(zoom, 1.0)/50.0;

                zoomFactor *= Math.pow(levelNr, 0.75);
                if (levelNr % 3 === 0) {
                    zoomFactor *= 3.0;
                }
                if (levelNr === 11) {
                    zoomFactor *= 1.5;
                }

                var lineStyle = new ol.style.Style({
                    stroke: new ol.style.Stroke({
                        color: feature.get('stroke'),
                        width: lineWidth * zoomFactor,
                    })
                });
                return lineStyle;
            }

            var vectorLayer = new ol.layer.VectorTile({
                source: vectorSource,
                style: lineStyleFunction,
                updateWhileInteracting: false,
                updateWhileAnimating: false,
                renderMode: 'vector',  // other options stop loading tiles after zooming on large resolutions (OL bug?)
                //preload: 2,
            });

            mapCache.addLayer(vectorLayer);
            contourLayer = vectorLayer;
            vectorLayer.setVisible(true);
            onFinish(contourLayer);
        });
    },
}


function createObservationMap() {
    var observationMap = Object.create(ObservationMap).ObservationMap();
    return observationMap
}


module.exports = {
    createObservationMap: createObservationMap,
};
