from sqlalchemy import (
    LargeBinary,
    Column,
    Enum,
    String,
    Integer,
    Boolean,
    UniqueConstraint,
    PrimaryKeyConstraint
)
from sqlalchemy.orm import relationship

import jwt
import bcrypt
import enum

from db_initializer import Base

import settings


class UserType(enum.Enum):
    admin = "admin"
    user = "user"



class User(Base):
    USER_TYPES = [UserType.admin.value, UserType.user.value]

    """Models a user table"""
    __tablename__ = "users"
    email = Column(String(225), index=True, unique=True)
    id = Column(Integer, nullable=False, primary_key=True)
    hashed_password = Column(LargeBinary, nullable=False)
    name = Column(String(225), nullable=False)
    type = Column(String(20), default=UserType.user)
    is_active = Column(Boolean, default=False)
    profile_image = Column(String(500), nullable=True)

    UniqueConstraint("email", name="uq_user_email")
    PrimaryKeyConstraint("id", name="pk_user_id")
    employees = relationship("Employee", back_populates="user")

    def __repr__(self):
        """Returns string representation of model instance"""
        return "<User {name!r}>".format(name=self.name)

    @staticmethod
    def hash_password(password) -> str:
        """Transforms password from it's raw textual form to
        cryptographic hashes
        """
        return bcrypt.hashpw(password.encode(), bcrypt.gensalt())

    def validate_password(self, password) -> bool:
        """Confirms password validity"""
        return bcrypt.checkpw(password.encode(), self.hashed_password)

    def generate_token(self) -> dict:
        """Generate access token for user"""
        return {
            "access_token": jwt.encode(
                {"name": self.name, "email": self.email},
                settings.SECRET_KEY
            )
        }
