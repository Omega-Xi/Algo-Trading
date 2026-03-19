from fastapi import APIRouter, HTTPException , Request ,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates

router = APIRouter(prefix="/config", tags=["Configurations"])
templates = Jinja2Templates(directory="templates")

@router.get("/settings")
def settings(request: Request):
    access_token = request.cookies.get("access_token")
    if not access_token:
        return templates.TemplateResponse("unauthorized.html", {"request": request}, status_code=401)
    else:
        response = templates.TemplateResponse("config.html", {"request": request})
        response.delete_cookie("access_token")
        return response

@router.post("/save_config")
def save_config(request: Request, config_data: str = Form(...)):
    pass