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
    // GETS INDEX VALUE OF FIRST UNFILLED STAR
    var firstEmptyStar = indexFill.length

    // ADDS FILL ON ICONS BETWEEN PRE-FILLED AND CURRENTLY HOVERED ICON
    $( ".star-rating-btn" ).on("mouseover", function () {
        var hoverIndex = $("i.bi").index($(this).children('i'))
        for (x = firstEmptyStar; x < hoverIndex + 1; x++) {
            $(".star-rating-btn").children('i').eq(x).removeClass('bi-star')
            $(".star-rating-btn").children('i').eq(x).addClass('bi-star-fill')
        }
    })
    // REMOVES FILL ON ICONS BETWEEN PRE-FILLED AND CURRENTLY HOVERED ICON
    $( ".star-rating-btn" ).on("mouseout", function () {
        var hoverIndex = $("i.bi").index($(this).children('i'))
        for (x = firstEmptyStar; x < hoverIndex + 1; x++) {
            $(".star-rating-btn").children('i').eq(x).addClass('bi-star')
            $(".star-rating-btn").children('i').eq(x).removeClass('bi-star-fill')
        }
    })
})

