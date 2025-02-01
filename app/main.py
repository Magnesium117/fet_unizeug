from typing import Annotated
from typing import List, Dict, Tuple
from fastapi import FastAPI, File, HTTPException, UploadFile, Request, Form
from fastapi.responses import FileResponse

# import fastapi
from fastapi.staticfiles import StaticFiles
import pymupdf
import json

# import os
import mariadb

app = FastAPI()

app.mount("/favicon", StaticFiles(directory="./favicon"), name="favicon")
app.mount("/static", StaticFiles(directory="./static"), name="static")
db = mariadb.connect(
    host="localhost", user="wildserver", password="DBPassword", database="Unizeug"
)


# cur = db.cursor()
# cur.execute("select * from FIP;")
# for l in cur:
#     print(l)
# locpaths = ["./VO_Mathematik_3.pdf"]  # replace this with a database
@app.get("/")
async def get_index():
    return FileResponse("./index.html")


@app.get("/files/{file_id}")
async def get_file(file_id: str):
    cur = db.cursor()
    try:
        cur.execute("Select filename from FIP where id=?", (file_id,))
    except mariadb.Error as e:
        print(f"Mariadb Error: {e}")
        raise HTTPException(
            status_code=500, detail="Somethings wrong with the database"
        )
    filename = cur.fetchone()[0]
    return FileResponse(f"./app/files/{filename}")


# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     return {"filesize": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    content = await file.read()
    filename = file.filename if file.filename is not None else "None"
    locpath = "./app/files/" + filename
    # locpaths.append(locpath)
    cur = db.cursor()
    try:
        cur.execute("Insert Into FIP (filename) Values(?)", (filename,))
    except mariadb.Error as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Somethings wrong with the database"
        )
    try:
        cur.execute("Select id From FIP where filename=?", (filename,))
    except mariadb.Error as e:
        print(f"Error: {e}")
        raise HTTPException(
            status_code=500, detail="Somethings wrong with the database"
        )
    id = cur.fetchone()[0]
    with open(locpath, "wb") as f:
        f.write(content)
    # app.mount("/files", StaticFiles(directory="./app/files/"), name="files")
    db.commit()
    return {
        "filename": filename,
        "path": "/files/" + id,
        "fid": id,
    }


@app.post("/submit/")
async def get_submittion(
    lva: Annotated[str, Form()],  # LVA Name and Number
    prof: Annotated[str, Form()],  # Vortragender
    fname: Annotated[str, Form()],  # Path to pdf File
    fileId: Annotated[str, Form()],
    sem: Annotated[str, Form()],  # Semester eg. 2024W
    stype: Annotated[str, Form()],  # Type of File eg. Prüfung
    ex_date: Annotated[str, Form()],  # Date of Exam only when type is exam
    rects: Annotated[
        str, Form()
    ],  # Rechtangles # List[List[Tuple[float, float, float, float]]],
    pagescales: Annotated[
        str, Form()
    ],  # Scales of Pages  # Annotated[List[Dict[str, float]], Form()],
):
    print(lva, prof, fname, stype, sem, ex_date, rects, pagescales)
    rects_p = json.loads(rects)
    scales_p = json.loads(pagescales)
    cur = db.cursor()
    try:
        cur.execute("Select filename from FIP where id=?", (fileId,))
    except mariadb.Error as e:
        print(f"Mariadb Error: {e}")
        raise HTTPException(
            status_code=500, detail="Somethings wrong with the database"
        )
    filepath = "./app/files/" + cur.fetchone()[0]
    censor_pdf(filepath, "./app/files/censored.pdf", rects_p, scales_p)
    return {"done": "ok"}


def censor_pdf(
    path: str,
    destpath: str,
    rects: List[List[List[float]]],
    scales: List[Dict[str, float]],
):
    doc = pymupdf.open(path)
    output = pymupdf.open()
    page = doc[0]
    width = page.rect.width
    height = page.rect.height
    print(width, height)
    for i in range(doc.page_count):
        page = doc[i]
        if i < len(rects):
            wfac = page.rect.width / scales[i]["width"]
            hfac = page.rect.height / scales[i]["height"]
            for rect in rects[i]:
                prect = pymupdf.Rect(
                    rect[0] * wfac,
                    rect[1] * hfac,
                    (rect[0] + rect[2]) * wfac,
                    (rect[1] + rect[3]) * hfac,
                )
                page.draw_rect(
                    prect,
                    color=(0, 0, 0),
                    fill=(0, 0, 0),
                )
        bitmap = page.get_pixmap()
        pdf_bytes = bitmap.pdfocr_tobytes(
            language="deu",
            tessdata="/usr/share/tessdata/",  # tesseract needs to be installed; this is the path to thetesseract files
        )
        output.insert_pdf(pymupdf.Document(stream=pdf_bytes))
    output.save(destpath)
    print("CENSORING DONE")


# async def get_submittion(request: Request):
#     reqJson = await request.form()
#     print(reqJson)
#     return {"done": "ok"}
