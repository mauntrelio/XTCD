var XTCD = (function($,window,document,undefined) {

  "use strict";

  var XTCD = {};

  XTCD.update_view = function(data){
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

  XTCD.bind_buttons = function () {

    $(".drone-control").on("click",function(){
      var $this = $(this);
      var command = $this.data("command");
      var callback = $this.data("callback");
      if (command) {
        $.post("/"+command, this.dataset, XTCD.update_view);  
      } else if (callback) {
        XTCD[callback]();
      }
      
    });

  };

  XTCD.bind_keys = function() {
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
      var targetElement = e.target || e.srcElement;
      var event = (mapping[e.code]) ? mapping[e.code] : mapping[e.key];
      if (!(targetElement.tagName == "TEXTAREA") && !(targetElement.tagName == "INPUT")){
        e.preventDefault();
      };
      if (event) {
        $.post("/" + event.command, event.data, XTCD.update_view);
      }
	  });
  };

  XTCD.toggle_pwm_status = function() {
    $("#show-pwm").on("click", function(){
      if ($(this).is(":checked")) {
        $("#pwm-status").show();
      } else {
        $("#pwm-status").hide();
      }
    });
  };

  XTCD.validate_config = function() {

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


  XTCD.update_sensors = function() {
    $(".diagnostic").each(function(index){
      var $element = $(this);
      var sensor_id = $element.data("sensorId");
      $.ajax({
        url: "/sensor?id=" + sensor_id
      }).done(function(data){
        if (data.value === null) {
          $element.html("N/A");
        } else {
          $element.html(data.value + " " + data.unit);
        }  
      });  
    });
  }


  XTCD.init = function() {
    XTCD.bind_buttons();
    XTCD.bind_keys();
    XTCD.toggle_pwm_status();
    XTCD.validate_config();
    XTCD.update_sensors();
    setInterval(XTCD.update_sensors, 30000);
  };

  return XTCD;

}(jQuery, window, document));
