// TOGGLES ORGANIC LABEL TEXT
$( "#organicToggle" ).on('click', function(){
    if ($( "#organicLabel" ).text() == "Off"){
        $( "#organicLabel" ).text("On")
    } else if ($( "#organicLabel" ).text() == "On"){
        $( "#organicLabel" ).text("Off")
    }
})

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

// CHECKS IF NOTES CHECKBOXES ARE CHECKED ON LOAD AND APPENDS TO LIVE PREVIEW
$(document).ready(function() {
    for (x in $(".note-checkbox")) {
        if ($(".note-checkbox").eq(x).is(':checked')){
            console.log($(".note-checkbox").eq(x).parent().text())
            appendToPreview($(".note-checkbox").eq(x).parent().text())
        }
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

// CHANGES LIVE PREVIEW IMAGE TO IMAGE URL INPUT VALUE
// SOURCE https://stackoverflow.com/a/13388240
$("#imgURL").focusout(function(){
    if (/(jpg|gif|png|JPG|GIF|PNG|JPEG|jpeg)$/ in $("#imgURL").val()){
        $("#imgPreview").attr('src', $("#imgURL").val())
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
    // const client = filestack.init("AvaoIzsbLTTG0R1N7vg2Uz"); ORIGINAL
    const client = filestack.init("AX7dD5B3WTAzYpPXMkcSBz"); // NEW

    const options = {
        // WRITES URL TO TEXT INPUT
        // IF ON MOBILE VIEW, HIDE UPLOADER UI AND INSERT RESET UI
        onFileUploadFinished: file => {
            $("#imgURL").val(file['url'])
            $("#imgPreview").attr('src', file['url'])
            if ($("#livePreview").is(":hidden")){
                $(".img-upload").css('background-image', `url("${file['url']}")`)
                $(".img-upload").css('background-size', 'cover')
                $("#img-filebrowser").css('display', 'none')
                $('#resetUpload').css('display', 'block')
            }
        },
        accept: 'image/*'
    }
    client.picker(options).open()
})

// ON WINDOW RESIZE, HIDE/SHOW UPLOAD UI AND RESET UI
$(window).resize(function(){     
    if ($("#livePreview").is(":visible")){ // DESKTOP
        if ($(".img-upload").css('background-image') != 'none'){ // HAS BACKGROUND
            $(".img-upload").css('background-image', "") // HIDE BACKGROUND
            $(".img-upload").css('background-size', "")
            $("#img-filebrowser").css('display', 'block') // SHOW UPLOADER
            $('#resetUpload').css('display', 'none') // HIDE RESET BUTTON
        }
    } else if ($("#livePreview").is(":hidden")){ // MOBILE
        if ($(".img-upload").css('background-image') == 'none'){ // HAS NO BACKGROUND
            if ($('#imgURL').val()){ // IF IMAGE EXISTS
                $(".img-upload").css('background-image', `url("${$('#imgURL').val()}")`) // SHOW IMAGE
                $(".img-upload").css('background-size', 'cover')
                $("#img-filebrowser").css('display', 'none') // HIDE UPLOADER
                $('#resetUpload').css('display', 'block') // SHOW RESET BUTTON
            }
        } else if ($(".img-upload").css('background-image') != 'none'){ // HAS BACKGROUND
            $("#img-filebrowser").css('display', 'none') // HIDE UPLOADER
            $('#resetUpload').css('display', 'block') // SHOW RESET BUTTON
        }
    }
});

// RESETS MOBILE UPLOADER BACK TO DEFAULT
$("#resetUpload").on('click', function(){
    $(".img-upload").css('background-image', "")
    $(".img-upload").css('background-size', "")
    $("#img-filebrowser").css('display', 'block')
    $('#imgURL').val("")
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