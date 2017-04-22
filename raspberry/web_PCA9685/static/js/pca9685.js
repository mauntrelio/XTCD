var PCA9685 = (function($,window,document,undefined) {

  "use strict";

  var set_range_label = function(range) {
    range.next("div.range-value").find("span").html(range.val());
  };

  var update_pulse = function(index, start, end) {
    var freq = parseInt($("#freq").val());
    var length = Math.abs(start - end);
    var pulse_lenght = Utils.round(length / (4096 * freq ) * 1000, 2);
    $("#pulse_" + index).html(pulse_lenght + " ms");
  };

  var bind_ranges = function() {
    $("input[type=range]").on("input",function(){
      var $this = $(this);
      var value = parseInt($this.val());
      var index = $this.data("index");
      set_range_label($this);
      var other = ($this.hasClass("start")) ? "end" : "start";
      var $other = $("#channel_"+index+"_"+other);
      if ($other.length) {
        var other_value = parseInt($other.val());
        var test = (other_value <= value);
        var new_value = value + 1;
        if (other == "start") {
          test = (other_value > value);
          new_value = value - 1;
        }
        if (test) {
          $other.val(new_value);
        }
        set_range_label($other);
      }
      $this.parents("tr").addClass("danger");
      update_pulse(index, value, other_value);
    });
  }

  var init = function() {
    bind_ranges();
  };

  return {
    init: init
  };

}(jQuery, window, document));
