from datetime import datetime
from Freee import HumanResourse

def paid(date: str, reason: str, email: str, hr: HumanResourse):
    now = datetime.now()
    employees = hr.get_employees(year=now.year, month=now.month)["employees"]
    employee_id = get_employee_id(employees=employees, email=email)
    print(employee_id)
    work_record = hr.update_employee_work_record(
        employee_id=employee_id,
        date=date,
        note=reason,
        paid_holiday=1
    )
    return work_record

def get_employee_id(employees: list, email: str):
    for employee in employees:
        if employee["profile_rule"]["email"] is not None and employee["profile_rule"]["email"] == email:
            return employee["profile_rule"]["employee_id"]