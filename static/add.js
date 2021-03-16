// IF USER SELECTS 'OTHER' IN DROPDOWN, PRESENT TEXT INPUT AND MAKE IT REQUIRED
$('#originSelection').on('change', function () {
    if ($('#originSelection').val() == "Other..."){
        $("#otherOrigin").css('display', 'block')
        $("#newOrigin").attr('required', true)
    } else {
        $("#otherOrigin").css('display', 'none')
        $("#newOrigin").attr('required', false)
    }
});

// ON 'OTHER' TEXT INPUT, MAKE DROPDOWN DISABLED
$("#otherOrigin").on('input', function() {
    if( $("#newOrigin").val().length === 0 ) {
        $("#originSelection").attr("disabled", false);
    } else {
        $("#originSelection").attr("disabled", true);
    }
})