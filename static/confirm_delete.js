$("#confirmUsername, #confirmPassword").on('input', function() {
    if ($("#confirmUsername").val().length > 2 && $("#confirmPassword").val().length > 2) {
        $("#initialDelete").prop('disabled', false)
    } else if ($("#confirmUsername").val().length < 3 || $("#confirmPassword").val().length < 3) {
        $("#initialDelete").prop('disabled', true)
    }
})

// TRIGGERS THE CONFIRMATION DELETE BUTTON TO APPEAR
$("#initialDelete").on('click', function() {
    $("#initialDelete").css('display', 'none')
    $("#confirmDelete, #confirmMessage").css('display', 'block')
    $("#confirmDelete").prop('disabled', false)
})