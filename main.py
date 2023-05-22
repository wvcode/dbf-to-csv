# -*- coding: utf-8 -*-

import os
import random
import time
import traceback
from pathlib import Path

from typing import Annotated
from fastapi import BackgroundTasks, FastAPI, File, Form, UploadFile, Request
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates

from dotenv import load_dotenv

import uvicorn

from simpledbf import Dbf5
import pandas as pd

load_dotenv()

app = FastAPI()
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")


async def del_old_files():
  # Defina o diretório onde os arquivos estão localizados
  diretorio = Path('static')
  # Obtenha o tempo atual em segundos
  tempo_atual = time.time()
  # Percorra todos os arquivos no diretório
  for arquivo in diretorio.iterdir():
    if arquivo.is_file() and tempo_atual - arquivo.stat().st_ctime > 3600 and arquivo.suffix in ['.dbf', '.csv']:
        os.remove(arquivo)    


async def converter(nomearquivo):
  try:
    numero = random.randint(10000, 99999)
    nomecsv = nomearquivo.lower().replace('.dbf','.csv')
    csvname = f"static/{str(numero)}_{nomecsv}"
    dbf = Dbf5(f"static/{nomearquivo}", codec='utf-8')
    dbf.to_csv(csvname)
    return csvname
  except:
    print(traceback.format_exc())
    return "none"


@app.get("/")
async def read_form(request: Request):
    return templates.TemplateResponse("form.html", {"request": request})


@app.post("/converter")
async def process_form(
    request: Request,
    arquivo: Annotated[UploadFile, File()],
):
    file_path = os.path.join("static", arquivo.filename)
    with open(file_path, "wb") as file:
        file.write(await arquivo.read())

    await del_old_files()
    filename = await converter(arquivo.filename)

    return templates.TemplateResponse("form.html", {"request": request, "arquivo": filename})


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
