var observationmap = require("./observationmap.js");

// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr){
        if (xhr.overrideMimeType)
        {
            xhr.overrideMimeType("application/json");
        }
    }
});

//var familySlug = 'all';
var familySlug = 'aalscholvers';
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

var contourmap = observationmap.createObservationMap();

var observationsLayer = null;

$.getJSON(dataDir + "observations_" + familySlug + ".json", function(json) {
    if (familySlug !== 'all') {
        observationsLayer = contourmap.createObservationsFeatureLayer(json.observations);
    }

    var geojsonUrl = dataDir + "contours_" + familySlug + ".geojson";
    contourmap.addContourTileLayer(geojsonUrl);
    contourmap.map.on("moveend", updateVisibility);
});


function updateVisibility() {
}


// Tooltip
$('#info').hide();

function onPointerMapMove(evt) {
    if (evt.dragging) {
        $('#info').hide();
        return;
    }

    displayFeatureInfo(contourmap.map.getEventPixel(evt.originalEvent));

    function displayFeatureInfo(pixel) {
        var info = $('#info');
        info.css({
            left: (pixel[0] + 10) + 'px',
            top: (pixel[1] - 50) + 'px'
        });

        var feature = contourmap.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
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
}


contourmap.map.on('pointermove', onPointerMapMove);
