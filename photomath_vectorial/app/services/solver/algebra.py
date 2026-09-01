"""
algebra.py
----------
Aritmética, simplificación algebraica y despeje de ecuaciones.

Contiene también `parse()`, la función de parseo seguro reutilizada por
TODOS los demás módulos (calculus.py, vector_calculus.py), por lo que
cualquier mejora aquí (nuevas funciones permitidas, notación implícita,
etc.) se propaga a todo el motor.
"""

import sympy as sp
from sympy.parsing.sympy_parser import (
    parse_expr,
    standard_transformations,
    implicit_multiplication_application,
    convert_xor,
)
from .base import SolverResult, SolverError

# Permite escribir "2x" en vez de "2*x", y "x^2" en vez de "x**2",
# que es la notación que espera un usuario que viene de una imagen/OCR.
TRANSFORMATIONS = standard_transformations + (
    implicit_multiplication_application,
    convert_xor,
)


def parse(expr_str: str, local_dict: dict = None) -> sp.Expr:
    """
    Convierte un string (texto plano u OCR) en una expresión SymPy.
    Lanza SolverError con mensaje amigable si el parseo falla, en vez de
    dejar escapar la excepción críptica de SymPy hacia la API.
    """
    try:
        return parse_expr(
            expr_str.replace("\\left", "").replace("\\right", ""),
            transformations=TRANSFORMATIONS,
            local_dict=local_dict,
            evaluate=True,
        )
    except Exception as exc:
        raise SolverError(f"No se pudo interpretar la expresión: '{expr_str}'") from exc


def solve_algebraic_equation(equation_str: str, variable: str = "x") -> dict:
    """
    Resuelve ecuaciones de la forma 'lhs = rhs'. Si no hay '=', se asume
    que es una simplificación (delega a simplify_expression).
    """
    if "=" not in equation_str:
        return simplify_expression(equation_str)

    lhs_str, rhs_str = equation_str.split("=", 1)
    var = sp.symbols(variable)
    local_dict = {variable: var}
    lhs = parse(lhs_str, local_dict)
    rhs = parse(rhs_str, local_dict)

    result = SolverResult(
        problem_type="Ecuación Algebraica",
        original_expression_latex=f"{sp.latex(lhs)} = {sp.latex(rhs)}",
    )

    result.add_step(
        title="Ecuación original",
        expr=sp.Eq(lhs, rhs),
        description="Se identifica el lado izquierdo (LHS) y derecho (RHS) de la ecuación.",
    )

    normal_form = sp.expand(lhs - rhs)
    result.add_step(
        title="Se agrupan todos los términos en un solo lado",
        expr=sp.Eq(normal_form, 0),
        description=f"Se resta el lado derecho al izquierdo: ({sp.latex(lhs)}) - ({sp.latex(rhs)}) = 0.",
    )

    solutions = sp.solve(sp.Eq(lhs, rhs), var)
    if not solutions:
        raise SolverError("No se encontraron soluciones para la ecuación dada.")

    for i, sol in enumerate(solutions, start=1):
        title = f"Solución {i} de {len(solutions)}" if len(solutions) > 1 else "Despeje de la variable"
        result.add_step(
            title=title,
            expr=sp.Eq(var, sp.simplify(sol)),
            description=f"Se despeja '{variable}' aplicando operaciones algebraicas inversas "
                        f"(suma, resta, multiplicación, radicación, etc.).",
        )

    if len(solutions) == 1:
        result.result_latex = sp.latex(sp.Eq(var, sp.simplify(solutions[0])))
    else:
        result.result_latex = r" \quad \text{o} \quad ".join(
            sp.latex(sp.Eq(var, sp.simplify(s))) for s in solutions
        )

    return result.to_response()


def simplify_expression(expr_str: str) -> dict:
    """Simplifica/expande/factoriza una expresión algebraica sin '='."""
    expr = parse(expr_str)

    result = SolverResult(
        problem_type="Simplificación Algebraica",
        original_expression_latex=sp.latex(expr),
    )

    expanded = sp.expand(expr)
    if sp.simplify(expanded - expr) == 0 and expanded != expr:
        result.add_step(
            title="Expansión de términos",
            expr=expanded,
            description="Se distribuyen productos y potencias sobre la expresión original.",
        )

    simplified = sp.simplify(expr)
    result.add_step(
        title="Reducción de términos semejantes",
        expr=simplified,
        description="Se combinan términos semejantes y se simplifican fracciones o potencias.",
    )

    factored = sp.factor(simplified)
    if factored != simplified:
        result.add_step(
            title="Forma factorizada (equivalente)",
            expr=factored,
            description="La expresión simplificada también puede escribirse de forma factorizada.",
        )

    result.result_latex = sp.latex(simplified)
    return result.to_response()
