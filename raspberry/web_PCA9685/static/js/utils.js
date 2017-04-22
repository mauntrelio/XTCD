var Utils = (function($,window,document,undefined){

  "use strict";

  var round = function(number, precision) {
    var factor = Math.pow(10, precision);
    var tempNumber = number * factor;
    var roundedTempNumber = Math.round(tempNumber);
    return roundedTempNumber / factor;
  };

  return {
    round: round
  };

}(jQuery,window,document));
