from typing import Annotated
from typing import List, Dict, Tuple
from datetime import date
from fastapi import FastAPI, File, UploadFile, Request, Form
from fastapi.staticfiles import StaticFiles

app = FastAPI()

app.mount("/static", StaticFiles(directory="./"), name="static")


@app.post("/files/")
async def create_file(file: Annotated[bytes, File()]):
    return {"filesize": len(file)}


@app.post("/uploadfile/")
async def create_upload_file(file: UploadFile):
    content = await file.read()
    filename = file.filename if file.filename is not None else "None"
    with open("./app/files/" + filename, "wb") as f:
        f.write(content)
    app.mount("/files", StaticFiles(directory="./app/files/"), name="files")
    return {"filename": filename, "path": "/files/" + filename}


@app.post("/submit/")
async def get_submittion(
    lva: Annotated[str, Form()],
    prof: Annotated[str, Form()],
    fname: Annotated[str, Form()],
    sem: Annotated[str, Form()],
    stype: Annotated[str, Form()],
    date: Annotated[str, Form()],
    rects: Annotated[str, Form()],  # List[List[Tuple[float, float, float, float]]],
    pagescales: Annotated[str, Form()],  # Annotated[List[Dict[str, float]], Form()],
):
    print(lva, prof, fname, stype, sem, date, rects, pagescales)
    return {"done": "ok"}


# async def get_submittion(request: Request):
#     reqJson = await request.form()
#     print(reqJson)
#     return {"done": "ok"}
