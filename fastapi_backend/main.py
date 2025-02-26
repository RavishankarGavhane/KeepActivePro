from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates  # Import Jinja2 Templates
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

# Initialize Jinja2 Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# Lifespan event for startup/shutdown
@asynccontextmanager
async def lifespan(app: FastAPI):
    """Initialize the database when the application starts"""
    print("🚀 Initializing Database...")
    init_db()  # Create tables if they don't exist
    yield
    print("🛑 Shutting down...")

# Initialize FastAPI with lifespan handler
app = FastAPI(
    title="KeepActive Pro API",
    description="Backend for KeepActive Pro contact form",
    lifespan=lifespan,
)

# Mount static directories
app.mount("/static", StaticFiles(directory=ASSETS_DIR), name="static")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Serve Home Page (index.html)
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    """Serve the home page"""
    return templates.TemplateResponse("index.html", {"request": request})

# Serve Contact Page (contact.html)
@app.get("/contact/", response_class=HTMLResponse)
async def contact_page(request: Request):
    """Serve the contact page"""
    return templates.TemplateResponse("contact.html", {"request": request})

# Serve Thank You Page (Dynamically Rendered)
@app.get("/thankyou.html", response_class=HTMLResponse)
async def thank_you_page(request: Request, email: str = None):
    """Render the thank you page with the submitted email"""
    return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})

# Handle Contact Form Submission
@app.post("/contact/")
async def submit_contact_form(
    request: Request,
    first_name: str = Form(...),  # Matches 'name="FirstName"' in HTML
    last_name: str = Form(...),   # Matches 'name="LastName"' in HTML
    email: str = Form(...),       # Matches 'name="Email"' in HTML
    phone_number: str = Form(...),# Matches 'name="PhoneNumber"' in HTML
    message: str = Form(...),     # Matches 'name="WHAT_DO_YOU_HAVE_IN_MIND"' in HTML
    db: Session = Depends(get_db)
):
    """Handles form submission and saves data to the database"""
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
        
        # Render the thank you page dynamically with the user's email
        return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})
    
    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving submission: {str(e)}")

# Serve HTML helper function
def serve_html(file_path: str, error_message: str):
    """Helper function to serve static HTML files"""
    try:
        with open(file_path, "r") as f:
            return HTMLResponse(content=f.read())
    except FileNotFoundError:
        raise HTTPException(status_code=404, detail=error_message)
