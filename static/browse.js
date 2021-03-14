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
