$(document).ready(function() {

  var x = window.x;
  var y = window.y
  var dir = '';

  $('button#movement').on('click', function(e) {
    e.preventDefault();
    var dir = $(this).text();
    sendRequest(x, y, dir);
  })

  var sendRequest = function(x,y,dir) {
    $.ajax({
      type: "GET",
      url: "/walk/" + x + "/" + y + "/" + dir,
      data: "",
      success: function(result) {
        handleResult(result, dir)
      },
    });
  }

  var handleResult = function(result, dir) {
    if (result.validMove === true) {
      switch (dir) {
        case 'left':
          x--;
          break;
        case 'up':
          y++;
          break;
        case 'right':
          x++;
          break;
        case 'down':
          y--;
          break;
        default:
      }
    }
    $('#prevCoors').prepend('<p> You moved from ' + x + ',' + y + ' in the direction ' + 
        dir + ' - This move is ' + result.validMove + '</p>');

    if (result.data.length > 0) {
      $('#prevCoors').prepend('<a href="' + result.data + '"">Click here</a>');
    }
  }
});
