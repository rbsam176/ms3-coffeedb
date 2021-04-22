$("#main").css('display', 'none')

// CYCLES THROUGH BOTH VIDEOS
$(document).ready(function(){
    $('video').on('ended',function(){
        if ($('.primary-video').css('display') == 'block') {
            $(this).css('display', 'none')
            $(this).next().css('display', 'block')
            $(this).next().trigger('play')
        }
        if ($('.secondary-video').css('display') == 'block') {
            $(this).css('display', 'none')
            $(this).prev().css('display', 'block')
            $(this).prev().trigger('play')
        }
    });
  });