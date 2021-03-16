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
            $(dynamicElements[x][1]).text($(this).val())
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
        console.log("clicked")
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
        $(".add-notes-container").append(`<li class="add-notes-checkboxes"><label><input class="note-checkbox" type="checkbox" checked>${rawInputText}</label></li>`)
        appendToPreview(rawInputText)
        $("#customNoteInput").val('')
    } else {
        $("#customNoteInput").effect("shake")
        $("#customNoteInput").focus()
    }
})