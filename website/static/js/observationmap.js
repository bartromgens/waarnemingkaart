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
    osmSource.setUrl("https://a.tile.thunderforest.com/neighbourhood/{z}/{x}/{y}.png?apikey=52962bab91de4e789491bc1f5ed4956e");

    var osmLayer = new ol.layer.Tile({source: osmSource});
    osmLayer.setOpacity(0.8);
    map.addLayer(osmLayer);
    map.contourLayers = [];
    map.observations = [];

    map.observationStyleFunction = function(feature, resolution) {
        var zoom = map.getView().getZoom();
        var number = feature.get('number');
        var zoomFactor = Math.pow(zoom, 3)/7000.0;
        var numberFactor = Math.pow(number, 1.0/2.0);
        var strokeColor = 'black';
        var circleColor = 'yellow';

        var radius = 2.0*numberFactor;
        radius = Math.max(10.0, radius);
        width = 1.5

        var circleStyle = new ol.style.Circle(({
            fill: new ol.style.Fill({color: circleColor}),
            stroke: new ol.style.Stroke({
                color: strokeColor,
                width: width,
            }),
            radius: radius*zoomFactor
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
