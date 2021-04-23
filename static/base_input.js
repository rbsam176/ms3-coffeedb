// IF USER SELECTS 'OTHER' IN DROPDOWN, PRESENT TEXT INPUT AND MAKE IT REQUIRED
$('.dynamicSelection').on('change', function () {
    var toggleInput = $(this).parent().next('.toggleInput')
    if ($(this).val() == "Other..."){
        $(toggleInput).css('display', 'block')
        $(toggleInput).children().attr('required', true)
        $(toggleInput).children('input').focus()
    } else {
        $(toggleInput).css('display', 'none')
        $(toggleInput).children().attr('required', false)
    }
});

// ON 'OTHER' TEXT INPUT, MAKE DROPDOWN DISABLED
$(".toggleInput").on('input', function() {
    var parentSelect = $(this).prev('div').children('.dynamicSelection')
    var dynamicInput = $(this).children('.dynamicInput')
    if( $(dynamicInput).val().length === 0 ) {
        $(parentSelect).attr("disabled", false);
    } else {
        $(parentSelect).attr("disabled", true);
        if ($(this).prev().children('select').attr('id') == "brandInput"){
            $("#brand-preview").text(dynamicInput.val())
        } else if ($(this).prev().children('select').attr('id') == "originInput") {
            $("#origin-preview").text(dynamicInput.val())
        }
    }
})

// TABLE LINKING THE INPUT ELEMENT WITH THE LIVE PREVIEW ELEMENT
dynamicElements = [
    ["brandInput", "#brand-preview"],
    ["nameInput", "#name-preview"],
    ["roastInput", "#roast-preview"],
    ["originInput", "#origin-preview"]
]

// LISTENS FOR CHANGES TO TEXT INPUTS AND SELECTS
$("select, input").on("keyup change", function() {
    for (x in dynamicElements){
        if (dynamicElements[x].includes($(this).attr("id"))){
            if ($(`#${dynamicElements[x][0]}`).val() == "Other..."){
                return
            } else {
            $(dynamicElements[x][1]).text($(this).val())
            }
        }
    }
})

// LISTENS FOR ORGANIC CHECKBOX CHANGE
$("#organicTrue").on("click", function() {
    $(".organic-preview").text("Organic")
})
$("#organicFalse").on("click", function() {
    $(".organic-preview").text("Not organic")
})

// ASSIGNS LIVE PREVIEW LINK TO USER INPUT
// CURRENTLY HTML FORCES HTTP REQUIREMENT, TRY TO ALLOW JUST WWW. <-----
$("#websiteInput").on('input', function() {
    $("#website-preview").attr('href', $(this).val())
})

// APPENDS HTML TO PREVIEW RENDER CONTAINER
function appendToPreview(tag){
    $(".preview-notes-container").append(`<span class="note-bubble card-notes tag-preview bean-note">${tag}</span>`)
}

// LISTENS FOR NOTE CHECKED AND RUNS APPENDING FUNCTION OR REMOVES
// HAD DOM BUBBLING ISSUE, WHERE IF THE ELEMENT DOESN'T EXIST ON DOCUMENT READY THEN IT CAN'T TARGET DYNAMICALLY CREATED ELEMENTS
// USED https://stackoverflow.com/a/40280312 FOR SUPPORT
$("form").on('change', 'input:checkbox.note-checkbox', function() {
    if($(this).is(':checked')){
        console.log('checked, appending')
        appendToPreview($(this).parent().text())
    } else if(!$(this).is(':checked')){
        console.log('remove')
        console.log($(this).parent().text())
        console.log($(".preview-notes-container").children('.tag-preview').text())
        $(".preview-notes-container").children(`.tag-preview:contains(${$(this).parent().text().trim()})`).remove()
    }
})

// ADDS CUSTOM INPUT NOTE TO INPUT CONTAINER AND LIVE PREVIEW CONTAINER
$("#addNote").on('click', function(e) {
    e.preventDefault()
    var rawInputText = $("#customNoteInput").val()
    console.log(rawInputText)
    console.log(rawInputText.replace(' ', ''))
    if (rawInputText.length > 0){
        // $(".add-notes-container").append(`<li class="add-notes-checkboxes"><label><input class="note-checkbox" name="note" value="${rawInputText}" type="checkbox" checked>${rawInputText}</label></li>`)
        $(".add-notes").append(`
        <span class="checkbox-container m-1">
            <input type="checkbox" id="${rawInputText.replace(' ', '')}" class="note-checkbox" name="note" value="${rawInputText}" checked>
            <label for="${rawInputText.replace(' ', '')}" class="filter-toggle">${rawInputText}</label>
        </span>
        `)
        appendToPreview(rawInputText)
        $("#customNoteInput").val('')
    } else {
        $("#customNoteInput").effect("shake")
        $("#customNoteInput").focus()
    }
})

// RECEIVES UPLOADED IMAGE, CONVERTS TO BASE64 AND DISPLAYS IN LIVE PREVIEW
// SOURCE https://stackoverflow.com/questions/12660124/javascript-jquery-preview-image-before-upload
$("#upload64").on('change', function(){
    var reader = new FileReader();
    reader.onload = function(e) {
        $('.img-preview').attr('src', e.target.result);
        $(".custom-file-label").text("Successfully uploaded!")
    }
    reader.readAsDataURL(this.files[0]);
})


// TOGGLES DISABLED STATE FOR 'ADD' NOTE BUTTON DEPENDING ON INPUT EXISTENCE
$("#customNoteInput").on('input', function() {
    if ($("#customNoteInput").val().length > 0) {
        $("#addNote").prop("disabled", false)
    } else if ($("#customNoteInput").val().length < 1) {
        $("#addNote").prop("disabled", true)
    }
})

// PROVIDES VALIDATION 
$("#submitCoffee").on('click', function(){
    if (!$('.note-checkbox:checked').length){
        $(".add-notes").effect("shake")
        return false
    }
})

// PREVENTS ENTER KEY DEFAULT BEHAVIOUR
// ADDS CUSTOM NOTE TO CONTAINER ON ENTER KEY INPUT
$("#customNoteInput").keydown(function (e) {
    if (e.keyCode == 13) {
        e.preventDefault()
        $("#addNote").click()
        return false
    }
})

$(document).ready(function() {
    // CHECKS IF NOTES CHECKBOXES ARE CHECKED ON LOAD AND APPENDS TO LIVE PREVIEW
    for (x in $(".note-checkbox")) {
        if ($(".note-checkbox").eq(x).is(':checked')){
            console.log($(".note-checkbox").eq(x).parent().text())
            appendToPreview($(".note-checkbox").eq(x).parent().text())
        }
    }
    // AUTOCOMPLETE ASSIGNMENT
    $.getJSON('/autocomplete', function(data) {     
        // PARSES JSON DATA PULLED FROM MONGODB
        var jsonParsed = JSON.parse(data.autocomplete_values);
        // ASSIGNS LIST OF BRANDS TO CUSTOM BRAND INPUT FIELD AUTOCOMPLETE
        $( "#customBrand" ).autocomplete({
            source: jsonParsed.brands
        });
        // ASSIGNS LIST OF ORIGINS TO CUSTOM ORIGIN INPUT FIELD AUTOCOMPLETE
        $( "#customOrigin" ).autocomplete({
            source: jsonParsed.origins
        });
        // ASSIGNS LIST OF NOTES TO CUSTOM NOTE INPUT FIELD AUTOCOMPLETE
        $( "#customNotes" ).autocomplete({
            source: jsonParsed.notes
        });
    });
})