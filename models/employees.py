from sqlalchemy import (
    LargeBinary,
    Column,
    Enum,
    String,
    Integer,
    Boolean,
    ForeignKey,
)
from sqlalchemy.orm import relationship

from db_initializer import Base


class Employee(Base):
    __tablename__ = "employees"

    id = Column(Integer, nullable=False, primary_key=True)
    name = Column(String(225), nullable=False)
    designation = Column(String(225), nullable=False)
    is_active = Column(Boolean, default=False)

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)

    user = relationship("User", back_populates="employees")
