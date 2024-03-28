
from datetime import datetime
from Freee import HumanResourse

def approval_paid_holiday(request_date: str, request_reason: str, user_email: str, hr: HumanResourse):
    now = datetime.now()
    employees = hr.get_employees(year=now.year, month=now.month)["employees"]
    employee_id = get_employee_id(employees=employees, target_email=user_email)
    work_record = hr.update_employee_work_record(
        employee_id=employee_id,
        date=request_date,
        note=request_reason,
        paid_holiday=1
    )
    return work_record

def get_employee_id(employees: list, target_email: str):
    for employee in employees:
        if employee["profile_rule"]["email"] is not None and employee["profile_rule"]["email"] == target_email:
            return employee["profile_rule"]["employee_id"]