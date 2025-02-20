from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.users import User
from schemas.users import CreateUserSchema
from services.db import employees as employee_db_services


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
