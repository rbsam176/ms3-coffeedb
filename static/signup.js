// REMOVE MINIMUM CHARACTER COUNT TIP WHEN CRITERIA MET, REINTRODUCE IF NOT MET
$("#inputUsername").on('input', function() {
    if ($("#inputUsername").val().length > 3){
        $("#usernameTag").html('<i class="bi bi-check-circle-fill"></i>')
    } else if ($("#inputUsername").val().length < 4){
        $("#usernameTag").text('Minimum 4 characters')
    }
})

// WHEN FIRST & LAST NAME ENTERED, GENERATE SUGGESTED USERNAME
$("#inputFirstName, #inputLastName").on('focusout', function() {
    if ($("#inputUsername").val().length < 1){
        if ($("#inputFirstName").val().length > 2 && $("#inputLastName").val().length > 2){
            fullname = $("#inputFirstName").val().toLowerCase() + $("#inputLastName").val().toLowerCase()
            $("#inputUsername").val(fullname)
            $("#usernameTag").html('<i class="bi bi-check-circle-fill"></i>')
        }
    }
})

