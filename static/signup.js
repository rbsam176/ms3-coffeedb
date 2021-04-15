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

$(".swatch-btn").on('click', function(){
    var clickedSwatchName = $(this).attr('name')
    if ($(this).parent().parent().attr('id') == 'bgSwatches'){
        $("#avatar").children('div').removeClass()
        $("#avatar").children('div').addClass(`avatar-circle ${clickedSwatchName}`)
    } else if ($(this).parent().parent().attr('id') == 'iconSwatches'){
        $(".avatar-icon-container").children('i').css('color', `${clickedSwatchName}`)
        // need to change this because clickedSwatchName is a background-color and it needs to be a color
    }
})

// PASSWORD LENGTH CHECKER
function characterLength(iconId){
    if ($("#inputPassword").val().length > 7 && $("#inputPassword").val().length < 16){
        // IF IT ISN'T ALREADY FILLED
        if (!$(iconId).hasClass('bi-check-circle-fill')){
            $(iconId).removeClass()
            $(iconId).addClass('bi bi-check-circle-fill')
        }
        // IF INPUT FIELD LENGTH IS NOT WITHIN RANGE
    } else {
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
        // IF IT ISN'T ALREADY FILLED
        if (!$(iconId).hasClass('bi-check-circle-fill')){
            $(iconId).removeClass()
            $(iconId).addClass('bi bi-check-circle-fill')
        }
    } else {
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
            // IF IT ISN'T ALREADY FILLED
            if (!$(iconId).hasClass('bi-check-circle-fill')){
                $(iconId).removeClass()
                $(iconId).addClass('bi bi-check-circle-fill')
            }
        } else {
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
})