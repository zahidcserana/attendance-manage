import os
import uuid

from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.users import User
from schemas.users import CreateUserSchema
from services.db import employees as employee_db_services
from dotenv import load_dotenv
import cloudinary
import cloudinary.uploader

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE_MB = 5  # Limit file size to 5MB


def create_user(session: Session, user: CreateUserSchema):
    if user.type and user.type not in User.USER_TYPES:
        raise HTTPException(status_code=400, detail="Invalid user type.")

    try:
        db_user = User(**user.dict())
        session.add(db_user)
        session.commit()
        session.refresh(db_user)

        employee_data = {
            'user_id': db_user.id,
            'name': db_user.name,
            'designation': 'Staff'
        }

        employee_db_services.create_employee(session, employee_data)
        return db_user
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Email already exists.")


def list_users(session: Session):
    return session.query(User).all()


def get_user(session: Session, email: str):
    return session.query(User).filter(User.email == email).one()


def get_user_by_id(session: Session, id: int):
    return session.query(User).filter(User.id == id).one()


async def upload_profile_image(file):
    """Uploads a user profile image to Cloudinary and returns the URL."""

    # Validate file type
    if file.content_type not in ALLOWED_IMAGE_TYPES:
        raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")

    # Validate file size
    file_size = await file.read()
    if len(file_size) > MAX_FILE_SIZE_MB * 1024 * 1024:
        raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")

    # Reset file cursor after reading size
    await file.seek(0)

    try:
        # Generate a unique public_id (e.g., user_id + UUID)
        unique_id = str(uuid.uuid4())
        upload_result = cloudinary.uploader.upload(
            file.file,
            overwrite=True,
            unique_filename=True,
            public_id=f"profile_images/{unique_id}",
            resource_type="image",
        )

        image_url = upload_result.get("secure_url")  # Get Cloudinary's secure URL

        return image_url

    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
