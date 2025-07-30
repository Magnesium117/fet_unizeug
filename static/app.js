class PDFView {
  constructor(nameRoute) {
    this.loadingTask = pdfjsLib.getDocument(nameRoute);
    this.pdfDoc = null;
    this.canvas = document.querySelector("#cnv");
    this.ctx = this.canvas.getContext("2d");
    this.scale = 1.5;
    this.numPage = 1;
    this.maxheight =
      window.innerHeight -
      document.getElementById("buttonsdiv").getBoundingClientRect().height;
    this.maxwidth = document
      .getElementById("cnvdiv")
      .getBoundingClientRect().width;
    this.rendering = false;
    this.loadingTask.promise.then((pdfDoc_) => {
      this.pdfDoc = pdfDoc_;
      document.querySelector("#npages").innerHTML = this.pdfDoc.numPages;
      this.GeneratePDF();
    });
  }
  GeneratePDF() {
    this.rendering = true;
    this.pdfDoc.getPage(this.numPage).then((page) => {
      let unscaled = page.getViewport({ scale: 1.0 });
      this.scale = Math.min(
        this.maxheight / unscaled.height,
        this.maxwidth / unscaled.width,
      );
    });
    this.pdfDoc.getPage(this.numPage).then((page) => {
      let viewport = page.getViewport({ scale: this.scale });
      this.canvas.height = viewport.height;
      this.canvas.width = viewport.width;

      let renderContext = {
        canvasContext: this.ctx,
        viewport: viewport,
      };
      doc.cnv.width = this.canvas.width;
      doc.cnv.height = this.canvas.height;
      document.getElementById("rightdiv").style.width =
        ((doc.cnv.width / screen.width) * 100).toString() + "vw";
      document.getElementById("controldiv").style.width =
        ((1 - doc.cnv.width / screen.width) * 100).toString() + "vw";
      doc.pagescales[this.numPage] = {
        scale: this.scale,
        width: doc.cnv.width,
        height: doc.cnv.height,
      };

      var renderTask = page.render(renderContext);
      renderTask.promise.then(() => {
        doc.drawRects();
        this.rendering = false;
      });
    });
    document.querySelector("#npage").innerHTML = this.numPage;
  }

  WaitToRender() {
    if (this.rendering) {
      window.setTimeout(this.WaitToRender.bind(this), 100);
    } else {
      this.GeneratePDF();
    }
  }

  PrevPage() {
    if (this.numPage === 1) {
      return;
    }
    this.numPage--;
    this.WaitToRender();
  }

  NextPage() {
    if (this.numPage >= this.pdfDoc.numPages) {
      return;
    }
    this.numPage++;
    this.WaitToRender();
  }
  RenderPage() {
    this.WaitToRender();
  }
}
class Rectangle {
  constructor(canvas, sx, sy, ex, ey, color, alpha = 1) {
    this.x = sx < ex ? sx : ex;
    this.y = sy < ey ? sy : ey;
    this.width = Math.abs(ex - sx);
    this.height = Math.abs(ey - sy);
    this.color = color;
    this.context = canvas.getContext("2d");
    this.alpha = alpha;
  }
  draw() {
    this.context.globalAlpha = this.alpha;
    this.context.beginPath();
    this.context.rect(this.x, this.y, this.width, this.height);
    this.context.fillStyle = this.color;
    this.context.strokeStyle = "black";
    this.context.lineWidth = 1;

    this.context.fill();
    this.context.stroke();
  }
  makeTuple() {
    return [this.x, this.y, this.width, this.height];
  }
}
class PDFDocument {
  constructor(filename, fileID, filetype) {
    if (filetype === "pdf") {
      this.pdf = new PDFView(filename);
    } else {
      this.pdf = new PDFView("/files/unsupported");
    }
    this.filetype = filetype;
    this.fname = filename;
    this.fID = fileID;
    this.rects = [];
    this.cnv = document.querySelector("#drw_cnv");
    this.ctx = this.cnv.getContext("2d");
    this.temprect = new Rectangle(this.cnv, 0, 0, 0, 0, "white", 0);
    this.pagescales = [];
    this.startX = 0;
    this.startY = 0;
  }
  drawAll() {
    //context = cnv.getContext("2d");
    this.ctx.clearRect(0, 0, this.cnv.width, this.cnv.height);
    //pdf.RenderPage();
    this.drawRects();
  }
  drawRects() {
    if (!(this.pdf.numPage in this.rects)) {
      this.rects[this.pdf.numPage] = [];
    }
    this.temprect.draw();
    for (var i = 0; i < this.rects[this.pdf.numPage].length; i++) {
      var shape = this.rects[this.pdf.numPage][i];
      shape.draw();
    }
  }
  addRect(endpos) {
    var re = new Rectangle(
      this.cnv,
      this.startX,
      this.startY,
      endpos.x,
      endpos.y,
      "black",
    );
    this.rects[this.pdf.numPage].push(re);
    this.drawAll();
  }
  clearCnv() {
    this.rects[this.pdf.numPage] = [];
    //context = cnv.getContext("2d");
    this.ctx.clearRect(0, 0, this.cnv.width, this.cnv.height);
    //pdf.RenderPage();
    this.temprect = new Rectangle(this.cnv, 0, 0, 0, 0, "black", 0);
  }
  clearAll() {
    this.rects = [];
    this.clearCnv();
  }
  get paramRects() {
    let prects = [];
    for (var k = 1; k < this.rects.length; k++) {
      prects[k - 1] = [];
      //console.log(this.rects[k]);
      if (this.rects[k] === undefined) {
        continue;
      }
      //console.log(this.rects[k].length);
      //console.log(0 < this.rects[k].length);
      let len = this.rects[k].length;
      for (var i = 0; i < len; i++) {
        //console.log(this.rects[k][i]);
        prects[k - 1].push(this.rects[k][i].makeTuple());
        //console.log(prects[k][i]);
      }
    }
    return prects;
  }
}
var mouseIsDown = false;
//var startX = 0;
//var startY = 0;
//var pdf;
//var cnv = document.querySelector("#drw_cnv");
//var ctx = cnv.getContext("2d");
//var rects = {};
//var temprect = new Rectangle(cnv, 0, 0, 0, 0, "white", 0);
//var pagescales = {};

function getMousePos(cnv, eve) {
  var rect = cnv.getBoundingClientRect();
  return {
    x: eve.clientX - rect.left,
    y: eve.clientY - rect.top,
  };
}
function mouseDown(eve) {
  //console.log(eve);
  if (eve.buttons != 1) {
    return;
  }
  if (mouseIsDown) {
    return;
  }
  mouseIsDown = true;
  var pos = getMousePos(cnv, eve);
  doc.startX = pos.x;
  doc.startY = pos.y;
}
function mouseUp(eve) {
  //console.log(eve);
  if (eve.buttons != 0) {
    return;
  }
  if (!mouseIsDown) {
    return;
  }
  mouseIsDown = false;
  doc.addRect(getMousePos(cnv, eve));
  doc.temprect = new Rectangle(doc.cnv, 0, 0, 0, 0, "black", 0);
}

//var mousexy = 0;
function mouSexy(eve) {
  if (mouseIsDown) {
    var pos = getMousePos(doc.cnv, eve);
    doc.temprect = new Rectangle(
      doc.cnv,
      doc.startX,
      doc.startY,
      pos.x,
      pos.y,
      "black",
      0.5,
    );
    doc.drawAll();
  }
}
function scrollPage(eve) {
  console.log(eve);
  if (eve.ctrlKey) {
    return;
  }
  if (eve.deltaY > 0) {
    doc.pdf.NextPage();
  } else {
    doc.pdf.PrevPage();
  }
}
const initDraw = () => {
  var cnv = document.querySelector("#drw_cnv");
  cnv.addEventListener("mousedown", mouseDown, false);
  cnv.addEventListener("mouseup", mouseUp, false);
  cnv.addEventListener("mousemove", mouSexy, false);
  cnv.addEventListener("wheel", scrollPage, false);
};
function submitPdf(eve) {
  eve.preventDefault();
  var formdata = new FormData(eve.target);
  console.log(doc.paramRects);
  formdata.append("rects", JSON.stringify(doc.paramRects));
  formdata.append("pagescales", JSON.stringify(doc.pagescales.slice(1)));
  formdata.append("fileId", doc.fID);
  //formdata.append("filename", doc.filename);
  formdata.append("ftype", doc.filetype);
  if (!formdata.has("censor")) {
    formdata.append("censor", "False");
  }
  console.log(formdata);
  submitForm(formdata);
}
async function submitForm(formData) {
  try {
    const response = await fetch("http://127.0.0.1:8000/submit", {
      method: "POST",
      body: formData,
    });
    //let responseJSON=await response.json();
    if (response.ok) {
      console.log("Submit OK");
      // console.log(response);
      // window.open(response);
      // console.log(URL.createObjectURL(response.body));
      // window.open(response);
      // window.open(response, (target = "_blank"));
      // var newWindow = window.open();
      // newWindow.document.write(response);
      // var blob = response.blob();
      const blobURL = URL.createObjectURL(await response.blob());
      window.open(blobURL, "_blank");
    } else {
      console.log("Submit failed");
    }
  } catch (error) {
    console.error("Error" + error);
  }
}
function uploadPdf(eve) {
  eve.preventDefault();
  const fileupload = document.querySelector("#filepicker");
  const file = fileupload.files;
  if (!file) {
    alert("Please Choose a file");
    return;
  }
  const form = document.querySelector("#uploadform");
  const formData = new FormData(form);
  //formData.append("files", file);
  uploadFile(formData);
}
async function uploadFile(formData) {
  try {
    const response = await fetch("http://127.0.0.1:8000/uploadfile", {
      method: "POST",
      body: formData,
    });
    let responseJSON = await response.json();

    if (response.ok) {
      console.log("upload OK " + responseJSON["filename"]);
      console.log(response);
      delete doc.pdf;
      //delete doc;
      document.getElementById("name").value = responseJSON.filename;
      doc = new PDFDocument(
        responseJSON.path,
        responseJSON.fid,
        responseJSON.filetype,
      );
    } else {
      console.log("upload failed");
    }
  } catch (error) {
    console.error("Error: " + error);
  }
}

function initUpload() {
  document.querySelector("#uploadform").addEventListener("submit", uploadPdf);
  document.querySelector("#submitform").addEventListener("submit", submitPdf);
}
function initListeners() {
  document.querySelector("#prev").addEventListener("click", function() {
    doc.pdf.PrevPage();
  });
  document.querySelector("#next").addEventListener("click", function() {
    doc.pdf.NextPage();
  });
  document.querySelector("#clr").addEventListener("click", function() {
    doc.clearCnv();
  });
  document.querySelector("#ca").addEventListener("click", function() {
    doc.clearAll();
  });
}
const startPdf = () => {
  // doc = new PDFDocument(
  //   "./files/b78c869f-e0bb-11ef-9b58-84144d05d665",
  //   "b78c869f-e0bb-11ef-9b58-84144d05d665",
  //   "pdf",
  // );
  //pdf = new PDFView("./VO_Mathematik_3.pdf");
  doc = new PDFDocument("./files/greeting", "greeting", "pdf");
  initDraw();
  initUpload();
  initListeners();
};

window.addEventListener("load", startPdf);
