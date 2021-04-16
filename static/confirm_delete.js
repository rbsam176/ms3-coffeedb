$("#confirmUsername, #confirmPassword").on('input', function() {
    if ($("#confirmUsername").val().length > 2 && $("#confirmPassword").val().length > 2) {
        $("#initialDelete").attr('disabled', false)
    }
})

// TRIGGERS THE CONFIRMATION DELETE BUTTON TO APPEAR
$("#initialDelete").on('click', function() {
    $("#initialDelete").css('display', 'none')
    $("#confirmDelete, #confirmMessage").css('display', 'block')
    $("#confirmDelete").attr('disabled', false)
})