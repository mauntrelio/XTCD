var XTCD = (function($,window,document,undefined) {

  "use strict";

  var update_view = function(data){
    if (data.PWM && $("#pwm-status").length) {
      for (var i = 0; i < 16; i++) {
        if (data.PWM[i] !== null) {
          $("#pwm-"+i).find("span").html(data.PWM[i]);  
        } else {
          $("#pwm-"+i).find("span").html("");
        }
      }
    }
  };

  var bind_buttons = function () {

    $(".drone-control").on("click",function(){
      var $this = $(this);
      var command = $this.data("command");
      $.post("/"+command, this.dataset, update_view);
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
        $.post("/" + event.command, event.data, update_view);
      }
	  });
  }

  var toggle_pwm_status = function() {
    $("#show-pwm").on("click", function(){
      if ($(this).is(":checked")) {
        $("#pwm-status").show();
      } else {
        $("#pwm-status").hide();
      }
    });
  }

  var validate_config = function() {
    $("#save-config").on("submit", function(e){
      var web_config, drone_config;

      try {
        JSON.parse($("#web-config").val());
        web_config = true;
      } catch(e) {
        web_config = false;
      }

      try {
        JSON.parse($("#drone-config").val());
        drone_config = true;
      } catch(e) {
        drone_config = false;
      }

      if (!web_config) {
        alert("Error in web configuration file! Cannot save!");
        e.preventDefault();
      } else if (!drone_config) {
        alert("Error in drone configuration file! Cannot save!");
        e.preventDefault();
      } else {
        $(this).submit();
      }
    })
  }


  var init = function() {
    bind_buttons();
    bind_keys();
    toggle_pwm_status();
    validate_config();
  };

  return {
    init: init
  };

}(jQuery, window, document));
