var indexFill = []

// APPENDS WHICH ICON INDEXES ARE FILLED
$("button.star-rating-btn").children('i').each(function(index) {
    if ($(this).hasClass('bi-star-fill')){
        indexFill.push(index)
    }
})

$("#reviewContent").keyup(function() {
    var limit = 150
    var currentCount = $("#reviewContent").val().length
    $("#characterCounter").text(limit - currentCount)
})

$( document ).ready(function() {
    // ON PAGE LOAD, ADJUST CHARACTER COUNT IF REVIEW PRE-EXISTS
    if ($("#reviewContent").val().length > 0){
        $("#characterCounter").text(150 - $("#reviewContent").val().length)
    }

    // GETS INDEX VALUE OF FIRST UNFILLED STAR
    var firstEmptyStar = indexFill.length

    // ADDS FILL ON ICONS BETWEEN PRE-FILLED AND CURRENTLY HOVERED ICON
    $( ".star-rating-btn" ).on("mouseover", function () {
        var hoverIndex = $(this).index()
        for (x = firstEmptyStar; x <= hoverIndex; x++) {
            $(".star-rating-btn").children('i').eq(x).removeClass('bi-star')
            $(".star-rating-btn").children('i').eq(x).addClass('bi-star-fill')
        }
    })
    // REMOVES FILL ON ICONS BETWEEN PRE-FILLED AND CURRENTLY HOVERED ICON
    $( ".star-rating-btn" ).on("mouseout", function () {
        var hoverIndex = $(this).index()
        for (x = firstEmptyStar; x <= hoverIndex; x++) {
            $(".star-rating-btn").children('i').eq(x).addClass('bi-star')
            $(".star-rating-btn").children('i').eq(x).removeClass('bi-star-fill')
        }
    })
})

