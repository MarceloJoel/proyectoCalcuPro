"""
base.py
--------
Estructuras compartidas por todos los sub-módulos del motor matemático.

Filosofía de diseño:
    En lugar de que cada función de resolución construya un dict a mano,
    todas usan `SolverResult`, que acumula pasos (`Step`) de forma
    incremental. Esto garantiza que TODAS las rutas de la API devuelvan
    exactamente el mismo contrato JSON, sin importar el tipo de problema.
"""

from dataclasses import dataclass, field
from typing import List, Dict, Any, Union
import sympy as sp


@dataclass
class Step:
    """Representa un paso pedagógico individual."""
    title: str
    latex: str
    description: str

    def to_dict(self) -> Dict[str, str]:
        return {
            "title": self.title,
            "latex": self.latex,
            "description": self.description,
        }


@dataclass
class SolverResult:
    """
    Acumulador de la solución completa de un problema.
    Se construye incrementalmente con `add_step()` y se serializa
    al contrato JSON final con `to_response()`.
    """
    problem_type: str
    original_expression_latex: str
    steps: List[Step] = field(default_factory=list)
    result_latex: str = ""

    def add_step(self, title: str, expr: Union[str, sp.Expr, sp.Eq], description: str) -> None:
        """
        Agrega un paso. `expr` puede ser:
          - un objeto SymPy (se convierte a LaTeX automáticamente), o
          - un string ya formateado en LaTeX (para composiciones manuales
            como fracciones de derivadas parciales con nombres simbólicos).
        """
        latex = expr if isinstance(expr, str) else sp.latex(expr)
        self.steps.append(Step(title=title, latex=latex, description=description))

    def to_response(self) -> Dict[str, Any]:
        return {
            "status": "success",
            "problem_type": self.problem_type,
            "original_expression_latex": self.original_expression_latex,
            "steps": [s.to_dict() for s in self.steps],
            "result_latex": self.result_latex,
        }


class SolverError(Exception):
    """
    Excepción de dominio para errores de parseo o de resolución matemática.
    La capa de API (routes.py) la captura y la traduce al contrato de error:
        {"status": "error", "message": "..."}
    """
    pass
