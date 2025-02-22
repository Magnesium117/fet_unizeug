var url = "http://127.0.0.1:8000/search/";
var lid = null;
var pid = null;
var activeAutocompletion = null;
/*Things I've stolen from https://www.w3schools.com/howto/howto_js_autocomplete.asp*/
function autocomplete(inp, type) {
  /*the autocomplete function takes two arguments,
  the text field element and an array of possible autocompleted values:*/
  var currentFocus;
  /*execute a function when someone writes in the text field:*/
  inp.addEventListener("focus", updateAutocomplete);
  inp.addEventListener("input", updateAutocomplete);
  async function updateAutocomplete() {
    activeAutocompletion = type;
    var a,
      b,
      i,
      apirq,
      iname,
      val = this.value;
    /*close any already open lists of autocompleted values*/
    closeAllLists();
    if (!val && type === "lva") {
      return false;
    }
    if (type === "prof" && lid !== null) {
      apirq =
        url + type + "?searchterm=" + val + "&lid=" + lid + "&searchlim=10";
    } else if (type === "subcat" && lid !== null && pid !== null) {
      apirq =
        url +
        type +
        "?searchterm=" +
        val +
        "&lid=" +
        lid +
        "&pid=" +
        pid +
        "&cat=" +
        document.getElementById("submitform").elements["stype"].value +
        "&searchlim=10";
    } else {
      apirq = url + type + "?searchterm=" + val + "&searchlim=10";
    }
    const response = await fetch(apirq);
    currentFocus = -1;
    /*create a DIV element that will contain the items (values):*/
    a = document.createElement("DIV");
    a.setAttribute("id", this.id + "autocomplete-list");
    a.setAttribute("class", "autocomplete-items");
    /*append the DIV element as a child of the autocomplete container:*/
    this.parentNode.appendChild(a);
    /*for each item in the array...*/
    //await response;
    if (response.ok) {
      arr = await response.json();
    } else {
      console.error("API call failed. Request:\n" + apirq);
      return false;
    }
    for (i = 0; i < arr.length; i++) {
      if (type === "lva") {
        iname =
          arr[i]["lvid"].slice(0, 3) +
          "." +
          arr[i]["lvid"].slice(3, 6) +
          " " +
          arr[i]["lvname"];
      } else {
        iname = arr[i]["name"];
      }
      console.log(iname);
      /*create a DIV element for each matching element:*/
      b = document.createElement("DIV");
      /*make the matching letters bold:*/
      //b.innerHTML = "<strong>" + iname.substr(0, val.length) + "</strong>";
      b.innerHTML = iname; //.substr(val.length);
      /*insert a input field that will hold the current array item's value:*/
      b.innerHTML += "<input type='hidden' value='" + i + "'>";
      /*execute a function when someone clicks on the item value (DIV element):*/
      b.addEventListener("click", function(e) {
        /*insert the value for the autocomplete text field:*/
        if (type === "lva") {
          const idx = this.getElementsByTagName("input")[0].value;
          inp.value =
            arr[idx]["lvid"].slice(0, 3) +
            "." +
            arr[idx]["lvid"].slice(3, 6) +
            " " +
            arr[idx]["lvname"];
          lid = arr[idx]["id"];
        } else if (type === "prof") {
          const idx = this.getElementsByTagName("input")[0].value;
          inp.value = arr[idx]["name"];
          pid = arr[idx]["id"];
        } else {
          inp.value = arr[this.getElementsByTagName("input")[0].value]["name"];
        }
        /*close the list of autocompleted values,
              (or any other open lists of autocompleted values:*/
        closeAllLists();
      });
      a.appendChild(b);
    }
    /*Add Listener to block the main click listener that destroys the autocompletion*/
    inp.addEventListener("click", function(e) {
      e.stopImmediatePropagation();
      if (activeAutocompletion != type) {
        closeAllLists(e.target);
      }
    });
  }
  /*execute a function presses a key on the keyboard:*/
  inp.addEventListener("keydown", function(e) {
    var x = document.getElementById(this.id + "autocomplete-list");
    if (x) x = x.getElementsByTagName("div");
    if (e.keyCode == 40) {
      /*If the arrow DOWN key is pressed,
        increase the currentFocus variable:*/
      currentFocus++;
      /*and and make the current item more visible:*/
      addActive(x);
    } else if (e.keyCode == 38) {
      //up
      /*If the arrow UP key is pressed,
        decrease the currentFocus variable:*/
      currentFocus--;
      /*and and make the current item more visible:*/
      addActive(x);
    } else if (e.keyCode == 13) {
      /*If the ENTER key is pressed, prevent the form from being submitted,*/
      e.preventDefault();
      if (currentFocus > -1) {
        /*and simulate a click on the "active" item:*/
        if (x) x[currentFocus].click();
      }
    }
  });
  function addActive(x) {
    /*a function to classify an item as "active":*/
    if (!x) return false;
    /*start by removing the "active" class on all items:*/
    removeActive(x);
    if (currentFocus >= x.length) currentFocus = 0;
    if (currentFocus < 0) currentFocus = x.length - 1;
    /*add class "autocomplete-active":*/
    x[currentFocus].classList.add("autocomplete-active");
  }
  function removeActive(x) {
    /*a function to remove the "active" class from all autocomplete items:*/
    for (var i = 0; i < x.length; i++) {
      x[i].classList.remove("autocomplete-active");
    }
  }
  function closeAllLists(elmnt) {
    /*close all autocomplete lists in the document,
    except the one passed as an argument:*/
    var x = document.getElementsByClassName("autocomplete-items");
    for (var i = 0; i < x.length; i++) {
      if (elmnt != x[i] && elmnt != inp) {
        x[i].parentNode.removeChild(x[i]);
      }
    }
  }
  /*execute a function when someone clicks in the document:*/
  document.addEventListener("click", function(e) {
    closeAllLists(e.target);
  });
}
function init() {
  autocomplete(document.getElementById("lva"), "lva");
  autocomplete(document.getElementById("prof"), "prof");
  autocomplete(document.getElementById("subcat"), "subcat");
}
window.addEventListener("load", init);
