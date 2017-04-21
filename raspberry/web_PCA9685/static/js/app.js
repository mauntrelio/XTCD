var App = (function($,window,document,undefined){

  var App = {};

  App.init = function(){
    if (typeof PCA9685 !== "undefined") {
      PCA9685.init();
    }
  };

  return App;

}(jQuery,window,document));


App.init();
