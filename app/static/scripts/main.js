$(document).ready(function() {

  var x = 0;
  var y = 0;
  var dir = '';

  var updateXandYFromTemplate = function() {
    var p = $('#prevCoors p:first-child').first()
    if (p.length > 0) {
      var text = p.text()
      var arr = text.split(',');
      x = arr[0];
      y = arr[1];
    }
  }

  updateXandYFromTemplate();

  $('button#movement').on('click', function(e) {
    e.preventDefault();
    var dir = $(this).text();
    sendRequest(x, y, dir);
  })

  var sendRequest = function(x,y,dir) {
    $.ajax({
      type: "POST",
      url: "/walk/" + x + "/" + y + "/" + dir,
      data: "",
      success: function(result, err) {
        console.log(result)
        handleResult(result, dir)
      },
    });
  }

  var handleResult = function(result, dir) {
    console.log(dir)
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
    $('#prevCoors').prepend('<p>' + x + ',' + y + ',' + dir + ' - This move is ' + result.validMove + '</p>');

    if (result.data.length > 0) {
      $('#prevCoors').prepend('<a href="' + result.data + '"">Click here</a>');
    }
  }
});
