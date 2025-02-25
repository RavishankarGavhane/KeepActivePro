# fastapi_backend/main.py
from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import get_db, init_db
from .models import ContactSubmission
import os

app = FastAPI(title="KeepActive Pro API", description="Backend for KeepActive Pro contact form")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(BASE_DIR)
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")
INDEX_FILE = os.path.join(PROJECT_ROOT, "index.html")

app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")
templates = Jinja2Templates(directory=TEMPLATES_DIR)

init_db()

@app.get("/", response_class=HTMLResponse)
async def get_home_page():
    try:
        with open(INDEX_FILE, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail="Home page not found")

@app.get("/contact/", response_class=HTMLResponse)
async def get_contact_page(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})

@app.post("/contact/", response_class=HTMLResponse)
async def submit_contact_form(
    request: Request,
    first_name: str = Form(..., alias="FirstName"),
    last_name: str = Form(..., alias="LastName"),
    email: str = Form(..., alias="Email"),
    phone_number: str = Form(..., alias="PhoneNumber"),
    message: str = Form(..., alias="WHAT_DO_YOU_HAVE_IN_MIND"),
    db: Session = Depends(get_db)
):
    try:
        submission = ContactSubmission(
            first_name=first_name,
            last_name=last_name,
            email=email,
            phone_number=phone_number,
            message=message
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving submission: {str(e)}")