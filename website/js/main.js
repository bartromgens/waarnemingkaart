
// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr){
        if (xhr.overrideMimeType)
        {
            xhr.overrideMimeType("application/json");
        }
    }
});

var familySlug = 'all';
//var familySlug = 'aalscholvers';
//var familySlug = 'boomklevers';
//var familySlug = 'cettiidae';
//var familySlug = 'haviken-en-arenden';
//var familySlug = 'staartmezen';
//var familySlug = 'duiven';
//var familySlug = 'zwaluwen';
//var familySlug = 'gierzwaluwen';
//var familySlug = 'flamingos';
//var familySlug = 'eenden-ganzen-en-zwanen';
//var familySlug = 'winterkoningen';
//var familySlug = 'spreeuwen';

var dataDir = "/static/data/";

var contourmap = createObservationMap();

var observationsLayer = null;

$.getJSON(dataDir + "observations_" + familySlug + ".json", function(json) {
    contourmap.observations = json.observations;
    if (familySlug !== 'all') {
        observationsLayer = addObservations(json.observations, contourmap, 500000);
    }

    var geojsonUrl = dataDir + "contours_" + familySlug + ".geojson";
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
        if (layer === observationsLayer) {
            return feature;
        }
        return null;
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
