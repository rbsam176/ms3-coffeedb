// CLICKING SHOW MORE ON NOTES
$("#showMoreNotes").on('click', function(){
    if ($("#showMoreNotes").text().includes("Show more")) {
        // TOGGLE BUTTON TEXT
        $("#showMoreNotes").html("Show less <i class='bi bi-chevron-compact-up'></i>")
        // SHOWS EXTRA NOTES
        $(".extra-note").each(function(index){
            $(this).css('display', 'inline-block')
        })
    } else if ($("#showMoreNotes").text().includes("Show less")){
        // TOGGLE BUTTON TEXT
        $("#showMoreNotes").html("Show more <i class='bi bi-chevron-compact-down'></i>")
        // HIDE EXTRA NOTES
        $(".extra-note").each(function(index){
            $(this).css('display', 'none')
        })
    }
})

// CLICKING SHOW MORE ON ORIGIN
$("#showMoreOrigin").on('click', function(){
    if ($("#showMoreOrigin").children('i').hasClass('bi bi-chevron-compact-down')) {
        // TOGGLE BUTTON ICON
        $("#showMoreOrigin").children('i').removeClass('bi-chevron-compact-down')
        $("#showMoreOrigin").children('i').addClass('bi-chevron-compact-up')
        
        // SHOW OVERFLOW ORIGINS
        if ($(".origin-box").hasClass('originOptionsExtra')){
            $(".origin-box").removeClass('originOptionsExtra')
        }

    } else if ($("#showMoreOrigin").children('i').hasClass('bi bi-chevron-compact-up')) {
        // TOGGLE BUTTON ICON
        $("#showMoreOrigin").children('i').removeClass('bi-chevron-compact-up')
        $("#showMoreOrigin").children('i').addClass('bi-chevron-compact-down')
        // HIDE OVERFLOW ORIGINS
        if (!$(".origin-box").hasClass('originOptionsExtra')){
            $(".origin-box").addClass('originOptionsExtra')
        }
    }
})

$(".filter-controls").on('click', function(){
    if ($(".filter-controls").text().includes("Open filter controls")){
        $(this).html("Close filter controls <i class='ml-2 bi bi-chevron-compact-up'>")
        $(this).css('background-color', '#E8EAED')
    } else {
        $(this).html("Open filter controls <i class='ml-2 bi bi-chevron-compact-down'>")
        $(this).css('background-color', 'white')
    }
})

$( document ).ready(function() {
    // SHOWS ORIGIN IF IN SHOW MORE SECTION AND IS IN URL ARGS
    if ($(".origin-box").children('input').is(':checked')){
        $('.origin-box').each(function(){
            if ($(this).hasClass('originOptionsExtra')){
                $(this).removeClass('originOptionsExtra')
            }
        })
    }
    // IF NO MORE ICONS ARE HIDDEN
    $(".origin-box").each(function(){
        if (!$(this).hasClass('originOptionsExtra')){
            // TOGGLE BUTTON ICON
            $("#showMoreOrigin").children('i').removeClass('bi-chevron-compact-down')
            $("#showMoreOrigin").children('i').addClass('bi-chevron-compact-up')
        }
    })
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
})