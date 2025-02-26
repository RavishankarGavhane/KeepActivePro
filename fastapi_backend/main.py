from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os
from contextlib import asynccontextmanager

from fastapi_backend.database import get_db, init_db
from fastapi_backend.models import ContactSubmission

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend directory
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Main project directory
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")  # HTML files location
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")  # Static files location
INDEX_FILE = os.path.join(PROJECT_ROOT, "index.html")  # Home page file

# Lifespan event for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    print("🚀 Initializing Database...")
    init_db()  # Initialize database on startup
    yield
    print("🛑 Shutting down...")

# Initialize FastAPI with lifespan handler
app = FastAPI(
    title="KeepActive Pro API",
    description="Backend for KeepActive Pro contact form",
    lifespan=lifespan,
)

# Mount static directories
app.mount("/static", StaticFiles(directory=TEMPLATES_DIR), name="static")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Serve Home Page (index.html)
@app.get("/", response_class=HTMLResponse)
async def get_home_page():
    return serve_html(INDEX_FILE, "Home page not found")

# Serve Contact Page (contact.html)
@app.get("/contact/", response_class=HTMLResponse)
async def get_contact_page():
    return serve_html(os.path.join(TEMPLATES_DIR, "contact.html"), "Contact page not found")

# Serve Thank You Page (thankyou.html)
@app.get("/thankyou.html", response_class=HTMLResponse)
async def get_thank_you_page():
    return serve_html(os.path.join(TEMPLATES_DIR, "thankyou.html"), "Thank you page not found")

# Handle Contact Form Submission (with Corrected Field Names)
@app.post("/contact/", response_class=RedirectResponse)
async def submit_contact_form(
    FirstName: str = Form(...),  # Matches 'name="FirstName"' in HTML
    LastName: str = Form(...),   # Matches 'name="LastName"' in HTML
    Email: str = Form(...),      # Matches 'name="Email"' in HTML
    PhoneNumber: str = Form(...),# Matches 'name="PhoneNumber"' in HTML
    WHAT_DO_YOU_HAVE_IN_MIND: str = Form(...),  # Matches 'name="WHAT_DO_YOU_HAVE_IN_MIND"'
    db: Session = Depends(get_db)
):
    try:
        submission = ContactSubmission(
            first_name=FirstName,
            last_name=LastName,
            email=Email,
            phone_number=PhoneNumber,
            message=WHAT_DO_YOU_HAVE_IN_MIND
        )
        db.add(submission)
        db.commit()
        return RedirectResponse(url="/thankyou.html", status_code=303)
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving submission: {str(e)}")

# Serve HTML helper function
def serve_html(file_path: str, error_message: str):
    try:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=error_message)
