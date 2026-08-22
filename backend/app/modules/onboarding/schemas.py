from datetime import date
from pydantic import BaseModel


class OnboardingTaskOut(BaseModel):
    id: int
    employee_id: int
    task_name: str
    status: str
    due_date: date | None = None
    role_template: str | None = None

    model_config = {"from_attributes": True}
