function addObservations(observations, map, minObservations) {
    console.log('addObservations', 'BEGIN');

    function createObservationFeatures(observation, lonLat) {
        return new ol.Feature({
            geometry: new ol.geom.Point( ol.proj.fromLonLat(lonLat) ),
            title: observation.title,
            number: observation.number
        });
    }

    var features = [];
    var coordinates = []

    for (var i in observations)
    {
        var observation = observations[i];
//        if (observation.number < minObservations) {
//            continue;
//        }
        var lat = parseFloat(observation.lat);
        lat = lat + 90.0;
        var epsilon = 0.001;
        coordinates.push([observation.lon, lat]);
        var lonLat = [observation.lon.toFixed(5), lat.toFixed(5)];
        var observationFeature = createObservationFeatures(observation, lonLat);
        features.push(observationFeature);
    }

    for (var j in features)
    {
        features[j].setStyle(map.observationStyleFunction);
    }

    var source = new ol.source.Vector({
        features: features
    });

    var layer = new ol.layer.Vector({
        source: source
    });

    layer.setZIndex(99);

    map.addLayer(layer);

//    // Select features
//    var select = new ol.interaction.Select({
//        layers: [sourcesLayer],
//        condition: ol.events.condition.click
//    });
//
//    var onSelectStationFeature = function(evt) {
//        evt.deselected.forEach(function(feature){
//            feature.setStyle(map.sourceStyleFunction);
//        });
//
//        if (!evt.selected[0])
//        {
//            return;
//        }
//
//        evt.selected.forEach(function(feature){
//            feature.setStyle(map.getSelectedStationStyle(feature));
//        });
//        var stationId = evt.selected[0].get('id');
//        map.showStationContours(stationId);
//        history.pushState(null, null, '?station=' + stationId);
//        $("#click-tip").hide();
//        //        moveToStation(stationId);
//    };
//
//    select.on('select', onSelectStationFeature);
//
//    map.addInteraction(select);
    console.log(features.length, 'features created');
    console.log('addObservations()', 'END');
    return layer;
}
