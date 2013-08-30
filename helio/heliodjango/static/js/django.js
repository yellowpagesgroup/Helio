var getCookieValue = function(cookieName) {
    var nameQSKey = cookieName + "=";
    var splitCookies = document.cookie.split(';');
    for(var i=0; i < splitCookies.length; ++i) {
        var cookie = splitCookies[i];
        while (cookie.charAt(0)==' ')
            cookie = cookie.substring(1, cookie.length);

        if (cookie.indexOf(nameQSKey) == 0)
            return cookie.substring(nameQSKey.length, cookie.length);
    }
    return null;
}

var csrfSafeMethod = function(method) {
    // these HTTP methods do not require CSRF protection
    return (/^(GET|HEAD|OPTIONS|TRACE)$/.test(method));
};

var sameOrigin = function(url) {
    // test that a given url is a same-origin URL
    // url could be relative or scheme relative or absolute
    var host = document.location.host; // host + port
    var protocol = document.location.protocol;
    var sr_origin = '//' + host;
    var origin = protocol + sr_origin;
    // Allow absolute or scheme relative URLs to same origin
    return (url == origin || url.slice(0, origin.length + 1) == origin + '/') ||
        (url == sr_origin || url.slice(0, sr_origin.length + 1) == sr_origin + '/') ||
        // or any other URL that isn't scheme relative or absolute i.e relative.
        !(/^(\/\/|http:|https:).*/.test(url));
};

$.ajaxSetup({
    beforeSend: function(xhr, settings) {
        if (!csrfSafeMethod(settings.type) && sameOrigin(settings.url)) {
            // Send the token to same-origin, relative URLs only.
            // Send the token only if the method warrants CSRF protection
            // Using the CSRFToken value acquired earlier
            xhr.setRequestHeader("X-CSRFToken", getCookieValue('csrftoken'));
        }
    }
});