function initialize() {
    var mapOptions = {
        center: new google.maps.LatLng(${latitude}, ${longitude}),
        zoom: 11,
        scrollwheel: false,
        disableDefaultUI: true,
        draggable: false,
        disableDoubleClickZoom: true
    };
    var map = new google.maps.Map(document.getElementById("map-canvas"),
                                  mapOptions);
}
google.maps.event.addDomListener(window, 'load', initialize);
