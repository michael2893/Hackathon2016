var music = document.getElementById('music'); 
var duration; // Duration of audio clip
var pButton = document.getElementById('pButton'); 

var playhead = document.getElementById('playhead');

var timeline = document.getElementById('timeline'); 
var timelineWidth = timeline.offsetWidth - playhead.offsetWidth;


music.addEventListener("timeupdate", timeUpdate, false);


timeline.addEventListener("click", function (event) {
	moveplayhead(event);
	music.currentTime = duration * clickPercent(event);
}, false);


function clickPercent(e) {
	return (e.pageX - timeline.offsetLeft) / timelineWidth;
}


playhead.addEventListener('mousedown', mouseDown, false);
window.addEventListener('mouseup', mouseUp, false);


var onplayhead = false;

function mouseDown() {
	onplayhead = true;
	window.addEventListener('mousemove', moveplayhead, true);
	music.removeEventListener('timeupdate', timeUpdate, false);
}

function mouseUp(e) {
	if (onplayhead == true) {
		moveplayhead(e);
		window.removeEventListener('mousemove', moveplayhead, true);
		
		music.currentTime = duration * clickPercent(e);
		music.addEventListener('timeupdate', timeUpdate, false);
	}
	onplayhead = false;
}

function moveplayhead(e) {
	var newMargLeft = e.pageX - timeline.offsetLeft;
	if (newMargLeft >= 0 && newMargLeft <= timelineWidth) {
		playhead.style.marginLeft = newMargLeft + "px";
	}
	if (newMargLeft < 0) {
		playhead.style.marginLeft = "0px";
	}
	if (newMargLeft > timelineWidth) {
		playhead.style.marginLeft = timelineWidth + "px";
	}
}


function timeUpdate() {
	var playPercent = timelineWidth * (music.currentTime / duration);
	playhead.style.marginLeft = playPercent + "px";
	if (music.currentTime == duration) {
		pButton.className = "";
		pButton.className = "play";
	}
}

function play() {

	if (music.paused) {
		music.play();
	
		pButton.className = "";
		pButton.className = "pause";
	} else { // pause music
		music.pause();
		
		pButton.className = "";
		pButton.className = "play";
	}
}


music.addEventListener("canplaythrough", function () {
	duration = music.duration;  
}, 
false);


