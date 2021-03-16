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

// APPENDS CHECKED NOTE TO PREVIEW RENDER
$(".add-notes-checkboxes").children("input").on("click", function() {
    if($(this).is(':checked')){
        $(".preview-notes-container").append(`<span class="note-bubble tag-preview bean-note">${$(this).next('label').text()}</span>`)
    } else if(!$(this).is(':checked')){
        $(".preview-notes-container").children(`.tag-preview:contains(${$(this).next('label').text()})`).remove()
    }
})