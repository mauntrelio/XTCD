var PCA9685 = (function($,window,document,undefined) {

  var bind_ranges = function() {
    $('input[type=range]').on("input",function(){
      var $this = $(this);
      var value = parseInt($this.val());
      var index = $this.data("index");
      $this.next("span").html(value);
      var other = ($this.hasClass("start")) ? "end" : "start";
      var $other = $("#channel_"+index+"_"+other);
      if ($other.length) {
        var other_value = parseInt($other.val());
        if (other == "end") {
          if (other_value <= value) {
            $other.val(value+1);
          }
        } else {
          if (other_value > value) {
            $other.val(value-1);
          }
        }
        $other.next("span").html($other.val());
      }
      $this.parents("tr").addClass("danger");
    });
  }

  var init = function() {
    bind_ranges();
  };

  return {
    init: init
  };

}(jQuery, window, document));
