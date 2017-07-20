var XTCD = (function($,window,document,undefined) {

  "use strict";

  var bind_buttons = function () {

    $(".drone-control").on("click",function(){
      var $this = $(this);
      var command = $this.data("command");
      $.post("/"+command, this.dataset,
        function(data){
          console.log(data);
      });
    });

  };

  var bind_keys = function() {
    var mapping = {};

    $(".drone-control").each(function(){
      var element = this;
      var $this = $(element);
      if ($this.data("keys")) {
        var keys = $this.data("keys").split(",");
        var command = $this.data("command");
        keys.forEach(function(key){
          mapping[key] = { command: command, data: element.dataset };
        });
      }
    });

    document.addEventListener("keydown", function(e) {
      var event = (mapping[e.code]) ? mapping[e.code] : mapping[e.key];
      if (event) {
        $.post("/" + event.command, event.data,
          function(data){
            console.log(data);
        });
      }
	  });
  }

  var init = function() {
    bind_buttons();
    bind_keys();
  };

  return {
    init: init
  };

}(jQuery, window, document));
