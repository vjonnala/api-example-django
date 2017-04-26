
var idleTime = 0;
function start_idle_timer(threshold, url){
    //Increment the idle time counter every minute.
    var idleInterval = setInterval(timerIncrement, 1000, threshold, url); // 1 second

    //Zero the idle timer on mouse movement.
    $(this).mousemove(function () {
        idleTime = 0;
    });
    $(this).keypress(function () {
        idleTime = 0;
    });
}

function timerIncrement(threshold, url) {
    idleTime = idleTime + 1;
    if (idleTime > threshold) {
        window.location =  url;
    }
}