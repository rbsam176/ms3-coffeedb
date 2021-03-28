$( ".star-rating-btn" ).on("mouseover", function () {
    $(this).prevAll().addBack().children('i').removeClass('bi-star')
    $(this).prevAll().addBack().children('i').addClass('bi-star-fill')
})

$( ".star-rating-btn" ).on("mouseout", function () {
    $(this).prevAll().addBack().children('i').removeClass('bi-star-fill')
    $(this).prevAll().addBack().children('i').addClass('bi-star')
})