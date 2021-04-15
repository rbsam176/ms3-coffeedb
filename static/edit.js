// TRIGGERS THE CONFIRMATION DELETE BUTTON TO APPEAR
$("#initialDelete").on('click', function() {
    $("#initialDelete").css('display', 'none')
    $("#confirmDelete, #confirmMessage").css('display', 'block')
})