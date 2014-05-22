String.prototype.lpad = function(length) {
  var str = this;
  while (str.length < length)
    str = '0' + str;
  return str;
}

function get_http() {
  if (window.XMLHttpRequest) {
    httpRequest = new XMLHttpRequest();
  } else if (window.ActiveXObject) {
    try {
      httpRequest = new ActiveXObject("Msxml2.XMLHTTP");
    } catch (e) {
      httpRequest = new ActiveXObject("Microsoft.XMLHTTP");
    }
  }
  return httpRequest;
}
