import os
import logging
from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from backend.models import ContactSubmission
from backend.database import init_db, get_db
from mangum import Mangum  
from fastapi.middleware.cors import CORSMiddleware
import psycopg2
from psycopg2 import pool
import os



# Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)



# Application Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # KeepActivePro/
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")  
STATIC_DIR = os.path.join(PROJECT_ROOT, "assets")  
INDEX_PATH = os.path.join(PROJECT_ROOT, "index.html")  



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



# Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")



# Initialize Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)



# Initialize Database on Startup
@app.on_event("startup")
def startup_event():
    init_db()
    logger.info("Database initialized successfully")



# Dependency for Database Session
def get_db_session(db: Session = Depends(get_db)):
    try:
        yield db
    finally:
        db.close()



# Use connection pool to reuse connections
db_pool = psycopg2.pool.SimpleConnectionPool(
    minconn=1,
    maxconn=5,
    user=os.getenv("DB_USER", "ravipostgres"),
    password=os.getenv("DB_PASSWORD", "Ravi#1234"),
    host=os.getenv("DB_HOST", "keepactivepro-db.ct8akq62elqa.eu-north-1.rds.amazonaws.com"),
    database=os.getenv("DB_NAME", "postgres"),
    port=os.getenv("DB_PORT", "5432")
)

def get_db_connection():
    try:
        return db_pool.getconn()
    except Exception as e:
        print("Error getting DB connection:", str(e))
        return None



# **Home Page Route - Serve `index.html` from Root**
@app.get("/", response_class=HTMLResponse, summary="Serve the homepage")
async def read_root():
    logger.info("Serving index.html from root endpoint")
    return FileResponse(INDEX_PATH)



@app.get("/contact/", response_class=HTMLResponse, summary="Render contact form page")
async def get_contact_form(request: Request):
    logger.info("Rendering contact form page")
    return templates.TemplateResponse("contact.html", {"request": request})  



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
        return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save submission: {str(e)}")
        raise HTTPException(
            status_code=500,
            detail="An error occurred while processing your submission."
        )



@app.get("/thankyou/", response_class=HTMLResponse, summary="Render thank you page")
async def get_thank_you(request: Request):
    logger.info("Attempting to render thankyou.html")
    try:
        return templates.TemplateResponse("thankyou.html", {"request": request})
    except Exception as e:
        logger.error(f"Failed to load thankyou.html: {str(e)}")
        return HTMLResponse(content="Error loading thankyou.html", status_code=500)



# Exception Handler for Generic Errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.detail}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": exc.detail},
        status_code=exc.status_code
    )



# Middleware for Logging Requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response



# ✅ Test Endpoint to Check API Status
@app.get("/test", response_class=HTMLResponse, summary="Test API")
def read_test():
    return {"message": "API is working well"}



# ✅ New API Endpoints for Different Functionalities
@app.post("/feedback/", summary="Submit Feedback Form")
async def submit_feedback_form(
    request: Request,
    name: str = Form(..., alias="Name"),
    email: str = Form(..., alias="Email"),
    feedback: str = Form(..., alias="Feedback"),
    db: Session = Depends(get_db_session)
):
    logger.info(f"Received feedback from {email}")
    try:
        submission = ContactSubmission(
            first_name=name,
            last_name="",
            email=email,
            phone_number="",
            message=feedback
        )
        db.add(submission)
        db.commit()
        db.refresh(submission)
        return {"message": "Feedback submitted successfully!"}
    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save feedback: {str(e)}")
        raise HTTPException(status_code=500, detail="Error processing the request")



# Use Mangum to wrap FastAPI for AWS Lambda
lambda_handler = Mangum(app)



# Run FastAPI Server (Only needed for local development)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")