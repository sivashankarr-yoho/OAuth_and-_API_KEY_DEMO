from pydantic import BaseModel, ConfigDict, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    department_id: int | None = None
    employee_id: str = Field(min_length=1, max_length=100)
    salary: float = Field()
    shift: str = Field(min_length=1, max_length=100)
    address: str = Field(min_length=1, max_length=100)

class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    department_id: int | None

    model_config = ConfigDict(from_attributes=True)
