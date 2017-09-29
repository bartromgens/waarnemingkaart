var observationmap = require("./observationmap.js");

var DATA_DIR = "/static/waarnemingkaart-data/";
var OBSERVATIONS_LAYER_ZOOM = 11;

var observationsLayer = null;
var contourLayerHighDetail = null;
var contourLayerLowDetail = null;

// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr){
        if (xhr.overrideMimeType)
        {
            xhr.overrideMimeType("application/json");
        }
    }
});


function getParameterByName(name, url) {
    if (!url) url = window.location.href;
    name = name.replace(/[\[\]]/g, "\\$&");
    var regex = new RegExp("[?&]" + name + "(=([^&#]*)|&|#|$)"),
        results = regex.exec(url);
    if (!results) return null;
    if (!results[2]) return '';
    return decodeURIComponent(results[2].replace(/\+/g, " "));
}


function getFileLocations() {
    var group = getParameterByName('group');
    var family = getParameterByName('family');
    var species = getParameterByName('species');
    if (group == '' && family == '' && species == '') {
        return null;
    }

    console.log('group', group);
    console.log('family', family);
    console.log('species', species);

    var observationsFilepath = DATA_DIR;
    var contoursDir = DATA_DIR;
    var name = null;

    if (group && family) {
        observationsFilepath += group + "/";
        contoursDir += group + "/";
    } else {
        observationsFilepath += group + ".json";
        name = group;
    }
    if ((family && species) && (family !== "" && species !== "")) {
        contoursDir += family + "/";
        observationsFilepath += family + "/" + species + ".json";
        name = species;
    } else if (family && family !== "") {
        observationsFilepath += family + ".json";
        name = family;
    }

    var contoursLowFilepath = contoursDir + "contours_" + name + "_1_.geojson";
    var contoursHighFilepath = contoursDir + "contours_" + name + "_0_.geojson";
    return {
        observations: observationsFilepath,
        contoursLow: contoursLowFilepath,
        contoursHigh: contoursHighFilepath,
    };
}


var filepaths = getFileLocations();

var contourmap = observationmap.createObservationMap();

if (filepaths) {
    contourmap.addContourTileLayer(filepaths.contoursLow, function(contourLayer) {
        contourLayerLowDetail = contourLayer;
    });
}


// Save map as png
document.getElementById('export-png').addEventListener('click', function() {
    var opacityBefore = contourmap.osmLayer.getOpacity();
    contourmap.osmLayer.setOpacity(1.0);
    contourmap.map.once('postcompose', function(event) {
        var canvas = event.context.canvas;
        if (navigator.msSaveBlob) {
            navigator.msSaveBlob(canvas.msToBlob(), 'map.png');
        } else {
            canvas.toBlob(function(blob) {
                saveAs(blob, 'map.png');
            });
        }
    });
    contourmap.map.renderSync();
    contourmap.osmLayer.setOpacity(opacityBefore);
});


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

function createObservationsLayer() {
    $.getJSON(filepaths.observations, function(json) {
        if (json.observations.length < 50000) {
            observationsLayer = contourmap.createObservationsFeatureLayer(json.observations);
        } else {
            console.log('WARNING: too many observations to show');
        }
    });
}

contourmap.map.on('pointermove', onPointerMapMove);

contourmap.map.on('moveend', function(event) {
    var observationsVisible = contourmap.map.getView().getZoom() > OBSERVATIONS_LAYER_ZOOM;
    if (observationsVisible && !observationsLayer) {
        createObservationsLayer();
    }
    if (observationsLayer) {
        observationsLayer.setVisible(observationsVisible);
    }
//    console.log('contourLayerLowDetail', contourLayerLowDetail);
//    console.log('contourLayerHighDetail', contourLayerHighDetail);

    var highDetailMode = contourmap.map.getView().getZoom() > 10
    if (highDetailMode && !contourLayerHighDetail) {
        contourmap.addContourTileLayer(filepaths.contoursHigh, function(contourLayer) {
            contourLayerHighDetail = contourLayer;
        });
    }
    if (contourLayerHighDetail) {
        contourLayerHighDetail.setVisible(highDetailMode);
    }
    if (contourLayerLowDetail) {
        contourLayerLowDetail.setVisible(!highDetailMode);
    }
})