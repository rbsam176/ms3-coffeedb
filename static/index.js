$("#main").css('display', 'none')

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