// IF USER SELECTS 'OTHER' IN DROPDOWN, PRESENT TEXT INPUT AND MAKE IT REQUIRED
$('.dynamicSelection').on('change', function () {
    var toggleInput = $(this).parent().next('.toggleInput')
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
    var parentSelect = $(this).prev('div').children('.dynamicSelection')
    var customInput = $(this).children('.customInput')
    if( $(customInput).val().length === 0 ) {
        $(parentSelect).attr("disabled", false);
    } else {
        $(parentSelect).attr("disabled", true);
        if ($(this).prev().children('select').attr('id') == "brandInput"){
            $("#brand-preview").text(customInput.val())
        } else if ($(this).prev().children('select').attr('id') == "originInput") {
            $("#origin-preview").text(customInput.val())
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
$("#organicToggle").on("click", function() {
    if($(this).is(':checked')){
        $("#organic-preview").text("True")
    } else if(!$(this).is(':checked')){
        $("#organic-preview").text("False")
    }
})

// ASSIGNS LIVE PREVIEW LINK TO USER INPUT
// CURRENTLY HTML FORCES HTTP REQUIREMENT, TRY TO ALLOW JUST WWW. <-----
$("#websiteInput").on('input', function() {
    $("#website-preview").attr('href', $(this).val())
})

// APPENDS HTML TO PREVIEW RENDER CONTAINER
function appendToPreview(tag){
    $(".preview-notes-container").append(`<span class="note-bubble tag-preview bean-note">${tag}</span>`)
}

// LISTENS FOR NOTE CHECKED AND RUNS APPENDING FUNCTION OR REMOVES
// HAD DOM BUBBLING ISSUE, WHERE IF THE ELEMENT DOESN'T EXIST ON DOCUMENT READY THEN IT CAN'T TARGET DYNAMICALLY CREATED ELEMENTS
// USED https://stackoverflow.com/a/40280312 FOR SUPPORT
$("form").on('change', 'input:checkbox.note-checkbox', function() {
    if($(this).is(':checked')){
        appendToPreview($(this).parent().text())
    } else if(!$(this).is(':checked')){
        $(".preview-notes-container").children(`.tag-preview:contains(${$(this).parent().text()})`).remove()
    }
})

// ADDS CUSTOM INPUT NOTE TO INPUT CONTAINER AND LIVE PREVIEW CONTAINER
$("#addNote").on('click', function(e) {
    e.preventDefault()
    var rawInputText = $("#customNoteInput").val()
    if (rawInputText.length > 0){
        $(".add-notes-container").append(`<li class="add-notes-checkboxes"><label><input class="note-checkbox" name="note" value="${rawInputText}" type="checkbox" checked>${rawInputText}</label></li>`)
        appendToPreview(rawInputText)
        $("#customNoteInput").val('')
    } else {
        $("#customNoteInput").effect("shake")
        $("#customNoteInput").focus()
    }
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
        $(".add-notes-container").effect("shake")
        return false
    }
})

// LINKS TO FILESTACK IMAGE UPLOAD API
$("#uploadTrigger").on('click', function(e){
    const client = filestack.init("AvaoIzsbLTTG0R1N7vg2Uz");
    const options = {
        onFileUploadFinished: file => {
            $("#imgURL").val(file['url'])
            $("#imgPreview").attr('src', file['url'])
            }
        }
    client.picker(options).open()
})