import os
import logging
from typing import Optional
from fastapi import FastAPI, Form, Depends, HTTPException, Request, status
from fastapi.responses import HTMLResponse, FileResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from backend.models import ContactSubmission
from backend.database import init_db, get_db

# ✅ Configure Logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    handlers=[logging.StreamHandler()]
)
logger = logging.getLogger(__name__)

# ✅ Application Configuration
BASE_DIR = os.path.dirname(os.path.abspath(__file__))  # backend/
PROJECT_ROOT = os.path.dirname(BASE_DIR)  # KeepActivePro/
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")  # `/home/ravishankar/KeepActivePro/templates/`
STATIC_DIR = os.path.join(PROJECT_ROOT, "assets")  # `/home/ravishankar/KeepActivePro/assets/`
INDEX_PATH = os.path.join(PROJECT_ROOT, "index.html")  # `/home/ravishankar/KeepActivePro/index.html`

# ✅ Initialize FastAPI App
app = FastAPI(
    title="KeepActive Pro API",
    description="A professional backend API for KeepActive Pro, handling contact forms and static content.",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json"
)

# ✅ Mount Static Files
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

# ✅ Initialize Templates
templates = Jinja2Templates(directory=TEMPLATES_DIR)

# ✅ Initialize Database on Startup
@app.on_event("startup")
async def startup_event():
    init_db()
    logger.info("Database initialized successfully")
    logger.info(f"Templates Directory: {TEMPLATES_DIR}")
    logger.info(f"Static Directory: {STATIC_DIR}")
    logger.info(f"Index.html Path: {INDEX_PATH}")

# ✅ Dependency for Database Session
def get_db_session(db: Session = Depends(get_db)):
    try:
        yield db
    finally:
        db.close()

# 🚀 **Home Page Route - Serve `index.html` from Root**
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
        # ✅ Save submission to the database
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

        # ✅ Render the Thank You Page Directly
        return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})

    except Exception as e:
        db.rollback()
        logger.error(f"Failed to save submission: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
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


# ✅ Exception Handler for Generic Errors
@app.exception_handler(HTTPException)
async def http_exception_handler(request: Request, exc: HTTPException):
    logger.error(f"HTTP error occurred: {exc.detail}")
    return templates.TemplateResponse(
        "error.html",
        {"request": request, "message": exc.detail},
        status_code=exc.status_code
    )

# ✅ Middleware for Logging Requests
@app.middleware("http")
async def log_requests(request: Request, call_next):
    logger.info(f"Incoming request: {request.method} {request.url}")
    response = await call_next(request)
    return response

# ✅ Run FastAPI Server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000, log_level="info")
