from fastapi import FastAPI, Request
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from endpoints.authenticator import router as auth_router
from endpoints.config import router as config_router

app = FastAPI(title="Trading Bot API", version="1.0")
templates = Jinja2Templates(directory="templates")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # or restrict to your frontend domain
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(auth_router)
app.include_router(config_router)

@app.get("/")
def root(request: Request):
    return templates.TemplateResponse("intro.html", {"request": request})
