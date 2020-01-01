import OLStyle from "ol/style/style";
import OLCircle from "ol/style/circle";
import OLFill from "ol/style/fill";
import OLStroke from "ol/style/stroke";

export function observationFeatureStyle(feature, resolution) {
//    var number = feature.get('number');
    const zoomFactor = Math.sqrt(5000/resolution)*0.25;
//    var numberFactor = Math.pow(number/2.0, 1/3)/3.14;
    const strokeColor = 'blue';
    const circleColor = 'white';

//    var radius = numberFactor*zoomFactor;
    let radius = zoomFactor;
//    radius = Math.min(radius, 100.0*zoomFactor);
//    radius = Math.max(2.0*zoomFactor, radius);

//    if (number > 200) {
//        radius = 0;
//    }

    if (radius < 1) {
        radius = 0;
    }

    const width = 0.3*radius;

    const circleStyle = new OLCircle(({
        fill: new OLFill({color: circleColor}),
        stroke: new OLStroke({
            color: strokeColor,
            width: width,
        }),
        radius: radius
    }));

    return new OLStyle({
        image: circleStyle,
    });
}
