from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from backend.models import ContactSubmission
from backend.database import init_db, get_db
from mangum import Mangum
import logging
import os

# Logging setup
logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s")
logger = logging.getLogger(__name__)

# Directories
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
STATIC_DIR = os.path.join(PROJECT_ROOT, "assets")
INDEX_PATH = os.path.join(PROJECT_ROOT, "index.html")

# FastAPI app
app = FastAPI()
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized")

def get_db_session(db: Session = Depends(get_db)):
    try:
        yield db
    finally:
        db.close()

@app.get("/", response_class=HTMLResponse)
async def read_root():
    return FileResponse(INDEX_PATH)

@app.get("/contact/", response_class=HTMLResponse)
async def get_contact_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact/", response_class=HTMLResponse)
async def submit_contact_form(
    request: Request,
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    message: str = Form(...),
    db: Session = Depends(get_db_session)
):
    submission = ContactSubmission(first_name=first_name, last_name=last_name, email=email, phone_number=phone_number, message=message)
    db.add(submission)
    db.commit()
    db.refresh(submission)
    return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})

# Mangum handler for Lambda
lambda_handler = Mangum(app)