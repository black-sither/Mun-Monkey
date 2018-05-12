
//Preloading animation.
var interval;
document.onreadystatechange = function (){
  var state = document.readyState
  if (state == 'interactive') {
       document.getElementById('contents').style.visibility="hidden";
       function blink_text(){
        $('#logo').fadeOut(1000);
        $('#logo').fadeIn(1000);
        console.log("blink");
        }
    interval = setInterval(blink_text, 1);
  } else if (state == 'complete') {
      setTimeout(function(){
        clearInterval(interval);
         document.getElementById('interactive');
         document.getElementById('load').style.visibility="hidden";
         document.getElementById('contents').style.visibility="visible";
      },1000);
  }
}

$(document).ready(function(){
   
        $('#login').click(function()
        {
            naam=$("#username").val()
            console.log(naam)
            cook="Loginwala=" + naam +";";
            console.log("original cookie supposed to be: " + cook)
            document.cookie=cook
        });
       
});