function getSlideElements() {
  return document.querySelectorAll("body section");
}

window.addEventListener('load',function(){
	
	distributeSlides(SlideDistributionFactory.makeVerticalDistributor(getSlideElements().length));
	//distributeSlidesHilbert(true);

	window.addEventListener('keydown',function(e) {
		var currSlide = getCurrentSlide();
		switch(e.keyCode) {
		case 37: // Left Arrow
			currSlide = currSlide.previousElementSibling || currSlide;
			e.preventDefault();
			break;
		case 39: // Right Arrow
			currSlide = currSlide.nextElementSibling || currSlide;
			e.preventDefault();
			break;
		}
		if (e.keyCode == 37 || e.keyCode == 39) {
			window.location.hash = getSlideNumber(currSlide);
		}
		if (e.keyCode == 90) {
			document.getElementsByTagName("body")[0].classList.toggle("zoomed");
		}
	}, false);

	window.addEventListener('resize', function (e) {
		resizeSlides();

		var currSlide = getCurrentSlide();
		document.body.style.top = -currSlide.offsetTop + "px";
		document.body.style.left = -currSlide.offsetLeft + "px";
	}, false);
	
	/*
	window.addEventListener('click', function (e) {        
		var currSlide = getCurrentSlide();
		
		currSlide = currSlide.nextElementSibling || currSlide;
		window.location.hash = getSlideNumber(currSlide);
		e.preventDefault();        		
	}, false);
	*/

        window.addEventListener('hashchange', function(e) {
		hashChange();
	}, false);

	hashChange();
},false);

// Get the 1-based index of the slide that we should be on from the hash.
function getCurrentSlideNumber() {
	var h = parseInt(window.location.hash.substring(1));
	if (!(h > -Infinity)) {
		h = 1;
	}

	return h;
}

// Get the current slide (section element)
function getCurrentSlide() {
	h = getCurrentSlideNumber() - 1; // Our index is 1-based, but we really want to be 0-based.

	var sections = getSlideElements();

	if (h < 0) { h = 0; } // If we're before the the first slide, use the first slide.
	if (h >= sections.length) { h = sections.length - 1; } // If we're after the last slide, use the last slide.

        var currSlide = sections[h];
	return currSlide;
}

// Handle when the hash changes.
function hashChange() {
        var currSlide = getCurrentSlide();

	document.body.style.top = -currSlide.offsetTop + "px";
	document.body.style.left = -currSlide.offsetLeft + "px";
}

// Get the 1-based index of the specified slide.
function getSlideNumber(slide) {
	var siblings = document.getElementsByTagName("section");
	for (var i = 0; i < siblings.length; i++) {
		if (siblings[i] == slide)
			return i + 1;
        }
	return 0;
}

function distributeSlides(distributor) {
	var slides = getSlideElements();
	var bodyWidth = document.body.clientWidth;
	var bodyHeight = document.body.clientHeight;
	var offsetX = bodyWidth;
	var offsetY = bodyHeight;

	for(var i = 0; i < slides.length; i++) {
		var location = distributor(i);

		slides[i].style.width = bodyWidth + "px";
		slides[i].style.height = bodyHeight + "px";
		slides[i].style.left = location.x * offsetX + "px";
		slides[i].style.top = location.y * offsetY + "px";
		slides[i].setAttribute("data-location", "(" + location.x.toString() + "," + location.y.toString() + ")");
	}
}

function resizeSlides() {
	var slides = getSlideElements();

	var bodyWidth = document.body.clientWidth;
	var bodyHeight = document.body.clientHeight;
	var offsetX = bodyWidth;
	var offsetY = bodyHeight;

	for(var i = 0; i < slides.length; i++) {
		var location = Point.parsePoint(slides[i].getAttribute("data-location"));

		slides[i].style.width = bodyWidth + "px";
		slides[i].style.height = bodyHeight + "px";
		slides[i].style.left = location.x * offsetX + "px";
		slides[i].style.top = location.y * offsetY + "px";
	}
}

SlideDistributionFactory = function() {
	function randomD(length) {
		var l = [{ x: 0, y: 0 }]; // The first one is always at (0,0)
		var gridWidth = Math.ceil(Math.sqrt(length))+1;
		var grid = [true];
		for(var i = 1; i < length; i++) {
			do {
				var x = Math.floor(Math.random()*gridWidth);
				var y = Math.floor(Math.random()*gridWidth);
			} while (grid[y*gridWidth + x]);
			grid[y*gridWidth + x] = true;
			l[i] = { x: x, y: y };
		}
		return function(index) {
			return l[index];
		};
	}

	function vertical() {
		return function(index) {
			return { x: 0, y: index };
		}
	}

	function horizontal() {
		return function(index) {
			return { x: index, y: 0 };
		}
	}

	return {
		makeRandomDistributor: randomD,
		makeVerticalDistributor: vertical,
		makeHorizontalDistributor: horizontal,
	}
}();


Point = function(x, y) {
  this.x = x;
  this.y = y;
}
Point.parsePoint = function(str) {
  var re = /^\s*\(\s*(\d+)\s*,\s*(\d+)\s*\)\s*$/
  var result = str.match(re);
  if (result && result[1] && result[2]) {
    return new Point(parseInt(result[1]), parseInt(result[2]));
  }
  else {
    return new Point(0,0);
  }
}
Point.prototype.scaleX = function(scaleX) {
  return new Point(this.x * scaleX, this.y);
}
Point.prototype.scaleY = function(scaleY) {
  return new Point(this.x, this.y * scaleY);
}
Point.prototype.scale = function(scaleX, scaleY) {
  if (scaleY === undefined) {
    scaleY = scaleX;
  }
  return new Point(this.x * scaleX, this.y * scaleY);
}
Point.prototype.offsetX = function(offsetX) {
  return new Point(this.x + offsetX, this.y);
}
Point.prototype.offsetY = function(offsetY) {
  return new Point(this.x, this.y + offsetY);
}
Point.prototype.offset = function(offsetX, offsetY) {
  if (offsetY === undefined) {
    offsetY = offsetX;
  }
  return new Point(this.x + offsetX, this.y + offsetY);
}
Point.prototype.toString = function() {
  return "(" + this.x.toString() + ", " + this.y.toString() + ")";
}