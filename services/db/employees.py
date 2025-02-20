from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from sqlalchemy import select

from models.employees import Employee
from models.users import User
from schemas.employees import EmployeeCreate
from schemas.users import CreateUserSchema


def create_employee(session: Session, employee_data):
    try:
        db_employee = Employee(**employee_data)
        session.add(db_employee)
        session.commit()
        session.refresh(db_employee)
        return db_employee
    except IntegrityError:
        session.rollback()
        raise HTTPException(status_code=400, detail="Something went wrong.")


def list_users(session: Session):
    return session.query(User).all()


def get_user(session: Session, email: str):
    return session.query(User).filter(User.email == email).one()


def get_user_by_id(session: Session, id: int):
    return session.query(User).filter(User.id == id).one()
