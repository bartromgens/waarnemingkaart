
// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr){
        if (xhr.overrideMimeType)
        {
            xhr.overrideMimeType("application/json");
        }
    }
});

var dataDir = "/static/data/";

contourmap = createObservationMap();

$.getJSON(dataDir + "observations.json", function(json) {
    contourmap.observations = json.observations;
    largeEmissionSourcesLayer = addObservations(json.observations, contourmap, 500000);

    var geojsonUrl = dataDir + "contours.geojson";
    addContourLayer(geojsonUrl, contourmap, contourmap.contourLayers, updateVisibility);
    contourmap.on("moveend", updateVisibility);
});

function updateVisibility() {
}


// Controls
contourmap.addControl(new ol.control.FullScreen());

// Tooltip
$('#info').hide();

var displayFeatureInfo = function(pixel) {
    var info = $('#info');
    info.css({
        left: (pixel[0] + 10) + 'px',
        top: (pixel[1] - 50) + 'px'
    });

    var feature = contourmap.forEachFeatureAtPixel(pixel, function(feature, layer) {
        return feature;
    });

    if (feature) {
        var tooltipText = feature.get('title');
        if (tooltipText !== '') {
            info.text(tooltipText);
            info.show();
        } else {
            info.hide();
        }
    } else {
        info.hide();
    }
};

contourmap.on('pointermove', function(evt) {
    if (evt.dragging) {
        $('#info').hide();
        return;
    }
    displayFeatureInfo(contourmap.getEventPixel(evt.originalEvent));
});
