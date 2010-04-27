var previousOnLoad = window.onload;

window.onload = function()
{
	if (previousOnLoad)
		previousOnLoad();

	function determineLastName(fullName) {
		var parts = fullName.replace(" and guest", "").split(" ");
		if (parts[1] == "and")
			return parts.slice(3).join(" ");
		else
			return parts.slice(1).join(" ");
	}


	var name = document.getElementById("name");
	var lastname = document.getElementById("lastname");

	var nameBlurEventHandler = {
		handleEvent: function(evt)
		{
			lastname.value = determineLastName(name.value);
		}
	}

	if (name.addEventListener)
	{
		name.addEventListener("blur", nameBlurEventHandler, false);
	}
	else if (name.attachEvent)
	{
		name.attachEvent("onblur", nameBlurEventHandler.handleEvent);
	}
}
