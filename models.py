from dataclasses import dataclass

@dataclass
class Employee:
    id: int
    first_name: str
    last_name: str
    salary: float
    designation: str
