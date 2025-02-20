from pydantic import BaseModel, Field, EmailStr

from models.users import UserType


class UserBaseSchema(BaseModel):
    email: EmailStr
    name: str


class CreateUserSchema(UserBaseSchema):
    hashed_password: str = Field(alias="password")
    type: str = Field(default=UserType.user)


class UserLoginSchema(BaseModel):
    email: EmailStr = Field(alias="username")
    password: str


class UserSchema(UserBaseSchema):
    id: int
    is_active: bool = Field(default=False)

    class Config:
        orm_mode = True


class UserResponse(UserBaseSchema):
    id: int

    class Config:
        orm_mode = True
