function draw() {
    for (var i = 0; i < circles.length; i ++) {
        window.circles[i].setMap(null);
    }
    window.circles = [];
    for (var i = 0; i < gauges.length; i ++) {
        var gauge = gauges[i];
        var stroke = '#000000';

        if (i < recent_rainfall.length) {
            var rainfall = recent_rainfall[i][2];
            var blue = rainfall/max_rain;
            blue *= 255;
            blue = Math.round(blue);
            var red = 255 - blue;
            stroke = '#';
            stroke += red.toString(16).lpad(2);
            stroke += '00';
            stroke += blue.toString(16).lpad(2);
        }
        var circle = new google.maps.Marker({
            position: new google.maps.LatLng(gauge[1], gauge[2]),
            map: map,
            icon: {
                path: google.maps.SymbolPath.CIRCLE,
                scale:5,
                strokeColor:stroke
            },
            title: 'Rain Gauge #' + readings[i][0]
        });
        window.circles.push(circle);
    }

    for (var i = 0; i < rectangles.length; i ++) {
        window.rectangles[i].setMap(null);
    }
    window.rectangles = [];
    for (var i = 0; i < quadrants.length; i ++) {
        var count = recent_trapCount[i][2];
        var red = count/max_trap;
        red *= 255;
        red = Math.floor(red);
        var green = 255 - red;
        var fill = '#';
        fill += red.toString(16).lpad(2);
        fill += green.toString(16).lpad(2);
        fill += '00';

        var rectangle = new google.maps.Rectangle({
            map: map,
            fillColor: fill,
            fillOpacity: 0.3,
            stroke: '#000000',
            strokeWeight: 1,
            bounds: new google.maps.LatLngBounds(
                new google.maps.LatLng(quadrants[i][0], quadrants[i][1]),
                new google.maps.LatLng(quadrants[i][2], quadrants[i][3])
            )
        });
        window.rectangles.push(rectangle);
    }
}
function initialize() {
    var location_center = new google.maps.LatLng(window.center[0], window.center[1]);
    var mapOptions = {
        center: location_center,
        zoom: 10,
        scrollwheel: false,
        disableDefaultUI: true,
        draggable: false,
        disableDoubleClickZoom: true
    };
    window.map = new google.maps.Map(document.getElementById("map-canvas"), mapOptions);
    draw();
}
