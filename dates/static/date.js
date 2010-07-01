var examples = document.getElementById('examples');
var text = document.getElementById('text');
var month = document.getElementById('month');
var day = document.getElementById('day');
var year = document.getElementById('year');

function update() {
	var textValue = text.value;
	var monthValue = month.value;
	var dayValue = day.value;
	var yearValue = year.value;

	var monthInt = parseInt(monthValue) - 1;
	var dayInt = parseInt(dayValue);
	var yearInt = parseInt(yearValue);
	if (isNaN(yearInt)) { yearInt = 1900; }
	
	var today = new Date();
	today.setHours(0);
	today.setMinutes(0);
	today.setSeconds(0);
	today.setMilliseconds(0);

	var originalDate = new Date(yearInt, monthInt, dayInt);
	var futureDate = new Date(yearInt, monthInt, dayInt);
	while (futureDate < today) {
		futureDate.setFullYear(futureDate.getFullYear() + 1);
	}

	examples.innerText = textValue;
	while (examples.childNodes[0]) {
		examples.removeChild(examples.childNodes[0]);
	}
	
	var ul = document.createElement("ul");
	ul.setAttribute("class", "examples");

	for (var i = -1; i <= 1; i++) {
		var currentDate = new Date(futureDate.getFullYear(), futureDate.getMonth(), futureDate.getDate());
		currentDate.setFullYear(futureDate.getFullYear() + i);

		dateText = currentDate.getFullYear().toString();
		valueText = textValue;
		if (yearValue == "") {
			valueText += " (?)";
		}
		else {
			var yearDifference = currentDate.getFullYear() - originalDate.getFullYear();
			valueText += " (" + yearDifference + ")";
		}
		var li = makeLi(dateText, valueText);
		ul.appendChild(li);
	}

	examples.appendChild(ul);
}

function makeLi(date, text) {
	var li = document.createElement("li");
	var h3 = document.createElement("h3");
	li.appendChild(h3);
	h3.innerText = date;
	var p = document.createElement("p");
	li.appendChild(p);
	p.innerText = text;

	return li;
}

month.addEventListener('change', update, false);
day.addEventListener('change', update, false);
year.addEventListener('change', update, false);

update();