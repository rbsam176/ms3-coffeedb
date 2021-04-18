// TOGGLES ORGANIC LABEL TEXT
$( "#organicRequired" ).on('click', function(){
    if ($( "#organicLabel" ).text() == "Not required"){
        $( "#organicLabel" ).text("Is required")
    } else if ($( "#organicLabel" ).text() == "Is required"){
        $( "#organicLabel" ).text("Not required")
    }
})

$( "input[name='tag']" ).on("change", function(){
    var checkedLength = $( "input[name='tag']:checked" ).length;
    if(checkedLength == 0){
        // UNCHECKING LAST CHECKBOX WILL REDIRECT TO /BROWSE
        window.location.href = "/browse"
    } else {
        // CLICKING ON NOTES TAG WILL SUBMIT FORM
        $( "#submitCriteria" ).click()
    }
});

// CLICKING SHOW MORE
$("#showMore").on('click', function(){
    if ($("#showMore").text() == "Show more"){
        // TOGGLE BUTTON TEXT
        $("#showMore").text("Show less")
        // SHOWS EXTRA NOTES
        $(".extra-note").each(function(index){
            $(this).css('display', 'inline-block')
        })
    } else if ($("#showMore").text() == "Show less"){
        // TOGGLE BUTTON TEXT
        $("#showMore").text("Show more")
        // HIDE EXTRA NOTES
        $(".extra-note").each(function(index){
            $(this).css('display', 'none')
        })
    }
})


// function myFunc(data) {
//     $("#showMore").on('click', function(){
//         $("#showMore").text('Show Less')
//         $(".checkbox-container").each(function(index){
//             if (index > 5){
//                 $(this).css('display', 'none')
//             }
//         })
//         for (item in data){
//             if (data[item][1] > 75){
//                 size = "cloud-75"
//             } else if (data[item][1] > 50) {
//                 size = "cloud-50"
//             } else if (data[item][1] > 50) {
//                 size = "cloud-25"
//             } else {
//                 size = "cloud-0"
//             }
//             $("#notesContainer").append(`
//                 <span class="checkbox-container my-2">
//                     <input type="checkbox" id="${data[item][0]}" form="filterCriteria" name="tag" value="${data[item][0]}">
//                     <label for="${data[item][0]}" class="note-bubble my-auto ${size} cloud-note">${data[item][0]}</label>
//                 </span>
//             `)
//         }
//     })
//     return data
// }

// var availableTags = [
//     "ActionScript",
//     "Nothing"
// ]

// $( "#searchCriteria" ).autocomplete({
//     source: availableTags
// });
