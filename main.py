from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status, Security
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Department, Employee
from schemas import EmployeeCreate, EmployeeResponse
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
import os
import secrets


@asynccontextmanager
async def lifespan(app: FastAPI):
    Base.metadata.create_all(bind=engine)
    yield
    

load_dotenv()

API_KEY = os.getenv('API_KEY')    

api_key_header = APIKeyHeader(
    name="X-API-KEY",
    auto_error=False
)

app = FastAPI(lifespan=lifespan)

async def verify_api_key (api_key: str | None = Security(api_key_header)):
    if not API_KEY:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
    
    if api_key is None or not secrets.compare_digest(api_key, API_KEY):
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Invalid API Key")
    
    return True    

@app.post(
    "/employees/create",
    response_model=EmployeeResponse,
    status_code=status.HTTP_201_CREATED,
)
def create_employee(
    data: EmployeeCreate,
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key)
):
    try:
        employee = Employee(
            name=data.name,
            email=data.email,
            department_id=data.department_id,
            employee_id="EMP_001",
            address="Not specified",
        )

        db.add(employee)
        db.commit()
        db.refresh(employee)

        return employee

    except Exception:
        db.rollback()
        raise


@app.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def get_employees(db: Session = Depends(get_db)):
    statement = select(Employee).order_by(Employee.id)
    return db.scalars(statement).all()


@app.get(
    "/employees/{employee_id}",
    response_model=EmployeeResponse,
)
def get_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    return employee


@app.delete("/employees/{employee_id}")
def delete_employee(
    employee_id: int,
    db: Session = Depends(get_db),
):
    employee = db.get(Employee, employee_id)

    if employee is None:
        raise HTTPException(
            status_code=404,
            detail="Employee not found",
        )

    db.delete(employee)
    db.commit()

    return {"message": "Employee deleted successfully"}


if __name__ == "__main__":
    import uvicorn

    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=True)
