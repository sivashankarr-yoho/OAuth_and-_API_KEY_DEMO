from decimal import Decimal
from sqlalchemy import String, ForeignKey, Numeric, Boolean, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from database import Base


class Department(Base):
    __tablename__ = "departments"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )

    employees: Mapped[list["Employee"]] = relationship(back_populates="department")


class Employee(Base):
    __tablename__ = "employees"

    id: Mapped[int] = mapped_column(primary_key=True)
    name: Mapped[str] = mapped_column(
        String(200),
        nullable=False,
    )
    email: Mapped[str] = mapped_column(
        String(255),
        unique=True,
        nullable=False,
    )

    department_id: Mapped[int | None] = mapped_column(
        ForeignKey("departments.id"),
        nullable=True,
    )

    employee_id: Mapped[str] = mapped_column(
        String(100),
        unique=True,
        nullable=False,
    )
    
    address: Mapped[str] = mapped_column(
        String(100),
        nullable=False,
    )

    salary: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)

    is_active: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("true"),
    )
    
    is_deleted: Mapped[bool] = mapped_column(
        Boolean,
        nullable=False,
        server_default=text("false"),
    )
    
    shift: Mapped[str] = mapped_column(
        String(100),
        nullable=True
    )

    department: Mapped["Department | None"] = relationship(back_populates="employees")
