"""
apex_rig.adapters.paperclip_adapter
~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

Adapter interfacing with Paperclip Company OS and AAH20/hermes-paperclip-adapter.
Manages AI agents as corporate employees with org charts, budget caps, and governance gates.
"""

from typing import Dict, List, Any, Optional
from dataclasses import dataclass, field
import time


@dataclass
class PaperclipEmployee:
    employee_id: str
    name: str
    role: str
    reports_to: Optional[str] = None
    budget_allocated_usd: float = 100.0
    budget_spent_usd: float = 0.0
    active_mandates: int = 0
    approved_for_commit: bool = True


class PaperclipAdapter:
    """
    Coordinates enterprise corporate governance and employee budgets with Paperclip Company OS.
    """

    def __init__(self, company_name: str = "Apex Autonomous Corp"):
        self.company_name = company_name
        self._employees: Dict[str, PaperclipEmployee] = {}
        self._init_default_org_chart()

    def _init_default_org_chart(self) -> None:
        self.register_employee(PaperclipEmployee(
            employee_id="emp-lead-01",
            name="Hermes Lead",
            role="Chief Software Architect",
            budget_allocated_usd=500.0,
            reports_to="Board_of_Directors",
        ))
        self.register_employee(PaperclipEmployee(
            employee_id="emp-dev-01",
            name="Claude Code Worker",
            role="Senior Systems Engineer",
            budget_allocated_usd=150.0,
            reports_to="emp-lead-01",
        ))
        self.register_employee(PaperclipEmployee(
            employee_id="emp-qa-01",
            name="Aider Auditor",
            role="Quality Assurance Engineer",
            budget_allocated_usd=50.0,
            reports_to="emp-lead-01",
        ))

    def register_employee(self, emp: PaperclipEmployee) -> None:
        self._employees[emp.employee_id] = emp

    def can_spend(self, employee_id: str, estimated_usd: float) -> bool:
        emp = self._employees.get(employee_id)
        if not emp:
            return False
        return (emp.budget_spent_usd + estimated_usd) <= emp.budget_allocated_usd

    def record_payroll_spend(self, employee_id: str, cost_usd: float) -> bool:
        emp = self._employees.get(employee_id)
        if not emp:
            return False
        emp.budget_spent_usd += cost_usd
        return True

    def requires_manager_approval(self, employee_id: str, blast_radius_files: int) -> bool:
        """Enforces managerial approval if blast radius exceeds 3 files."""
        return blast_radius_files > 3

    def get_company_ledger(self) -> Dict[str, Any]:
        total_allocated = sum(e.budget_allocated_usd for e in self._employees.values())
        total_spent = sum(e.budget_spent_usd for e in self._employees.values())
        return {
            "company_name": self.company_name,
            "headcount": len(self._employees),
            "total_budget_allocated_usd": round(total_allocated, 2),
            "total_budget_spent_usd": round(total_spent, 4),
            "budget_remaining_usd": round(total_allocated - total_spent, 4),
            "employees": [e.__dict__ for e in self._employees.values()],
        }
