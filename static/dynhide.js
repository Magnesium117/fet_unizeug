var radiobuttons;
var datediv;
var subcatdiv;
var rdbarr;
var subcatcategories = [1, 2, 3];
var datecategorires = [0, 1];
function changevis() {
  for (let i = 0; i < rdbarr.length; i++) {
    if (rdbarr[i].checked) {
      if (subcatcategories.includes(i)) {
        subcatdiv.style.display = "block";
      } else {
        subcatdiv.style.display = "none";
      }
      if (datecategorires.includes(i)) {
        datediv.style.display = "block";
      } else {
        datediv.style.display = "none";
      }
      return;
    }
  }
}
function starthide() {
  radiobuttons = document.getElementsByName("stype");
  datediv = document.getElementById("datediv");
  subcatdiv = document.getElementById("subcatdiv");
  rdbarr = [
    document.getElementById("pruefung"),
    document.getElementById("klausur"),
    document.getElementById("uebung"),
    document.getElementById("labor"),
    document.getElementById("unterlagen"),
    document.getElementById("zusammenfassungen"),
    document.getElementById("multimedia"),
  ];
  changevis();
  radiobuttons.forEach((rdb) => {
    rdb.addEventListener("change", changevis);
  });
}
window.addEventListener("load", starthide);
