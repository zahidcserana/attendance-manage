from pydantic import BaseModel, EmailStr
from typing import Optional

from schemas.users import UserResponse


class EmployeeBase(BaseModel):
    name: str
    designation: str
    is_active: Optional[bool] = False


class EmployeeCreate(EmployeeBase):
    user_id: int


class EmployeeResponse(EmployeeBase):
    id: int
    user: UserResponse  # Nested response

    class Config:
        orm_mode = True
