var db = null;
addEventListener("load", onload, false);
function onload(event) {
  var ul = document.getElementById("dates");
  ul.addEventListener("click", click, false);

  db = openDatabase("Vitamins", "1.0", "Vitamins", 200000);
  db.transaction(function (tx) {
    tx.executeSql("SELECT COUNT(*) FROM Dates", [],
    function (tx, result) {
      var tooOldDate = new Date();
      tooOldDate.setDate(tooOldDate.getDate() - 10);
      tx.executeSql("DELETE FROM Dates WHERE date < ?", [tooOldDate.valueOf()]);
      addDates(ul);
    },
    function (tx, error) {
      tx.executeSql("CREATE TABLE Dates (date REAL UNIQUE, checked INTEGER)", [], function (result) {
        addDates(ul);
      });
    });
  });
}

function click(event) {
  if (!isBox(event.target)) { return; }
  toggleChecked(event.target);
}

function isBox(element) {
  return isInClass(element, "box");
}

function isInClass(element, className) {
  var c = " " + element.className + " ";
  return c.indexOf(" " + className + " ") >= 0;
}

function setChecked(element) {
  if (isInClass(element, "checked")) { return; }
  if (isInClass(element, "unchecked")) {
    element.className = (" " + element.className + " ").replace(" unchecked ", " checked ").trim();
  }
  else {
    element.className = element.className.trim() + " checked";
  }

  updateDb(element, true);
}

function setUnchecked(element) {
  if (isInClass(element, "unchecked")) { return; }
  if (isInClass(element, "checked")) {
    element.className = (" " + element.className + " ").replace(" checked ", " unchecked ").trim();
  }
  else {
    element.className = element.className.trim() + " unchecked";
  }

  updateDb(element, false);
}

function updateDb(element, checked) {
  var d = new Date(parseInt(element.getAttribute("data-date")));

  db.transaction(function (tx) {
    tx.executeSql("UPDATE Dates SET checked = ? WHERE date = ?", [checked ? 1 : 0, d.valueOf()],
      function(tx, result) {
        if (result.rowsAffected == 0) {
          tx.executeSql("INSERT INTO Dates (date, checked) VALUES (?, ?)", [d.valueOf(), checked ? 1 : 0]);
        }
      },
      function(tx, error) {
        tx.executeSql("INSERT INTO Dates (date, checked) VALUES (?, ?)", [d.valueOf(), checked ? 1 : 0]);
      });
  });
}

function toggleChecked(element) {
  if (isInClass(element, "checked")) {
    setUnchecked(element);
  }
  else {
    setChecked(element);
  }
}

function addDates(parent) {
  var now = new Date();
  var currentDay = new Date(now.getFullYear(), now.getMonth(), now.getDate());

  var frag = document.createDocumentFragment();

  for (var i = 0; i < 10; i++) {        
     var li = document.createElement("li");
     var span = document.createElement("span");
     var div = document.createElement("div");
     li.appendChild(span);
     span.appendChild(document.createTextNode(dateToString(currentDay)));
     li.appendChild(div);
     div.className = "box unchecked";
     div.setAttribute("data-date", (currentDay.valueOf()).toString());
     frag.appendChild(li);

     setDivChecked(currentDay.valueOf(), div);

     currentDay.setDate(currentDay.getDate() - 1);
  }

  parent.appendChild(frag);
}

function setDivChecked(value, div) {
  db.transaction(function (tx) {
    tx.executeSql("SELECT * FROM Dates WHERE date = ?", [value], function(tx, result) {
      var isChecked = result.rows.length == 1 && result.rows.item(0)['checked'];
      if (isChecked) {
        div.className = "box checked";
      }
    });
  });
}

function dateToString(date) {
  var today = new Date();
  today = new Date(today.getFullYear(), today.getMonth(), today.getDate());
  if (date.valueOf() == today.valueOf()) {
    return "Today";
  }
  today.setDate(today.getDate() - 1);
  if (date.valueOf() == today.valueOf()) {
    return "Yesterday";
  }

  var days = ["Sunday", "Monday", "Tuesday", "Wednesday", "Thursday", "Friday", "Saturday"];
  var months = ["January", "February", "March", "April", "May", "June", "July", "August", "September", "October", "November", "December"];
  var s = "";
  s += days[date.getDay()];
  s += ", ";
  s += months[date.getMonth()];
  s += " ";
  s += date.getDate().toString();
  return s;
}