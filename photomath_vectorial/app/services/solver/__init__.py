"""
Punto de entrada único del motor matemático.
La capa de API (routes.py) solo debe importar desde aquí, nunca desde
los submódulos internos directamente — esto permite refactorizar
algebra.py / calculus.py / vector_calculus.py sin romper la API.
"""

from .base import SolverError
from .algebra import solve_algebraic_equation, simplify_expression
from .calculus import solve_derivative, solve_integral
from .vector_calculus import (
    solve_gradient,
    solve_divergence,
    solve_curl,
    solve_double_integral,
    solve_triple_integral,
)

__all__ = [
    "SolverError",
    "solve_algebraic_equation",
    "simplify_expression",
    "solve_derivative",
    "solve_integral",
    "solve_gradient",
    "solve_divergence",
    "solve_curl",
    "solve_double_integral",
    "solve_triple_integral",
]
