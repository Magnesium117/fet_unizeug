//const c = document.getElementById("pdf_canvas");
//const pdf_url = "./VO_Mathematik_3.pdf";
//import * as pdfjsLib from "./pdf.mjs";
//pdfjsLib.GlobalWorkerOptions.workerSrc = './pdf.worker.mjs';
//pdfjsLib.getDocument(pdfUrl).promise.then(function(pdfDoc) {
//  // Continue with further steps.
//});
//pdfDoc.getPage(1).then(function(page) {
//  // Continue with further steps.
//});
//const viewport = page.getViewport({ scale: 1 });
//canvas.width = viewport.width;
//canvas.height = viewport.height;
//const ctx = canvas.getContext('2d');
//const renderContext = {
//  canvasContext: ctx,
//  viewport: viewport,
//};
//
//page.render(renderContext);
//pdfjsLib
//  .getDocument(pdfUrl)
//  .promise.then(function(pdfDoc) {
//    // Handling and rendering logic.
//  })
//  .catch(function(error) {
//    console.log('Error loading PDF file:', error);
//  });
//var ctx = c.getContext("2d");
//ctx.moveTo(0, 0);
//ctx.lineTo(10000, 10000);
//ctx.stroke();
//import pdfjsLib from 'https://cdn.jsdelivr.net/npm/pdfjs-dist@4.9.155/+esm'
const PDFStart = nameRoute => {
}
const startPdf = () => {
  PDFStart('./VO_Mathematik_3.pdf')
}
window.addEventListener('load', startPdf);
let loadingTask = pdfjsLib.getDocument(nameRoute),
  pdfDoc = null,
  canvas = document.querySelector('#cnv'),
  ctx = canvas.getContext('2d'),
  scale = 1.5,
  numPage = 1;
loadingTask.promise.then(pdfDoc_ => { pdfDoc = pdfDoc_; document.querySelector('#npages').innerHTML = pdfDoc.numPages; GeneratePDF(numPage) });
const GeneratePDF = numPage => { pdfDoc.getPage(numPage).then(page => { let viewport = page.getViewport({ scale: scale }); canvas.height = viewport.height; canvas.width = viewport.width; let renderContext = { canvasContext: ctx, viewport: viewport }page.render(renderContext); })document.querySelector('#npages').innerHTML = numPage; };
