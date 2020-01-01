var sidebar = require("./sidebar.js");
var observationmap = require("./observationmap");
import OLSelect from "ol/interaction/select";


const DATA_DIR = "/static/waarnemingkaart-data/";
const OBSERVATIONS_LAYER_ZOOM = 11;

let observationsLayer = null;
const contourLayers = {
    high: null,
    low: null
};

let filepaths = null;
let contourmap = null;
let changeLayersOnZoom = true;

$(window).ready(initialize);


function initialize() {
    filepaths = getFileLocations();
    contourmap = observationmap.createObservationMap();
    if (filepaths) {
        showContourLayer('low');
    }
    setEventHandlers();
    $(".btn-group-layers").show();
}


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
    if (group === '' && family === '' && species === '') {
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
        contours: {
            low: contoursLowFilepath,
            high: contoursHighFilepath
        }
    };
}


function onPointerMapMove(evt) {
    if (evt.dragging) {
        $('#info').hide();
        return;
    }

    displayFeatureInfo(contourmap.map.getEventPixel(evt.originalEvent));

    function displayFeatureInfo(pixel) {
        let info = $('#info');
        info.css({
            left: (pixel[0] + 10) + 'px',
            top: (pixel[1] - 50) + 'px'
        });

        let feature = contourmap.map.forEachFeatureAtPixel(pixel, function(feature, layer) {
            if (layer === observationsLayer) {
                return feature;
            }
            return null;
        });

        if (feature) {
            let tooltipText = feature.get('title');
            if (tooltipText !== '') {
                info.text(tooltipText);
                info.show();
            } else {
                info.hide();
            }
        } else {
            info.hide();
        }
    }
}


function preloadContourLayer(type) {
    if (!contourLayers[type]) {
        contourmap.addContourTileLayer(filepaths.contours[type], function(contourLayer) {
            contourLayers[type] = contourLayer;
            contourLayer.setVisible(false);
        });
    }
}


function showContourLayer(type) {
    if (!contourLayers[type]) {
        createContourLayerType(type);
    } else {
        hideAllContourLayersExcept(type);
    }

    function createContourLayerType(type) {
        if (!contourLayers[type]) {
            contourmap.addContourTileLayer(filepaths.contours[type], function(contourLayer) {
                contourLayers[type] = contourLayer;
                hideAllContourLayersExcept(type);
            });
        }
    }

    function hideAllContourLayersExcept(type) {
        if (contourLayers[type]) {
            contourLayers[type].setVisible(true);
        }
        for (let key in contourLayers) {
            if (key !== type && contourLayers[key]) {
                contourLayers[key].setVisible(false);
            }
        }
    }
}


function updateOnZoom(event) {
    const zoom = contourmap.map.getView().getZoom();

    showObservationsLayerForZoom();
    showLayerForZoom();

    function showLayerForZoom() {
        if (!changeLayersOnZoom) {
            return;
        }

        if (zoom > (OBSERVATIONS_LAYER_ZOOM-1)) {
            preloadContourLayer("high");
        }

        if (zoom > OBSERVATIONS_LAYER_ZOOM) {
            showContourLayer("high");
        } else {
            showContourLayer("low");
        }
    }

    function showObservationsLayerForZoom() {
        const observationsVisible = zoom > OBSERVATIONS_LAYER_ZOOM;
        if (observationsVisible && !observationsLayer) {
            createObservationsLayer();
        }
        if (observationsLayer) {
            observationsLayer.setVisible(observationsVisible);
        }

        function createObservationsLayer() {
            $.getJSON(filepaths.observations, function(json) {
                if (json.observations.length < 50000) {
                    console.log('observations', json);
                    observationsLayer = contourmap.createObservationsFeatureLayer(json.observations);
                } else {
                    console.log('WARNING: too many observations to show');
                }
            });
        }
    }
}


function updateLayersOnButtonClick(event) {
    const layerInputElement = $('input[name=layers]:checked');
    const layerSelected = layerInputElement.val();
    $('input[name=layers]').parent().removeClass('active');
    layerInputElement.parent().addClass('active');
    if (layerSelected === "high") {
        showContourLayer("high");
    }
    if (layerSelected === "low") {
        showContourLayer("low");
    }
    changeLayersOnZoom = layerSelected === "auto";
}


function setEventHandlers() {
    contourmap.map.on('pointermove', onPointerMapMove);
    contourmap.map.on('moveend', updateOnZoom);
    createFeatureClickInteraction();

    $(".sidebar-toggle").bind("click", function(e) {
        setTimeout(function() { contourmap.map.updateSize();}, 600);
    });

    $(".btn-group-layers").bind("change", updateLayersOnButtonClick);

    document.getElementById('export-png').addEventListener('click', exportMapToImage);
}


function exportMapToImage(event) {
    const opacityBefore = contourmap.osmLayer.getOpacity();
    contourmap.osmLayer.setOpacity(1.0);
    contourmap.map.once('postcompose', function(event) {
        const canvas = event.context.canvas;
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
}


function createFeatureClickInteraction() {
    const select_interaction = new OLSelect();
    select_interaction.getFeatures().on("add", function (e) {
         const feature = e.element;
         const url = feature.get('waarneming_url');
         if (url) {
            window.open(feature.get('waarneming_url'), '_blank');
         }
    });
    contourmap.map.addInteraction(select_interaction);
}

// http://stackoverflow.com/a/4234006
$.ajaxSetup({
    beforeSend: function(xhr){
        if (xhr.overrideMimeType)
        {
            xhr.overrideMimeType("application/json");
        }
    }
});

