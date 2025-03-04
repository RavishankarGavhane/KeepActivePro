from fastapi import FastAPI, Form, Depends, HTTPException, Request
from fastapi.responses import HTMLResponse, RedirectResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from sqlalchemy.orm import Session
from .database import ContactSubmission, get_db, init_db
import os

# Initialize FastAPI app
app = FastAPI(
    title="KeepActive Pro API",
    description="Backend for KeepActive Pro contact form & future APIs",
    version="1.0.0"
)

# Initialize Database
init_db()

# Configure Template & Static Files
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
TEMPLATES_DIR = os.path.join(BASE_DIR, "../templates")
STATIC_DIR = os.path.join(BASE_DIR, "../assets")

templates = Jinja2Templates(directory=TEMPLATES_DIR)
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")


# 🚀 **Home Page Route**
@app.get("/", response_class=HTMLResponse)
async def home_page(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


# 🚀 **Contact Form - Render Page**
@app.get("/contact/", response_class=HTMLResponse)
async def get_contact_form(request: Request):
    return templates.TemplateResponse("contact.html", {"request": request})


# 🚀 **Handle Contact Form Submission**
@app.post("/contact/")
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
        # Save submission to the database
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

        # Redirect to thank you page with email
        return templates.TemplateResponse("thankyou.html", {"request": request, "email": email})

    except Exception as e:
        db.rollback()
        raise HTTPException(status_code=500, detail=f"Error saving submission: {str(e)}")


# 🚀 **Health Check API (For AWS Lambda)**
@app.get("/health")
async def health_check():
    return {"status": "OK", "message": "KeepActivePro API is running smoothly!"}


# 🚀 **AWS Lambda Compatibility**
def handler(event, context):
    from mangum import Mangum
    lambda_handler = Mangum(app)
    return lambda_handler(event, context)
