import os
import uuid
from typing import Dict

from fastapi import (
    status,

    HTTPException,
    UploadFile,
    FastAPI,
    Depends,
    File,
    Body
)
from fastapi.security import OAuth2PasswordBearer
from fastapi.security import OAuth2PasswordRequestForm

from sqlalchemy.orm import Session

import cloudinary
import cloudinary.uploader
from dotenv import load_dotenv

from db_initializer import get_db
from models import users as user_model
from models.users import UserType, User
from services.db import users as user_db_services
from schemas.users import (
    CreateUserSchema,
    UserLoginSchema,
    UserSchema
)

load_dotenv()

cloudinary.config(
    cloud_name=os.getenv("CLOUDINARY_CLOUD_NAME"),
    api_key=os.getenv("CLOUDINARY_API_KEY"),
    api_secret=os.getenv("CLOUDINARY_API_SECRET"),
    secure=True
)

app = FastAPI()
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="login")

ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png"}
MAX_FILE_SIZE_MB = 5  # Limit file size to 5MB


@app.post('/login', response_model=Dict)
def login(
        payload: OAuth2PasswordRequestForm = Depends(),
        session: Session = Depends(get_db)
):
    """Processes user's authentication and returns a token on successful authentication.
    request body:
    - username: Unique identifier for a user e.g email, phone number, name
    - password:
    """
    try:
        user: user_model.User = user_db_services.get_user(session=session, email=payload.username)
    except:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials"
        )

    is_validated: bool = user.validate_password(payload.password)
    if not is_validated:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid user credentials"
        )

    return user.generate_token()


@app.post('/signup', response_model=UserSchema)
def signup(
        payload: CreateUserSchema = Body(),
        session: Session = Depends(get_db)
):
    """Processes request to register user account."""
    payload.hashed_password = user_model.User.hash_password(payload.hashed_password)
    return user_db_services.create_user(session, user=payload)


@app.get("/profile/{id}", response_model=UserSchema)
def profile(
        id: int,
        session: Session = Depends(get_db),
        token: str = Depends(oauth2_scheme),
):
    """ Processes request to retrieve the requesting user profile """
    return user_db_services.get_user_by_id(session=session, id=id)


@app.post('/upload-profile-image', response_model=str)
async def upload_profile_image(
        user_id: int = 40,
        token: str = Depends(oauth2_scheme),
        file: UploadFile = File(description="User profile image"),
        db: Session = Depends(get_db),
):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(status_code=404, detail="User not found.")

    image_url = await user_db_services.upload_profile_image(file)

    user.profile_image = image_url
    db.commit()
    db.refresh(user)

    return image_url
    #
    # """Uploads a user profile image to Cloudinary and returns the URL."""
    #
    # # Validate file type
    # if file.content_type not in ALLOWED_IMAGE_TYPES:
    #     raise HTTPException(status_code=400, detail="Invalid file type. Only JPEG and PNG are allowed.")
    #
    # # Fetch the user from the database
    # user = db.query(User).filter(User.id == user_id).first()
    # if not user:
    #     raise HTTPException(status_code=404, detail="User not found.")
    #
    # # Validate file size
    # file_size = await file.read()
    # if len(file_size) > MAX_FILE_SIZE_MB * 1024 * 1024:
    #     raise HTTPException(status_code=400, detail="File size exceeds 5MB limit.")
    #
    # # Reset file cursor after reading size
    # await file.seek(0)
    #
    # try:
    #     # Generate a unique public_id (e.g., user_id + UUID)
    #     unique_id = str(uuid.uuid4())
    #     upload_result = cloudinary.uploader.upload(
    #         file.file,
    #         overwrite=True,
    #         unique_filename=True,
    #         public_id=f"profile_images/{unique_id}",
    #         resource_type="image",
    #     )
    #
    #     image_url = upload_result.get("secure_url")  # Get Cloudinary's secure URL
    #
    #     # Save image URL to DB (pseudo-code)
    #     # save_image_url_to_db(user_id, image_url)
    #
    #     user.profile_image = image_url
    #     db.commit()
    #     db.refresh(user)
    #
    #     return image_url
    #
    # except Exception as e:
    #     raise HTTPException(status_code=500, detail=f"Image upload failed: {str(e)}")
