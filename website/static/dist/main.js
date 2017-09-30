!function(e){function t(n){if(o[n])return o[n].exports;var r=o[n]={i:n,l:!1,exports:{}};return e[n].call(r.exports,r,r.exports,t),r.l=!0,r.exports}var o={};t.m=e,t.c=o,t.d=function(e,o,n){t.o(e,o)||Object.defineProperty(e,o,{configurable:!1,enumerable:!0,get:n})},t.n=function(e){var o=e&&e.__esModule?function(){return e.default}:function(){return e};return t.d(o,"a",o),o},t.o=function(e,t){return Object.prototype.hasOwnProperty.call(e,t)},t.p="",t(t.s=0)}([function(e,t,o){e.exports=o(1)},function(e,t,o){function n(e,t){t||(t=window.location.href),e=e.replace(/[\[\]]/g,"\\$&");var o=new RegExp("[?&]"+e+"(=([^&#]*)|&|#|$)"),n=o.exec(t);return n?n[2]?decodeURIComponent(n[2].replace(/\+/g," ")):"":null}function r(e){if(e.dragging)return void $("#info").hide();!function(e){var t=$("#info");t.css({left:e[0]+10+"px",top:e[1]-50+"px"});var o=g.map.forEachFeatureAtPixel(e,function(e,t){return t===s?e:null});if(o){var n=o.get("title");""!==n?(t.text(n),t.show()):t.hide()}else t.hide()}(g.map.getEventPixel(e.originalEvent))}function a(){$.getJSON(p.observations,function(e){e.observations.length<5e4?s=g.createObservationsFeatureLayer(e.observations):console.log("WARNING: too many observations to show")})}var i=o(2),l="/static/waarnemingkaart-data/",s=null,u=null,c=null;$.ajaxSetup({beforeSend:function(e){e.overrideMimeType&&e.overrideMimeType("application/json")}});var p=function(){var e=n("group"),t=n("family"),o=n("species");if(""==e&&""==t&&""==o)return null;console.log("group",e),console.log("family",t),console.log("species",o);var r=l,a=l,i=null;return e&&t?(r+=e+"/",a+=e+"/"):(r+=e+".json",i=e),t&&o&&""!==t&&""!==o?(a+=t+"/",r+=t+"/"+o+".json",i=o):t&&""!==t&&(r+=t+".json",i=t),{observations:r,contoursLow:a+"contours_"+i+"_1_.geojson",contoursHigh:a+"contours_"+i+"_0_.geojson"}}(),g=i.createObservationMap();p&&g.addContourTileLayer(p.contoursLow,function(e){c=e}),document.getElementById("export-png").addEventListener("click",function(){var e=g.osmLayer.getOpacity();g.osmLayer.setOpacity(1),g.map.once("postcompose",function(e){var t=e.context.canvas;navigator.msSaveBlob?navigator.msSaveBlob(t.msToBlob(),"map.png"):t.toBlob(function(e){saveAs(e,"map.png")})}),g.map.renderSync(),g.osmLayer.setOpacity(e)}),$("#info").hide(),g.map.on("pointermove",r),g.map.on("moveend",function(e){var t=g.map.getView().getZoom(),o=t>11;o&&!s&&a(),s&&s.setVisible(o),t>10&&!u&&g.addContourTileLayer(p.contoursHigh,function(e){e.setVisible(t>11),u=e});var n=t>11;u&&u.setVisible(n),c&&c.setVisible(!n)});var d=new ol.interaction.Select;d.getFeatures().on("add",function(e){var t=e.element;window.open(t.get("waarneming_url"),"_blank")}),g.map.addInteraction(d)},function(e,t,o){function n(){return Object.create(a).ObservationMap()}var r=o(3),a={ObservationMap:function(){return this.osmLayer=null,this.map=this.createOpenLayersMap(),this},createOpenLayersMap:function(){console.log("createOpenLayersMap","BEGIN");var e=new ol.Map({target:"map"}),t=new ol.View({center:ol.proj.fromLonLat(["5.5","142.0"]),zoom:8,projection:"EPSG:3857"});e.setView(t);var o=new ol.source.OSM("OpenStreetMap");return o.setUrl("https://maps.wikimedia.org/osm-intl/{z}/{x}/{y}.png"),this.osmLayer=new ol.layer.Tile({source:o}),this.osmLayer.setOpacity(.7),e.addLayer(this.osmLayer),e.addControl(new ol.control.FullScreen),console.log("createOpenLayersMap","END"),e},createObservationsFeatureLayer:function(e){console.log("createObservationsFeatureLayer","BEGIN");var t=[];for(var o in e){var n=e[o],a=parseFloat(n.lat);a+=90;var i=[n.lon.toFixed(5),a.toFixed(5)],l=function(e,t){var o=e.title;return e.name&&(o+=" door "+e.name),new ol.Feature({geometry:new ol.geom.Point(ol.proj.fromLonLat(t)),title:o,waarneming_url:e.waarneming_url,number:e.number})}(n,i);t.push(l)}for(var s in t)t[s].setStyle(r.observationFeatureStyle);var u=new ol.source.Vector({features:t}),c=new ol.layer.Vector({source:u});return c.setZIndex(0),this.map.addLayer(c),console.log(t.length,"features created"),console.log("createObservationsFeatureLayer()","END"),c},addContourTileLayer:function(e,t){console.log("create contour layer for geojson_url",e);var o=function(e,t){if(t.geometry){var o=t.type,n=t.geometry;return 1===o?1===n.length?"Point":"MultiPoint":2===o?1===n.length?"LineString":"MultiLineString":3===o&&(1===n.length?"Polygon":"MultiPolygon"),{type:"Feature",geometry:{type:"MultiLineString",coordinates:n},properties:t.tags}}return t},n=new ol.proj.Projection({code:"TILE_PIXELS",units:"tile-pixels"}),r=this.map;return fetch(e).then(function(e){return e.json()}).then(function(e){function a(e,t){var o=e.get("stroke-width"),n=r.getView().getZoom(),a=o/3,i=(e.get("level-value"),1+e.get("level-index")),l=Math.pow(n,1)/50;return l*=Math.pow(i,.75),i%3==0&&(l*=3),11===i&&(l*=1.5),new ol.style.Style({stroke:new ol.style.Stroke({color:e.get("stroke"),width:a*l})})}var i=geojsonvt(e,{extent:4096,debug:1,indexMaxPoints:5e5}),l=new ol.source.VectorTile({format:new ol.format.GeoJSON,tileGrid:ol.tilegrid.createXYZ(),tilePixelRatio:16,tileLoadFunction:function(e){var t=e.getFormat(),r=e.getTileCoord(),a=i.getTile(r[0],r[1],-r[2]-1),l=t.readFeatures(JSON.stringify({type:"FeatureCollection",features:a?a.features:[]},o));e.setLoader(function(){e.setFeatures(l),e.setProjection(n)})},url:"data:"}),s=new ol.layer.VectorTile({source:l,style:a,updateWhileInteracting:!1,updateWhileAnimating:!1,renderMode:"vector"});r.addLayer(s),contourLayer=s,s.setVisible(!0),t(contourLayer)})}};e.exports={createObservationMap:n}},function(e,t){function o(e,t){var o=.25*Math.sqrt(5e3/t),n=o;n<1&&(n=0),width=.3*n;var r=new ol.style.Circle({fill:new ol.style.Fill({color:"white"}),stroke:new ol.style.Stroke({color:"blue",width:width}),radius:n});return new ol.style.Style({image:r})}e.exports={observationFeatureStyle:o}}]);