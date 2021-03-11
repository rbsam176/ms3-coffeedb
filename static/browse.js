// function roastGoTo(checkedBox){
//     console.log(checkedBox.value)
//     window.location.href = `/browse/roast=${checkedBox.value}`
// }

// function gatherState(){
//     $(" .filter-checks ").children('input').each(function() {
//         if ($(this).prop('checked')) {
//             console.log($(this).attr('value'))
//         }
//     })
// }

$("#organicRequired").on('click', function(){
    if ($("#organicLabel").text() == "Not required"){
        $("#organicLabel").text("Is required")
    } else if ($("#organicLabel").text() == "Is required"){
        $("#organicLabel").text("Not required")
    }
})
