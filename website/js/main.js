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
//var familySlug = 'aalscholvers';
//var familySlug = 'boomklevers';
//var familySlug = 'cettiidae';
//var familySlug = 'haviken-en-arenden';
//var familySlug = 'staartmezen';
//var familySlug = 'duiven';
//var familySlug = 'zwaluwen';
var familySlug = 'gierzwaluwen';
//var familySlug = 'flamingos';
//var familySlug = 'eenden-ganzen-en-zwanen';
//var familySlug = 'winterkoningen';
//var familySlug = 'spreeuwen';

function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}

var group = getParameterByName('group');
var family = getParameterByName('family');
var species = getParameterByName('species');
console.log('group', group);
console.log('family', family);
console.log('species', species);

var observationFilepath = "/static/data/";
var contoursFilepath = "/static/data/";

if (group) {
    observationFilepath += group + "/";
    contoursFilepath += group + "/";
}
if (family !== "" && species !== "") {
    observationFilepath += family + "/";
    contoursFilepath += family + "/";
    observationFilepath += species + ".json";
    contoursFilepath += "contours_" + species + ".geojson";
} else if (family !== "") {
    observationFilepath += family + ".json";
    contoursFilepath += "contours_" + family + ".geojson";
}

console.log(observationFilepath);
console.log(contoursFilepath);

var contourmap = observationmap.createObservationMap();

var observationsLayer = null;

$.getJSON(observationFilepath, function(json) {
    if (familySlug !== 'all') {
        observationsLayer = contourmap.createObservationsFeatureLayer(json.observations);
    }

    contourmap.addContourTileLayer(contoursFilepath);
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
