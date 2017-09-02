
function observationFeatureStyle(feature, resolution) {
    var number = feature.get('number');
    var zoom = 5.0; // TODO: function of resolution;
    var zoomFactor = Math.pow(zoom, 2)/75.0;
    var numberFactor = Math.pow(number, 1.0/2.0)/3.14;
    var strokeColor = 'blue';
    var circleColor = 'white';

    var radius = numberFactor*zoomFactor;
    radius = Math.min(radius, 100.0*zoomFactor);
    radius = Math.max(2.0*zoomFactor, radius);
    width = 1.0*zoomFactor/1.5;

    if (number > 200) {
        radius = 0;
    }

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
}


module.exports = {
    observationFeatureStyle: observationFeatureStyle,
};
