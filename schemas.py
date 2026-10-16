from pydantic import BaseModel, ConfigDict, Field


class EmployeeCreate(BaseModel):
    name: str = Field(min_length=1, max_length=100)
    email: str = Field(max_length=255)
    department_id: int | None = None


class EmployeeResponse(BaseModel):
    id: int
    name: str
    email: str
    department_id: int | None

    model_config = ConfigDict(from_attributes=True)
