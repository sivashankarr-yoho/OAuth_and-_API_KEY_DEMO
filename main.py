from contextlib import asynccontextmanager

from fastapi import Depends, FastAPI, HTTPException, status, Security, Query, Request
from sqlalchemy import select
from sqlalchemy.orm import Session

from database import Base, engine, get_db
from models import Department, Employee
from schemas import EmployeeCreate, EmployeeResponse
from dotenv import load_dotenv
from fastapi.security import APIKeyHeader
import os
import secrets
from slowapi import Limiter, _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded
from slowapi.util import get_remote_address



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

limiter = Limiter(key_func=get_remote_address)

app.state.limiter = limiter

app.add_exception_handler(
    RateLimitExceeded,
    _rate_limit_exceeded_handler
)

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
            employee_id=data.employee_id,
            address=data.address,
            salary=data.salary,
            shift=data.shift    
        )

        db.add(employee)
        db.commit()
        db.refresh(employee)

        return employee

    except Exception:
        db.rollback()
        raise

@app.get("/employees/cursor")
@limiter.limit("10/minute")
def get_employees_cursor(
    request: Request,
    limit: int = Query(default=10, ge=1, le=100),
    cursor: int | None = Query(default=None, ge=1),
    db: Session = Depends(get_db),
    authenticated: bool = Depends(verify_api_key),
):
    statement = select(Employee)

    if cursor is not None:
        statement = statement.where(Employee.id > cursor)

    statement = (
        statement
        .order_by(Employee.id)
        .limit(limit + 1)
    )

    employees = db.scalars(statement).all()

    has_more = len(employees) > limit
    data = employees[:limit]

    next_cursor = (
        data[-1].id if has_more and data else None
    )

    return {
        "data": data,
        "next_cursor": next_cursor,
        "has_more": has_more,
    }  


@app.get(
    "/employees",
    response_model=list[EmployeeResponse],
)
def get_employees(
    db: Session = Depends(get_db), 
    limit: int = Query(default=10, ge=1, le=100), 
    offset: int = Query(default=0, ge=0)
    ):
    statement = (
        select(Employee).order_by(Employee.id).limit(limit).offset(offset)
    )
    
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
