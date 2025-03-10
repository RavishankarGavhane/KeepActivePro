import os
import logging
from fastapi import FastAPI, Form, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, FileResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from mangum import Mangum
from fastapi.middleware.cors import CORSMiddleware
from backend.models import ContactSubmission
from backend.database import init_db, get_db
from backend.metrics_handler import router as metrics_router

# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# Application Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
FRONTEND_DIR = os.path.abspath(os.path.join(BASE_DIR, "../frontend"))  # Move up to frontend
STATIC_DIR = os.path.join(FRONTEND_DIR, "assets")  # Access assets under frontend

# Initialize FastAPI App
app = FastAPI(
    title="KeepActive Pro API",
    description="A professional backend API for KeepActive Pro, handling contact forms and static content.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# Add CORS Middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["https://www.keepactivepro.com"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Mount Static Files (For Serving Assets)
app.mount("/assets", StaticFiles(directory=STATIC_DIR), name="assets")

# Initialize Database on Startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized successfully")

# Dependency for Database Session
def get_db_session(db: Session = Depends(get_db)):
    try:
        yield db
    finally:
        db.close()

# Serve Homepage
@app.get("/", response_class=FileResponse, summary="Serve homepage")
async def read_root():
    return FileResponse(os.path.join(FRONTEND_DIR, "index.html"))

# Serve Contact Page as a Static File
@app.get("/contact/", response_class=FileResponse, summary="Serve contact page")
async def get_contact_form():
    return FileResponse(os.path.join(FRONTEND_DIR, "contact.html"))

# Handle Contact Form Submission
@app.post("/contact/", response_class=HTMLResponse, summary="Handle contact form submission")
async def submit_contact_form(
    request: Request,
    first_name: str = Form(..., alias="FirstName"),
    last_name: str = Form(..., alias="LastName"),
    email: str = Form(..., alias="Email"),
    phone_number: str = Form(..., alias="PhoneNumber"),
    message: str = Form(..., alias="WHAT_DO_YOU_HAVE_IN_MIND"),
    db: Session = Depends(get_db_session)
):
    logger.info(f"Received contact form submission from {email}")
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

        logger.info(f"Successfully saved submission for {email}")

        return RedirectResponse(url="/thankyou/", status_code=303)

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="An error occurred while processing your submission."
        )

# Serve Thank You Page as a Static File
@app.get("/thankyou/", response_class=FileResponse, summary="Serve thank you page")
async def get_thank_you_page():
    return FileResponse(os.path.join(FRONTEND_DIR, "thankyou.html"))

# AWS Lambda Handler
lambda_handler = Mangum(app)
