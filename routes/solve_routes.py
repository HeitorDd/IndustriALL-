import os
from fastapi import APIRouter, UploadFile, File, HTTPException
from fastapi.responses import HTMLResponse, Response
from controllers.solve_controller import SolveController
from config import settings

router = APIRouter()

@router.get("/", response_class=HTMLResponse)
def get_index():
    """
    Retorna o arquivo HTML principal (dashboard de controle) a partir da pasta estática.
    """
    index_path = os.path.join(settings.STATIC_DIR, "index.html")
    if not os.path.exists(index_path):
        raise HTTPException(status_code=404, detail="index.html não encontrado no diretório static.")
    with open(index_path, "r", encoding="utf-8") as f:
        return f.read()

@router.get("/index.css")
def get_css():
    """
    Retorna a folha de estilo CSS correspondente ao visual Ethereal Glass do projeto.
    """
    css_path = os.path.join(settings.STATIC_DIR, "index.css")
    if not os.path.exists(css_path):
        raise HTTPException(status_code=404, detail="index.css não encontrado no diretório static.")
    with open(css_path, "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="text/css")

@router.get("/index.js")
def get_js():
    """
    Retorna a lógica de script JavaScript principal que controla as interações do frontend.
    """
    js_path = os.path.join(settings.STATIC_DIR, "index.js")
    if not os.path.exists(js_path):
        raise HTTPException(status_code=404, detail="index.js não encontrado no diretório static.")
    with open(js_path, "r", encoding="utf-8") as f:
        return Response(content=f.read(), media_type="application/javascript")

@router.post("/solve")
async def solve_backlog(file: UploadFile = File(...)):
    """
    Recebe a planilha Excel enviada, aciona a otimização e retorna os resultados estruturados.
    """
    return SolveController.process_scheduling(file)
