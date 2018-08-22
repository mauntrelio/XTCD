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
  };

  var toggle_pwm_status = function() {
    $("#show-pwm").on("click", function(){
      if ($(this).is(":checked")) {
        $("#pwm-status").show();
      } else {
        $("#pwm-status").hide();
      }
    });
  };

  var validate_config = function() {

    $("#save-config").on("submit", function(event){

      var configs = [
        {
          "config": $("#web-config").val(),
          "valid": undefined,
          "file": "web"
        },
        {
          "config": $("#drone-config").val(),
          "valid": undefined,
          "file": "drone"
        }
      ];

      var valid = true;

      configs.forEach(function(config){
        try {
          JSON.parse(config.config);
          config.valid = true;
        } catch(err) {
          config.valid = false;
        }
        if (!config.valid) {
          alert("Error in " + config.file + " configuration file! Cannot save!");
          valid = false;
        } 
      });

      return valid;
      
    })
  };


  var update_sensors = function() {
    $(".diagnostic").each(function(index){
      var $element = $(this);
      var sensor_id = $element.data("sensorId");
      $.ajax({
        url: "/sensor?id=" + sensor_id
      }).done(function(data){
        $element.html(data.value + " " + data.unit);
      });  
    });
  }


  var init = function() {
    bind_buttons();
    bind_keys();
    toggle_pwm_status();
    validate_config();
    update_sensors();
    setInterval(update_sensors, 30000);
  };

  return {
    init: init
  };

}(jQuery, window, document));
