from fastapi import FastAPI, Request, Form
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from pydantic import BaseModel, Field, ValidationError, field_validator
from datetime import datetime

app = FastAPI()

app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

productos_db = []


class ProductoPapeleria(BaseModel):
    nombre: str = Field(min_length=3, max_length=80)
    categoria: str = Field(min_length=3, max_length=40)
    precio: float = Field(gt=0)
    stock: int = Field(ge=0)
    Descripcion: str = Field(min_length=3, max_length=20)

    @field_validator("nombre")
    @classmethod
    def validar_nombre(cls, value):
        if not value.strip():
            raise ValueError("El nombre no puede estar vacío")
        return value.strip()

    @field_validator("categoria")
    @classmethod
    def validar_categoria(cls, value):
        categorias_validas = ["Escolar", "Oficina", "Arte", "Tecnología"]
        if value not in categorias_validas:
            raise ValueError("La categoría no es válida")
        return value

    @field_validator("Descripcion")
    @classmethod
    def validar_Descripcion(cls, value):
        return value.strip().upper()


@app.get("/")
def inicio():
    return {"mensaje": "API de papelería activa"}


@app.get("/productos", response_class=HTMLResponse)
def ver_productos(request: Request):
    return templates.TemplateResponse(
        "productos.html",
        {
            "request": request,
            "title": "Papelería Central",
            "heading": "Inventario de Papelería",
            "year": datetime.now().year,
            "productos": productos_db,
            "errores": [],
            "form_data": {}
        }
    )


@app.post("/productos", response_class=HTMLResponse)
def crear_producto_html(
    request: Request,
    nombre: str = Form(...),
    categoria: str = Form(...),
    precio: float = Form(...),
    stock: int = Form(...),
    Descripcion: str = Form(...)
):
    form_data = {
        "nombre": nombre,
        "categoria": categoria,
        "precio": precio,
        "stock": stock,
        "Descripcion": Descripcion
    }

    try:
        producto = ProductoPapeleria(
            nombre=nombre,
            categoria=categoria,
            precio=precio,
            stock=stock,
            Descripcion=Descripcion
        )
        productos_db.append(producto)
        errores = []
        form_data = {}
    except ValidationError as e:
        errores = [err["msg"] for err in e.errors()]

    return templates.TemplateResponse(
        "productos.html",
        {
            "request": request,
            "title": "Papelería Central",
            "heading": "Inventario de Papelería",
            "year": datetime.now().year,
            "productos": productos_db,
            "errores": errores,
            "form_data": form_data
        }
    )
