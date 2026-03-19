from fastapi import APIRouter, HTTPException , Request ,Form
from fastapi.responses import RedirectResponse
from fastapi.templating import Jinja2Templates
from authenticator.upstox_authenticator import Authenticator

router = APIRouter(prefix="/authenticator", tags=["Authenticator"])
auth=Authenticator(mode="api")
templates = Jinja2Templates(directory="templates")

@router.get("/login")
def login(request:Request):
    if not auth.check_env_file():
        return RedirectResponse(url="/authenticator/registration")
    else:
        if auth.check_token_validity():
            response = RedirectResponse(url="/config/settings", status_code=303)
            # Set token in a secure cookie
            response.set_cookie(
                key="access_token",
                value=auth.access_token,
                httponly=True,   # prevents JavaScript access
                secure=True,     # only over HTTPS
                samesite="Lax"   # controls cross-site behavior
            )
            return response
        else:
            return templates.TemplateResponse("login.html", {"request": request})

@router.get("/registration")
def registration(request:Request):
    return templates.TemplateResponse("credential_form.html", {"request": request})

@router.post("/save_credentials")
def save_credentials(
    request: Request,
    api_key: str = Form(...),
    api_secret: str = Form(...),
    redirect_url: str = Form(...),
    state: str = Form(...)
):
    auth.save_credentials(api_key, api_secret, redirect_url, state)
    return RedirectResponse(url="/authenticator/login", status_code=303)

@router.get("/generate_login_uri")
def generate_login_url(request:Request):
    if not auth.check_env_file():
        raise HTTPException(status_code=400, detail="API credentials not found. Please save credentials first.")
    auth.load_credentials()
    return RedirectResponse(auth.url)

@router.post("/token")
def fetch_access_token(request: Request, redirect_uri: str = Form(...)):
    code = auth.get_code(redirect_uri)
    if not code:
        raise HTTPException(status_code=400, detail="Invalid redirect URI")
    auth.fetch_token(code)
    if not auth.access_token:
        raise HTTPException(status_code=401, detail="Failed to fetch token")
    auth.update_access_token()
    if auth.check_token_validity():
        response = RedirectResponse(url="/config/settings", status_code=303)
        # Set token in a secure cookie
        response.set_cookie(
            key="access_token",
            value=auth.access_token,
            httponly=True,   # prevents JavaScript access
            secure=True,     # only over HTTPS
            samesite="Lax"   # controls cross-site behavior
        )
        return response

    else:
        raise HTTPException(status_code=401, detail="Token expired or invalid")
