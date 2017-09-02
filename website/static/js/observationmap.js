function createObservationMap() {
    var map = new ol.Map({
        target: 'map',
    });

    var lon = '6.1';
    var lat = '142.0';
    var view = new ol.View( {center: ol.proj.fromLonLat([lon, lat]), zoom: 8, projection: 'EPSG:3857'} );
    map.setView(view);

    var osmSource = new ol.source.OSM("OpenCycleMap");
//    osmSource.setUrl("http://a.tile.opencyclemap.org/transport/{z}/{x}/{y}.png");  // needs an API key
//    osmSource.setUrl("https://a.tile.thunderforest.com/landscape/{z}/{x}/{y}.png?apikey=52962bab91de4e789491bc1f5ed4956e");
    osmSource.setUrl("https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png");
//    osmSource.setUrl("http://a.basemaps.cartocdn.com/light_all/{z}/{x}/{y}.png");
//    osmSource.setUrl("https://a.tile.openstreetmap.org/{z}/{x}/{y}.png");
//    osmSource.setUrl("https://tiles.wmflabs.org/bw-mapnik/{z}/{x}/{y}.png");

    var osmLayer = new ol.layer.Tile({source: osmSource});
    osmLayer.setOpacity(0.8);
    map.addLayer(osmLayer);
    map.contourLayers = [];
    map.observations = [];

    map.observationStyleFunction = function(feature, resolution) {
        var zoom = map.getView().getZoom();
        var number = feature.get('number');
        var zoomFactor = Math.pow(zoom, 2)/100.0;
        var numberFactor = Math.pow(number, 1.0/2.0)/3.14;
        var strokeColor = 'black';
        var circleColor = 'yellow';

        var radius = numberFactor*zoomFactor;
        radius = Math.min(radius, 100.0*zoomFactor);
        radius = Math.max(2.0*zoomFactor, radius);
        width = 1.5

        var circleStyle = new ol.style.Circle(({
            fill: new ol.style.Fill({color: circleColor}),
            stroke: new ol.style.Stroke({
                color: strokeColor,
                width: width,
            }),
            radius: radius
        }));

        return new ol.style.Style({
            image: circleStyle,
        });
    };

//    map.getSelectedStationStyle = function(feature, resolution) {
//        var strokeColor = 'lightgreen';
//        var circleColor = 'green';
//
//        var circleStyle = new ol.style.Circle(({
//            fill: new ol.style.Fill({color: circleColor}),
//            stroke: new ol.style.Stroke({color: strokeColor, width: 3}),
//            radius: typeScales[feature.get('type')] * 1.5
//        }));
//
//        return new ol.style.Style({
//            image: circleStyle,
//        });
//    };

    return map;
}
