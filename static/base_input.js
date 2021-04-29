// IF USER SELECTS 'OTHER' IN DROPDOWN, PRESENT TEXT INPUT AND MAKE IT REQUIRED
$('.dynamicSelection').on('change', function () {
    var toggleInput = $(this).parent().next('.toggleInput')
    if ($(this).val() == "Other..."){
        $(toggleInput).css('display', 'block')
        $(toggleInput).children().prop('required', true)
        $(toggleInput).children('input').focus()
    } else {
        $(toggleInput).css('display', 'none')
        $(toggleInput).children().prop('required', false)
    }
});

// ON 'OTHER' TEXT INPUT, MAKE DROPDOWN DISABLED
$(".toggleInput").on('input', function() {
    var parentSelect = $(this).prev('div').children('.dynamicSelection')
    var dynamicInput = $(this).children('.dynamicInput')
    if( $(dynamicInput).val().length === 0 ) {
        $(parentSelect).prop("disabled", false);
    } else {
        $(parentSelect).prop("disabled", true);
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
    for (var x in dynamicElements){
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
$("#websiteInput").on('input', function() {
    $("#website-preview").attr('href', $(this).val())
})

// APPENDS HTML TO PREVIEW RENDER CONTAINER
function appendToPreview(tag){
    $(".preview-notes-container").append(`<span class="note-bubble card-notes tag-preview bean-note">${tag}</span>`)
}

// CHECKS NUMBER OF CHECKED NOTES AND DISABLES TO PREVENT FURTHER ADDITIONS
function limitNotes(){
    if ($('input:checkbox.note-checkbox:checked').length >= 4){
        $("input:checkbox.note-checkbox").each(function() {
            if(!$(this).is(':checked')){
                $(this).prop('disabled', true)
                $("#customNoteInput").prop('disabled', true)
            }
        });
    }
    if ($('input:checkbox.note-checkbox:checked').length < 4){
        console.log('else')
        $("input:checkbox.note-checkbox").each(function(index) {
            if($("input:checkbox.note-checkbox").eq(index).is(':disabled')){
                $(this).prop('disabled', false)
                $("#customNoteInput").prop('disabled', false)
            }
        });
    }
}

// LISTENS FOR NOTE CHECKED AND RUNS APPENDING FUNCTION OR REMOVES
// SOURCE https://stackoverflow.com/a/40280312
$("form").on('change', 'input:checkbox.note-checkbox', function() {
    if($(this).is(':checked')){
        limitNotes()
        appendToPreview($(this).parent().text())
    } else if(!$(this).is(':checked')){
        $(".preview-notes-container").children(`.tag-preview:contains(${$(this).parent().text().trim()})`).remove()
        limitNotes()
    }
})

// ADDS CUSTOM INPUT NOTE TO INPUT CONTAINER AND LIVE PREVIEW CONTAINER
$("#addNote").on('click', function(e) {
    e.preventDefault()
    var rawInputText = $("#customNoteInput").val()
    if (rawInputText.length > 0){
        $(".add-notes").append(`
        <span class="checkbox-container m-1">
            <input type="checkbox" id="${rawInputText.replace(' ', '')}" class="note-checkbox" name="note" value="${rawInputText}" checked>
            <label for="${rawInputText.replace(' ', '')}" class="filter-toggle">${rawInputText}</label>
        </span>
        `)
        appendToPreview(rawInputText)
        $("#customNoteInput").val('')
        limitNotes()
    } else {
        $("#customNoteInput").effect("shake")
        $("#customNoteInput").focus()
    }
})

// RECEIVES UPLOADED IMAGE, CONVERTS TO BASE64 AND DISPLAYS IN LIVE PREVIEW
// SOURCE https://stackoverflow.com/questions/12660124/javascript-jquery-preview-image-before-upload
$("#uploadImg").on('change', function(){
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

var totalNotes = $(".add-notes").children('span.checkbox-container').length

$("#showMoreNotes").on('click', function(){
    if ($("#showMoreNotes").text().includes("Show all")) {
        // TOGGLE BUTTON TEXT
        $("#showMoreNotes").html("Show less <i class='bi bi-chevron-compact-up'></i>")
        // SHOWS EXTRA NOTES
        $( ".checkbox-container" ).each(function( index ) {
            $(this).css('display', 'inline-block')
        });
    } else if ($("#showMoreNotes").text().includes("Show less")){
        // TOGGLE BUTTON TEXT
        $("#showMoreNotes").html(`Show all ${totalNotes} notes <i class='bi bi-chevron-compact-down'></i>`)
        // HIDE EXTRA NOTES EXCEPT THOSE THAT ARE CHECKED
        $( ".checkbox-container" ).each(function( index ) {
            if (index > 10 && $(this).children('input').prop('checked') != true){
                $(this).css('display', 'none')
            }
        });
    }
})

$(document).ready(function() {
    // CHECKS IF NOTES CHECKBOXES ARE CHECKED ON LOAD AND APPENDS TO LIVE PREVIEW
    for (var x in $(".note-checkbox")) {
        if ($(".note-checkbox").eq(x).is(':checked')){
            console.log($(".note-checkbox").eq(x).parent().text())
            appendToPreview($(".note-checkbox").eq(x).parent().text())
        }
    }

    // SHOW ONLY 10 NOTES AND THOSE THAT ARE CHECKED BY DEFAULT ON PAGE LOAD
    $( ".checkbox-container" ).each(function( index ) {
        if (index > 10 && $(this).children('input').prop('checked') != true){
            $(this).css('display', 'none')
        }
    });

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
        $( "#customNoteInput" ).autocomplete({
            source: jsonParsed.notes
        });
    });
})