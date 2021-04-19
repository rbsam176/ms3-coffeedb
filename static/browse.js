// $( "input[name='tag']" ).on("change", function(){
//     var checkedLength = $( "input[name='tag']:checked" ).length;
//     if(checkedLength == 0){
//         // UNCHECKING LAST CHECKBOX WILL REDIRECT TO /BROWSE
//         window.location.href = "/browse"
//     } else {
//         // CLICKING ON NOTES TAG WILL SUBMIT FORM
//         $( "#submitCriteria" ).click()
//     }
// });

// CLICKING SHOW MORE ON NOTES
$("#showMoreNotes").on('click', function(){
    if ($("#showMoreNotes").text().includes("Show more")) {
        // TOGGLE BUTTON TEXT
        $("#showMoreNotes").html("Show less <i class='bi bi-chevron-compact-up'></i>")
        // SHOWS EXTRA NOTES
        $(".extra-note").each(function(index){
            $(this).css('display', 'inline-block')
        })
    } else if ($("#showMoreNotes").text().includes("Show less")){
        // TOGGLE BUTTON TEXT
        $("#showMoreNotes").html("Show more <i class='bi bi-chevron-compact-down'></i>")
        // HIDE EXTRA NOTES
        $(".extra-note").each(function(index){
            $(this).css('display', 'none')
        })
    }
})

// CLICKING SHOW MORE ON ORIGIN
$("#showMoreOrigin").on('click', function(){
    if ($("#showMoreOrigin").children('i').hasClass('bi bi-chevron-compact-down')) {
        // TOGGLE BUTTON ICON
        $("#showMoreOrigin").children('i').removeClass('bi-chevron-compact-down')
        $("#showMoreOrigin").children('i').addClass('bi-chevron-compact-up')
        
        // SHOW OVERFLOW ORIGINS
        if ($(".origin-box").hasClass('originOptionsExtra')){
            $(".origin-box").removeClass('originOptionsExtra')
        }

    } else if ($("#showMoreOrigin").children('i').hasClass('bi bi-chevron-compact-up')) {
        // TOGGLE BUTTON ICON
        $("#showMoreOrigin").children('i').removeClass('bi-chevron-compact-up')
        $("#showMoreOrigin").children('i').addClass('bi-chevron-compact-down')
        // HIDE OVERFLOW ORIGINS
        if (!$(".origin-box").hasClass('originOptionsExtra')){
            $(".origin-box").addClass('originOptionsExtra')
        }
    }
})

// on page load if origin/note checked then ensure show all is enabled




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
