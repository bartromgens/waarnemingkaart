
function observationFeatureStyle(feature, resolution) {
//    var number = feature.get('number');
    var zoomFactor = Math.sqrt(5000/resolution)*0.25;
//    var numberFactor = Math.pow(number/2.0, 1/3)/3.14;
    var strokeColor = 'blue';
    var circleColor = 'white';

//    var radius = numberFactor*zoomFactor;
    var radius = zoomFactor;
//    radius = Math.min(radius, 100.0*zoomFactor);
//    radius = Math.max(2.0*zoomFactor, radius);

//    if (number > 200) {
//        radius = 0;
//    }

    if (radius < 1) {
        radius = 0;
    }

    width = 0.3*radius;

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
