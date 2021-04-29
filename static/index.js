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

    function arrowDown() {
        $('.down-btn').animate({
            top: '10px',
        }, 1000, function() {
            arrowUp();
        });
    }

    function arrowUp() {
        $('.down-btn').animate({
            top: '0px',
        }, 1000, function() {
            arrowDown();
        });
    }

    arrowDown();

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
    // ADD SMOOTH SCROLLING TO ALL LINKS
    $("a").on('click', function(event) {
        if (this.hash !== "") {
            event.preventDefault();
            var hash = this.hash;
            $('html, body').animate({
                scrollTop: $(hash).offset().top
            }, 800, function(){
                window.location.hash = hash;
            });
        }
    });