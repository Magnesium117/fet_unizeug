from typing import Annotated
from typing import List, Dict, Tuple
from annotated_types import IsDigit
from fastapi import FastAPI, File, HTTPException, UploadFile, Request, Form
from fastapi.responses import FileResponse

# import fastapi
from fastapi.staticfiles import StaticFiles
import pymupdf
import json
import re


import os
import mariadb

import filetype

import datetime


app = FastAPI()

app.mount("/favicon", StaticFiles(directory="./favicon"), name="favicon")
app.mount("/static", StaticFiles(directory="./static"), name="static")
db = mariadb.connect(
    host="localhost", user="wildserver", password="DBPassword", database="Unizeug"
)
CATEGORIES = [
    "Prüfungen",
    "Klausuren",
    "Übungen",
    "Labore",
    "Unterlagen",
    "Zusammenfassungen",
    "Multimedia",
]
SUBCAT_CATEGORIES = ["Klausuren", "Übungen", "Labore"]
SUBCAT_CATEGORIES_I = [1, 2, 3]
EX_DATE_CATEGORIES = ["Prüfungen", "Klausuren"]
EX_DATE_CATEGORIES_I = [0, 1]
UNIZEUG_PATH = "./app/dest/"
FILES_IN_PROGRESS = "./app/files/"


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
    if file_id == "unsupported":
        return FileResponse(FILES_IN_PROGRESS + "unsupported.pdf")
    if file_id == "empty":
        return FileResponse(FILES_IN_PROGRESS + "empty.pdf")
    cur = db.cursor()
    try:
        cur.execute("Select filename from FIP where id=?", (file_id,))
    except mariadb.Error as e:
        print(f"Mariadb Error: {e}")
        raise HTTPException(
            status_code=500, detail="Somethings wrong with the database"
        )
    filename = cur.fetchone()[0]
    return FileResponse(FILES_IN_PROGRESS + filename)


@app.get("/search/lva")
async def search_lva(
    searchterm: str, searchlim: int = 10
) -> List[Dict[str, int | str]]:
    res = []
    cur = db.cursor(dictionary=True)
    if await is_LVID(searchterm):
        cur.execute(
            "SELECT lvid,lvname FROM LVAs WHERE lvid LIKE ?", (searchterm + "%",)
        )
        res = cur.fetchall()
    else:
        cur.execute(
            "SELECT id,lvid,lvname FROM LVAs WHERE lvname LIKE ?",
            (searchterm + "%",),
        )
        res = cur.fetchall()
        cur.execute(
            "SELECT id,lvid,lvname FROM LVAs WHERE lvname LIKE ?",
            ("%" + searchterm + "%",),
        )
        res = remove_duplicates(res + cur.fetchall())
    if searchlim == 0:
        return res
    else:
        return res[:searchlim]


@app.get("/search/prof")
async def search_profs(
    searchterm: str = "", lid: int | None = None, searchlim: int = 10
) -> List[Dict[str, str | int]]:
    res = []
    zw = []
    cur = db.cursor(dictionary=True)
    if lid is not None:
        # cur.execute("SELECT id FROM LVAs WHERE LVId=?", (lvid,))
        # lid = cur.fetchall()[0]["id"]
        cur.execute(
            "SELECT Profs.id,Profs.name FROM Profs LEFT JOIN LPLink ON Profs.id=LPLink.pid WHERE name like ? AND lid=?",
            ("%" + searchterm + "%", lid),
        )
        res = cur.fetchall()
        cur.execute(
            "SELECT Profs.id,Profs.name FROM Profs LEFT JOIN LPLink ON Profs.id=LPLink.pid WHERE name NOT like ? AND lid=?",
            ("%" + searchterm + "%", lid),
        )
        zw = cur.fetchall()
    if searchterm != "":
        cur.execute(
            "SELECT id,name FROM Profs WHERE name LIKE ?", ("%" + searchterm + "%",)
        )
        res += cur.fetchall()
    res = remove_duplicates(res + zw)
    if searchlim == 0:
        return res
    else:
        return res[:searchlim]


@app.get(
    "/search/subcat"
)  # NOT FULLY TESTED DUE TO INCOMPLETE DATABASE DUE TO INACCEPTABLE FOLDERSTRUCTURE
async def search_subcats(
    searchterm: str = "",
    lid: int | None = None,
    pid: int | None = None,
    cat: int | None = None,
    searchlim: int = 10,
) -> List[Dict[str, str | int]]:
    res = []
    rest = []
    cur = db.cursor(dictionary=True)
    if not (lid is None or pid is None or cat is None):  # Rest is available
        # cur.execute("SELECT id FROM LVAs WHERE LVId=?", (lvid,))
        # lid = cur.fetchall()[0]["id"]
        cur.execute(
            "SELECT id,name FROM SubCats WHERE lid=? AND pid=? AND cat=?",
            (lid, pid, cat),
        )
        rest = cur.fetchall()
    if searchterm != "":  # searchterm is available
        if not (lid is None or pid is None or cat is None):
            cur.execute(
                "SELECT id,name FROM SubCats WHERE lid=? AND pid=? AND cat=? AND name LIKE ?",
                (lid, pid, cat, "%" + searchterm + "%"),
            )
            res = cur.fetchall()
        cur.execute(
            "SELECT id,name FROM SubCats WHERE name LIKE ?", ("%" + searchterm + "%",)
        )
        res += cur.fetchall()
    res = remove_duplicates(res + rest)
    if searchlim == 0:
        return res
    else:
        return res[:searchlim]


# @app.post("/files/")
# async def create_file(file: Annotated[bytes, File()]):
#     return {"filesize": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(files: List[UploadFile], c2pdf: bool = True):
    if len(files) == 0:
        raise HTTPException(status_code=400, detail="No files found in file submission")
    filename = files[0].filename if files[0].filename is not None else "None"
    if len(files) == 1:
        content = await files[0].read()
        ft = filetype.guess(content).extension
        if c2pdf and ft != "pdf":
            ret = convert_to_pdf(content)
            if ret is not None:
                content = ret
                filename = filename_to_pdf(filename)
                ft = "pdf"
    else:
        filecontents = []
        for file in files:
            content = await file.read()
            ft = filetype.guess(content).extension
            if ft == "pdf":
                filecontents.append(content)
                continue
            if c2pdf:
                res = convert_to_pdf(content)
                if res is None:
                    filename = await save_files_to_folder(files)
                    content = None
                    ft = "dir"
                    break
                filecontents.append(res)
            else:
                filename = await save_files_to_folder(files)
                content = None
                ft = "dir"
                break
        else:  # is executed when the loop was not broken out of
            filename = filename_to_pdf(filename)
            ft = "pdf"
            doc = pymupdf.open()
            for content in filecontents:
                doc.insert_pdf(pymupdf.open("pdf", content))
            content = doc.tobytes()
    if ft != "dir":
        filename = make_filename_unique(filename)
    locpath = FILES_IN_PROGRESS + filename
    # locpaths.append(locpath)
    cur = db.cursor()
    try:
        cur.execute(
            "Insert Into FIP (filename,filetype,initTimeStamp) Values(?,?,?)",
            (filename, ft, str(datetime.datetime.now())),
        )
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
    if content is not None:
        with open(locpath, "wb") as f:
            f.write(content)
    # app.mount("/files", StaticFiles(directory="./app/files/"), name="files")
    db.commit()
    fname = "".join(filename.split(".")[0:-1])
    # ftype = filename.split(".")[-1]
    return {
        "filename": fname,
        "filetype": ft,
        "path": "/files/" + id,
        "fid": id,
    }


@app.post("/submit/")
async def get_submission(
    lva: Annotated[str, Form()],  # LVA Name and Number
    prof: Annotated[str, Form()],  # Vortragender
    fname: Annotated[str, Form()],  # Path to pdf File
    fileId: Annotated[str, Form()],  # UUID of file in FIP table
    sem: Annotated[str, Form()],  # Semester eg. 2024W
    stype: Annotated[str, Form()],  # Type of File eg. Prüfung=>0
    subcat: Annotated[str, Form()],  # Subcategory of file if the category has subcats
    ex_date: Annotated[
        str, Form()
    ],  # Date of Exam only when type is exam(Klausur/Prüfung)
    ftype: Annotated[str, Form()],  # type of File
    rects: Annotated[
        str, Form()
    ],  # Rechtangles # List[List[Tuple[float, float, float, float]]],
    pagescales: Annotated[
        str, Form()
    ],  # Scales of Pages  # Annotated[List[Dict[str, float]], Form()],
):
    print(lva, prof, fname, stype, subcat, sem, ex_date, rects, pagescales)
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
    try:
        dest = make_savepath(lva, prof, stype, subcat, sem, ex_date, fname, ftype)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    censor_pdf(filepath, dest, rects_p, scales_p)
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
        bitmap = page.get_pixmap(dpi=300)
        pdf_bytes = bitmap.pdfocr_tobytes(
            language="deu",
            tessdata="/usr/share/tessdata/",  # tesseract needs to be installed; this is the path to thetesseract files
        )
        output.insert_pdf(pymupdf.Document(stream=pdf_bytes))
    output.save(destpath)
    print("CENSORING DONE")


async def is_LVID(term: str) -> bool:
    if re.match(r"[a-zA-Z0-9]{3}\.[a-zA-Z0-9]*", term):
        return True
    if term.isdigit():
        return True
    return False


def remove_duplicates(
    results: List[Dict[str, str | int]],
) -> List[Dict[str, str | int]]:
    ids = []
    res = []
    for result in results:
        if result["id"] in ids:
            continue
        ids.append(result["id"])
        res.append(result)
    return res


def make_savepath(
    lva: str,
    prof: str,
    cat: str,
    subcat: str,
    sem: str,
    ex_date: str,
    fname: str,
    ftype: str,
) -> str:
    """Generates the path, the file is saved to after the upload process is finished. It creates all nessecery directories."""
    lv = get_lvpath(lva)
    lvpath = lv[1] + "/"
    pf = get_profpath(prof, lv[0])
    pfpath = pf[1] + "/"
    catpath = CATEGORIES[int(cat)] + "/"
    scpath = ""
    if int(cat) in SUBCAT_CATEGORIES_I and subcat != "":
        sc = get_subcatpath(subcat, int(cat), pf[0], lv[0])
        scpath = sc[1] + "/"
    if int(cat) == 6:
        savepath = UNIZEUG_PATH + lv[1] + "_Multimedia_only/" + pfpath
    else:
        savepath = UNIZEUG_PATH + lvpath + pfpath + catpath + scpath
    os.makedirs(savepath, exist_ok=True)
    filename = sem + "_"
    if int(cat) in EX_DATE_CATEGORIES_I:
        _, mm, dd = ex_date.split("-")
        filename += mm + "_" + dd + "_"
    filename += fname + "." + ftype
    return savepath + filename


def get_lvpath(lva: str) -> Tuple[int, str]:
    """returns the path in UNIZEUG from a LVA based on its LVID (or name) that may be within a string. It uses the path within the database. If there is no Entry with a fitting LVID in the database it creates a new LVA. Returns: (id,path)"""
    cur = db.cursor()
    lvid = re.search(r"[a-zA-Z0-9]{3}\.[a-zA-Z0-9]{3}", lva)
    if lvid is not None:
        cur.execute(
            "SELECT id,lvpath FROM LVAs WHERE lvid=?",
            (lvid.group()[:3] + lvid.group()[4:],),
        )
        res = cur.fetchone()
        if res is not None:
            return res
        else:
            return makenew(lva, "LVAs")
    else:
        cur.execute("SELECT id,lvpath FROM LVAs WHERE lvname=?", (lva,))
        res = cur.fetchone()
        if res is not None:
            return res
        else:
            return makenew(lva, "LVAs")


def get_profpath(prof: str, lid: int) -> Tuple[int, str]:
    """Generates the foldername for a prof based on his name. It searches the database for matches. Returns: (id,name)"""
    cur = db.cursor()
    prof = prof.replace("_", " ")
    cur.execute("SELECT id,name FROM Profs WHERE name=?", (prof,))
    res = cur.fetchall()
    print(res != [])
    if res is not None and res != []:
        ret = (res[0][0], res[0][1].replace(" ", "_"))
        cur.execute("SELECT * FROM LPLink WHERE LId=? AND PId=?", (lid, ret[0]))
        if cur.fetchall() is None:
            linkLP(lid, ret[0])
        return ret
    fname, lname = prof.split(" ")
    cur.execute("SELECT id,name FROM Profs WHERE name like ?", (lname + " " + fname,))
    res = cur.fetchall()
    if res is not None and res != []:
        ret = (res[0][0], res[0][1].replace(" ", "_"))
        cur.execute("SELECT * FROM LPLink WHERE LId=? AND PId=?", (lid, ret[0]))
        if cur.fetchall() is None:
            linkLP(lid, ret[0])
        return ret
    ret = makenew(prof, "Profs")
    linkLP(lid, ret[0])
    return ret


def get_subcatpath(subcat: str, cat: int, pid: int, lid: int) -> Tuple[int, str]:
    """Generates the subcat path from a subcat name. Returns: (id,name)"""
    cur = db.cursor()
    cur.execute(
        "SELECT id,name FROM SubCats WHERE LId=? AND PId=? AND cat=? AND name=?",
        (lid, pid, cat, subcat),
    )
    res = cur.fetchone()
    if res is None:
        return makenew(subcat, "SubCats", LId=lid, PId=pid, cat=cat)
    return res


def makenew(input: str, table: str, **kwargs) -> Tuple[int, str]:
    """Generates new Entrys in the database for LVAs, Profs, SUBCATS. Returns: (id,name/path)"""
    cur = db.cursor()
    if table == "LVAs":
        lvaid = re.search(r"[a-zA-Z0-9]{3}\.[a-zA-Z0-9]{3}", input)
        if lvaid is None:
            raise ValueError("LVA needs to have a LVA ID to be inserted into the table")
        lvid = lvaid.group()[:3] + lvaid.group()[4:]
        lvname = re.sub(r"[_ -]*[a-zA-Z0-9]{3}\.[a-zA-Z0-9]{3}[_ -]*", "", input)
        lvpath = lvname + "_" + lvaid.group()
        cur.execute(
            "INSERT INTO LVAs(lvid,lvname,lvpath) VALUES(?,?,?)", (lvid, lvname, lvpath)
        )
        cur.execute("SELECT id,lvpath FROM LVAs WHERE lvid=?", (lvid,))
        db.commit()
        return cur.fetchone()
    querry = "INSERT INTO " + table + "(name"
    values = [input]
    nvals = 0
    for k, v in kwargs.items():
        values.append(v)
        querry += "," + k
        nvals += 1
    querry += ") VALUES(?" + nvals * ",?" + ")"
    cur.execute(querry, tuple(values))
    cur.execute("SELECT id,name FROM " + table + " WHERE name=?", (input,))
    res = cur.fetchone()
    db.commit()
    if table == "Profs":
        return (res[0], res[1].replace(" ", "_"))
    return res


def linkLP(lid: int, pid: int):
    """declares that a Prof (id in database) offers a LVA (id in database)"""
    cur = db.cursor()
    cur.execute("INSERT INTO LPLink(LId,PId) VALUES(?,?)", (lid, pid))
    db.commit()


def convert_to_pdf(file: bytes) -> bytes | None:
    """Converts an image(thats all thats implemented right now) into a pdf."""
    # ft = filetype.guess(file)
    # cid = hash(file)
    # if (
    #     ft.mime
    #     == "application/vnd.openxmlformats-officedocument.wordprocessingml.document"
    # ):
    #     with open(f"./app/convert_temp/input{cid}.docx", "wb") as f:
    #         f.write(file)
    #     docx2pdf.convert(
    #         f"./app/convert_temp/input{cid}.docx", f"./app/convert_temp/output{cid}.pdf"
    #     )
    #     with open(f"./app/convert_temp/output{cid}.pdf", "rb") as f:
    #         cont = f.read()
    #     os.remove(f"./app/convert_temp/input{cid}.docx")
    #     os.remove(f"./app/convert_temp/output{cid}.pdf")
    #     return cont
    # elif (
    #     ft.mime
    #     == "application/vnd.openxmlformats-officedocument.presentationml.presentation"
    # ):
    #     with open("f./app/convert_temp/input{cid}.pptx", "wb") as f:
    #         f.write(file)
    #     pptxtopdf.convert(
    #         f"./app/convert_temp/input{cid}.pptx", f"./app/convert_temp/output{cid}.pdf"
    #     )
    #     with open(f"./app/convert_temp/output{cid}.pdf", "rb") as f:
    #         cont = f.read()
    #     os.remove(f"./app/convert_temp/input{cid}.pptx")
    #     os.remove(f"./app/convert_temp/output{cid}.pdf")
    #     return cont
    try:
        doc = pymupdf.Document(stream=file)
        return doc.convert_to_pdf()
    except (pymupdf.mupdf.FzErrorUnsupported, pymupdf.FileDataError) as e:
        print(e)
        return None


def filename_to_pdf(filename: str) -> str:
    farr = filename.split(".")
    if len(farr) > 1:
        farr[-1] = "pdf"
        filename = ".".join(farr)
    else:
        filename = filename + ".pdf"
    return filename


def make_filename_unique(filename: str, idx: int | None = None) -> str:
    cur = db.cursor()
    cur.execute("SELECT id FROM FIP WHERE filename=?", (filename,))
    res = cur.fetchall()
    if res is not None and len(res) > 0:
        farr = filename.split(".")
        if len(farr) > 1:
            farr[-2] = (
                farr[-2][:-1] + str(idx + 1) if idx is not None else farr[-2] + "_0"
            )
            filename = ".".join(farr)
        else:
            filename = (
                filename[:-1] + str(idx + 1) if idx is not None else filename + "_0"
            )
        idx = 0 if idx is None else idx + 1
        idx = idx if idx < 10 else idx - 10
        filename = make_filename_unique(filename, idx)
    return filename


async def save_files_to_folder(files: List[UploadFile]) -> str:
    filename = files[0].filename if files[0].filename is not None else "None"
    filename = filename.split(".")[0]
    if filename == "":
        filename = "None"
    filename = make_filename_unique(filename)
    os.mkdir(FILES_IN_PROGRESS + filename)
    for idx, file in enumerate(files):
        fn = file.filename if file.filename is not None else "None" + str(idx)
        with open(FILES_IN_PROGRESS + filename + "/" + fn, "wb") as f:
            f.write(await file.read())
    return filename


# async def get_submittion(request: Request):
#     reqJson = await request.form()
#     print(reqJson)
#     return {"done": "ok"}
