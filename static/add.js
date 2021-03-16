// IF USER SELECTS 'OTHER' IN DROPDOWN, PRESENT TEXT INPUT AND MAKE IT REQUIRED
$('.dynamicSelection').on('change', function () {
    toggleInput = $(this).parent().next('.toggleInput')
    if ($(this).val() == "Other..."){
        $(toggleInput).css('display', 'block')
        $(toggleInput).children().attr('required', true)
    } else {
        $(toggleInput).css('display', 'none')
        $(toggleInput).children().attr('required', false)
    }
});

// ON 'OTHER' TEXT INPUT, MAKE DROPDOWN DISABLED
$(".toggleInput").on('input', function() {
    parentSelect = $(this).prev('div').children('.dynamicSelection')
    customInput = $(this).children('.customInput')
    if( $(customInput).val().length === 0 ) {
        $(parentSelect).attr("disabled", false);
    } else {
        $(parentSelect).attr("disabled", true);
    }
})


