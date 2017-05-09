var XTCD = (function($,window,document,undefined) {

  "use strict";

  var bind_buttons = function () {

    $(".drone-control").on("click",function(){
      var $this = $(this);
      var command = $this.data("command");
      $.post("/"+command, {},
        function(data){
          console.log(data);
      });
    });

  };

  var bind_keys = function() {
    var mapping = {};

    $(".drone-control").each(function(){
      var $this = $(this);
      if ($this.data("keys")) {
        var keys = $this.data("keys").split(",");
        var command = $this.data("command");
        keys.forEach(function(key){
          mapping[key] = command;
        });
      }
    });

    document.addEventListener("keydown", function(event) {
      console.log(event.code);
      console.log(event.key);
      var command = (mapping[event.code]) ? mapping[event.code] : mapping[event.key];
      if (command) {
        $.post("/"+command, {},
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
