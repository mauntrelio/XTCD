(function(window, document, undefined){

	var move = function(pos){
		window.location.href="/?pos=" + pos; 
	};

	var init = function() {
		
		document.addEventListener("keydown", function(event) {
		  if (event.code == "ArrowLeft") {
		  	move("000");
		  } else if (event.code == "ArrowUp") {
		  	move("090");
		  } else if (event.code == "ArrowRight") {
				move("180");
		  }
		});

		document.getElementById("container").addEventListener("click", function(event){
			if (event.target && event.target.matches("div.button")) {
				event.preventDefault();
				event.stopPropagation();
				move(event.target.dataset.position);
			}
		});

	};

	return {
		init: init
	};

}(window, document)).init();
