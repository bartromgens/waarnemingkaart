function addContourLayer(geojsonUrl, map, contourLayers, onLoaded) {
    console.log('create contour layer for geojson_url', geojsonUrl);

    var replacer = function(key, value) {
        if (value.geometry) {
            var type;
            var rawType = value.type;
            var geometry = value.geometry;

            if (rawType === 1) {
                type = geometry.length === 1 ? 'Point' : 'MultiPoint';
            } else if (rawType === 2) {
                type = geometry.length === 1 ? 'LineString' : 'MultiLineString';
            } else if (rawType === 3) {
                type = geometry.length === 1 ? 'Polygon' : 'MultiPolygon';
            }

            return {
                'type': 'Feature',
                'geometry': {
                    'type': 'MultiLineString',
                    'coordinates': geometry,
                },
                'properties': value.tags
            };
        } else {
            return value;
        }
    };

    var tilePixels = new ol.proj.Projection({
        code: 'TILE_PIXELS',
        units: 'tile-pixels'
    });


    return fetch(geojsonUrl).then(function(response) {
        return response.json();
    }).then(function(json) {
        var tileIndex = geojsonvt(json, {
            extent: 4096,
            debug: 1,
            indexMaxPoints: 500000
        });

        var vectorSource = new ol.source.VectorTile({
            format: new ol.format.GeoJSON(),
            tileGrid: ol.tilegrid.createXYZ(),
            tilePixelRatio: 16,
            tileLoadFunction: function(tile) {
                var format = tile.getFormat();
                var tileCoord = tile.getTileCoord();
                var data = tileIndex.getTile(tileCoord[0], tileCoord[1], -tileCoord[2] - 1);

                var features = format.readFeatures(
                    JSON.stringify({
                        type: 'FeatureCollection',
                        features: data ? data.features : []
                    }, replacer));
                    tile.setLoader(function() {
                        tile.setFeatures(features);
                        tile.setProjection(tilePixels);
                    });
                },
            url: 'data:' // arbitrary url, we don't use it in the tileLoadFunction
        });

        function lineStyleFunction(feature, resolution) {
            var strokeWidth = feature.get('stroke-width');
            var zoom = map.getView().getZoom();
            var lineWidth = strokeWidth/3.0;
//            console.log(strokeWidth);
//            var value = feature.get('level-value');
//            var levelNr = feature.get('level-index');
            // var color = ol.color.asArray(feature.get('stroke'));
            // color[3] = 0.8;
//            var scaleFactor = 0.5;
            var zoomFactor = 1.0;
            if (zoom > 7) {
                zoomFactor = Math.pow(zoom, 2.0)/60.0;
            }
//            var zoomLevelShow10 = 9;
//            var zoomLevelShow5 = 10;

//            lineWidth *= (1.0 + (levelNr+1)/10);

            var lineStyle = new ol.style.Style({
                stroke: new ol.style.Stroke({
                    color: feature.get('stroke'),
                    width: lineWidth * zoomFactor,
                })
            });
            return lineStyle;
        }

        var vectorLayer = new ol.layer.VectorTile({
            source: vectorSource,
            style: lineStyleFunction,
            updateWhileInteracting: false,
            updateWhileAnimating: false,
            renderMode: 'vector',  // other options stop loading tiles after zooming on large resolutions (OL bug?)
            //preload: 2,
        });

        map.addLayer(vectorLayer);
        vectorLayer.setVisible(true);
        contourLayers.push(vectorLayer);
        onLoaded();
    });
}


module.exports = {
    addContourLayer: addContourLayer,
};