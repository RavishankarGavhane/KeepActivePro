from fastapi import FastAPI, Form, Depends, HTTPException
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
import os

from fastapi_backend.database import get_db, init_db
from fastapi_backend.models import ContactSubmission


app = FastAPI(title="KeepActive Pro API", description="Backend for KeepActive Pro contact form")

# Define paths
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # Backend directory
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # Main project directory
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")  # HTML files location
ASSETS_DIR = os.path.join(PROJECT_ROOT, "assets")  # Static files location
INDEX_FILE = os.path.join(PROJECT_ROOT, "index.html")  # Home page file

# Mount static directories
app.mount("/static", StaticFiles(directory=TEMPLATES_DIR), name="static")
app.mount("/assets", StaticFiles(directory=ASSETS_DIR), name="assets")

# Initialize database
init_db()

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

# Handle Contact Form Submission
@app.post("/contact/", response_class=RedirectResponse)
async def submit_contact_form(
    first_name: str = Form(...),
    last_name: str = Form(...),
    email: str = Form(...),
    phone_number: str = Form(...),
    message: str = Form(...),
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
