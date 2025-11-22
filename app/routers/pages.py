from fastapi import APIRouter, Request
from fastapi.templating import Jinja2Templates

# Setup the router
router = APIRouter(tags=["Frontend"])

# Tell FastAPI where your HTML files are located
templates = Jinja2Templates(directory="templates")

@router.get("/register")
async def register_page(request: Request):
    """
    Serves the Registration HTML page.
    """
    return templates.TemplateResponse("register.html", {"request": request})

@router.get("/login")
async def login_page(request: Request):
    """
    Serves the Login HTML page.
    """
    return templates.TemplateResponse("login.html", {"request": request})

@router.get("/dashboard")
async def dashboard_page(request: Request):
    """
    Serves the Dashboard page (Redirection target after login).
    If you don't have a dashboard.html yet, we render a simple message.
    """
    # Note: You will need a dashboard.html eventually. 
    # For now, we can reuse layout or a simple response, 
    # but ideally, create a simple dashboard.html.
    # If dashboard.html doesn't exist, this line will error. 
    # Do you have a dashboard.html? 
    # If not, let's just return a success message for now or render layout.
    return templates.TemplateResponse("layout.html", {"request": request})