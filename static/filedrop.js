var fileinput;
function dropHandler(eve) {
  eve.preventDefault();
  fileinput.files = eve.dataTransfer.files;
}
function init() {
  fileinput = document.getElementById("filepicker");
  document.getElementById("filepicker").addEventListener("drop", dropHandler);
}
window.addEventListener("load", init);
