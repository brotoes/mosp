/**
    Copyright 2014 CHOICE Online Marketing Group

    This file is part of MosP.

    MosP is free software: you can redistribute it and/or modify
    it under the terms of the GNU General Public License as published by
    the Free Software Foundation, either version 3 of the License, or
    (at your option) any later version.

    MosP is distributed in the hope that it will be useful,
    but WITHOUT ANY WARRANTY; without even the implied warranty of
    MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
    GNU General Public License for more details.

    You should have received a copy of the GNU General Public License
    along with MosP.  If not, see <http://www.gnu.org/licenses/>.
*/

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
    var selected_date = select[0][select[0].selectedIndex].text;
    var url = "/rainfall/${location}/" + selected_date;
    url += "?t=" + Math.random(1000);
    $.getJSON(url, function(data) {
        recent_rainfall = data.data;
    });
    url = "/traps/${location}/" + selected_date;
    url += "?t=" + Math.random(1000);
    $.getJSON(url, function(data) {
        recent_trapCount = data.data;
    });
    draw();
}
