// GET NAV ON-LOAD POSITION
var defaultPosition = $("#navContainer").position()
// ON SCROLL
document.addEventListener('scroll', function (event) {
    // IF MOBILE NAV IS OPEN AND AT ON-LOAD POSITION
    if ($("#navContainer").position().top == defaultPosition.top && $(".navbar-collapse").hasClass('show')) {
        $('.navbar-collapse').collapse('toggle')
    }
})

$(document).ready(function(){
    // CYCLES THROUGH BOTH VIDEOS
    $('video').on('ended',function(){
        if ($('.primary-video').css('display') == 'block') {
            $(this).css('display', 'none')
            $(this).next().css('display', 'block')
            $(this).next().trigger('play')
        }
        if ($('.secondary-video').css('display') == 'block') {
            $(this).css('display', 'none')
            $(this).prev().css('display', 'block')
            $(this).prev().trigger('play')
        }
    });

    // AUTOCOMPLETE ASSIGNMENT
    $.getJSON('/autocomplete', function(data) {     
        // PARSES JSON DATA PULLED FROM MONGODB
        var jsonParsed = JSON.parse(data.autocomplete_values);
        // CONCATENATES BRANDS AND NAMES TO SINGLE LIST
        var autocompleteData = jsonParsed.brands.concat(jsonParsed.names)
        // ASSIGNS LIST OF BRANDS, NAMES TO SEARCH INPUT AUTOCOMPLETE
        $( "#searchInput" ).autocomplete({
            source: autocompleteData
        });
    });
  });

    // SOURCE: https://www.w3schools.com/howto/howto_css_smooth_scroll.asp#section2
    // Add smooth scrolling to all links
    $("a").on('click', function(event) {
        // Make sure this.hash has a value before overriding default behavior
        if (this.hash !== "") {
            // Prevent default anchor click behavior
            event.preventDefault();
            // Store hash
            var hash = this.hash;
            // Using jQuery's animate() method to add smooth page scroll
            // The optional number (800) specifies the number of milliseconds it takes to scroll to the specified area
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800, function(){
                // Add hash (#) to URL when done scrolling (default click behavior)
                window.location.hash = hash;
            });
        }
    });