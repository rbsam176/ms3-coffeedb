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
    // IF USERNAME INPUT FIELD IS EMPTY
    if ($("#inputUsername").val().length < 1){
        // IF FIRST NAME AND LAST NAME INPUT FIELD HAS MORE THAN 2 CHARACTERS
        if ($("#inputFirstName").val().length > 2 && $("#inputLastName").val().length > 2){
            // CREATE FULL NAME FROM FIRST AND LAST NAME VALUES
            fullname = $("#inputFirstName").val().toLowerCase() + $("#inputLastName").val().toLowerCase()
            fullnameTrimmed = fullname.replace(/ /g, "")
            // ENTER SUGGESTED USERNAME
            $("#inputUsername").val(fullnameTrimmed)
        }
    }
})

formCriteria = {
    "firstName": false,
    "lastName": false,
    "email": false,
    "username": false
}

passwordCriteria = {
    "passwordLength": false,
    "passwordUppercase": false,
    "passwordNumber": false,
    "passwordMatch": false
}

// PASSWORD LENGTH CHECKER
function characterLength(iconId){
    if ($("#inputPassword").val().length > 7){
        // SET CRITERIA TO TRUE
        passwordCriteria['passwordLength'] = true
        // IF IT ISN'T ALREADY FILLED
        if (!$(iconId).hasClass('bi-check-circle-fill')){
            $(iconId).removeClass()
            $(iconId).addClass('bi bi-check-circle-fill')
        }
        // ELSE INPUT FIELD LENGTH IS NOT WITHIN RANGE
    } else {
        // SET CRITERIA TO FALSE
        passwordCriteria['passwordLength'] = false
        // IF IT ISN'T ALREADY WITHOUT FILL
        if (!$(iconId).hasClass('bi-check-circle')){
            $(iconId).removeClass()
            $(iconId).addClass('bi bi-check-circle')
        }
    }
}

// UPPERCASE/NUMBER CHECKER
function regexCheck(iconId, regex){
    if ($("#inputPassword").val().match(regex)){
        // SET CRITERIA TO TRUE FOR EACH ID
        if (iconId == '#uppercaseCheck'){
            passwordCriteria['passwordUppercase'] = true
        } else if (iconId == "#numberCheck"){
            passwordCriteria['passwordNumber'] = true
        }
        // IF IT ISN'T ALREADY FILLED
        if (!$(iconId).hasClass('bi-check-circle-fill')){
            $(iconId).removeClass()
            $(iconId).addClass('bi bi-check-circle-fill')
        }
    } else {
        // SET CRITERIA TO FALSE FOR EACH ID
        if (iconId == '#uppercaseCheck'){
            passwordCriteria['passwordUppercase'] = false
        } else if (iconId == "#numberCheck"){
            passwordCriteria['passwordNumber'] = false
        }
        // IF IT ISN'T ALREADY WITHOUT FILL
        if (!$(iconId).hasClass('bi-check-circle')){
            $(iconId).removeClass()
            $(iconId).addClass('bi bi-check-circle')
        }
    }
}

// BOTH PASSWORDS MATCH CHECKER
function passwordMatch(firstId, secondId, iconId){
    // TO PREVENT BOTH EMPTY INPUTS BEING A MATCH
    if ($(firstId).val().length > 0 && $(secondId).val().length > 0){
        // IF BOTH INPUTS HAVE THE SAME VALUE
        if ($(firstId).val() == $(secondId).val()){
            // SET CRITERIA TO TRUE
            passwordCriteria['passwordMatch'] = true
            // IF IT ISN'T ALREADY FILLED
            if (!$(iconId).hasClass('bi-check-circle-fill')){
                $(iconId).removeClass()
                $(iconId).addClass('bi bi-check-circle-fill')
            }
        } else {
            // SET CRITERIA TO FALSE
            passwordCriteria['passwordMatch'] = false
            // IF IT ISN'T ALREADY WITHOUT FILL
            if (!$(iconId).hasClass('bi-check-circle')){
                $(iconId).removeClass()
                $(iconId).addClass('bi bi-check-circle')
            }
        }
    }
}

// RUNS PASSWORD CHECKER FUNCTIONS ON PASSWORD INPUT FIELDS
$("input:password").on('input', function(){
    characterLength("#characterLength")
    regexCheck("#uppercaseCheck", "[A-Z]")
    regexCheck("#numberCheck", "[0-9]")
    passwordMatch("#inputPassword", "#inputConfirmPassword", "#matchCheck")

    // IF ALL CRITERIA IS MET ON SIGN UP, ENABLE SUBMIT
    if (!Object.values(passwordCriteria).includes(false)){
        $(".password-criteria").prop('disabled', false)
    } else {
        // ELSE MAKE IT DISABLED
        $(".password-criteria").prop('disabled', true)
    }

    // IF EXISTING PASSWORD HAS BEEN ENTERED ON UPDATE ACCOUNT, ENABLE SUBMIT
    if ($("#inputExistingPassword").val().length > 7){
        $(".password-criteria").prop('disabled', false)
    } else {
        $(".password-criteria").prop('disabled', true)
    }
})