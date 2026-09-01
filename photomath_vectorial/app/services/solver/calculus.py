"""
calculus.py
-----------
Cálculo diferencial e integral de una sola variable:
  - Derivadas de orden n, con identificación de la regla aplicada
    (suma, producto, potencia, cadena, funciones elementales).
  - Integrales indefinidas y definidas, con evaluación explícita
    del Teorema Fundamental del Cálculo cuando hay límites.
"""

import sympy as sp
from .base import SolverResult, SolverError
from .algebra import parse


def _describe_diff_rule(expr: sp.Expr) -> str:
    """Heurística simple para explicar en lenguaje natural qué regla se aplicó."""
    if expr.is_Add:
        return "Se aplica la regla de la suma: la derivada de una suma es la suma de las derivadas."
    if expr.is_Mul:
        return "Se aplica la regla del producto sobre los factores presentes en la expresión."
    if expr.is_Pow:
        base, exp = expr.as_base_exp()
        if base.is_Symbol:
            return f"Se aplica la regla de la potencia: d/dx[x^n] = n·x^(n-1)."
        return "Se aplica la regla de la potencia junto con la regla de la cadena."
    if expr.has(sp.sin, sp.cos, sp.tan):
        return "Se aplica la derivada de una función trigonométrica elemental."
    if expr.has(sp.exp):
        return "Se aplica la derivada de la función exponencial (y su posible regla de la cadena)."
    if expr.has(sp.log):
        return "Se aplica la derivada del logaritmo natural."
    return "Se aplican las reglas básicas de derivación."


def solve_derivative(expr_str: str, variable: str = "x", order: int = 1) -> dict:
    """Deriva una expresión respecto a `variable`, `order` veces, mostrando cada nivel."""
    var = sp.symbols(variable)
    expr = parse(expr_str, {variable: var})

    result = SolverResult(
        problem_type="Derivada",
        original_expression_latex=sp.latex(sp.Derivative(expr, (var, order))),
    )

    result.add_step(
        title="Función original",
        expr=sp.Eq(sp.Function("f")(var), expr),
        description=f"Se identifica la función a derivar respecto de la variable '{variable}'.",
    )

    current = expr
    for k in range(1, order + 1):
        derivative_raw = sp.diff(current, var)
        derivative_simplified = sp.simplify(derivative_raw)
        label = "Primera derivada" if k == 1 else f"Derivada de orden {k}"
        result.add_step(
            title=label,
            expr=sp.Eq(sp.Derivative(expr, (var, k)) if k > 1 else sp.Derivative(expr, var),
                       derivative_simplified),
            description=_describe_diff_rule(current),
        )
        current = derivative_simplified

    result.result_latex = sp.latex(current)
    return result.to_response()


def solve_integral(expr_str: str, variable: str = "x", lower=None, upper=None) -> dict:
    """
    Integra `expr_str` respecto a `variable`.
    Si `lower`/`upper` se proporcionan, calcula la integral definida
    mostrando explícitamente la evaluación en los límites.
    """
    var = sp.symbols(variable)
    expr = parse(expr_str, {variable: var})
    is_definite = lower is not None and upper is not None

    if is_definite:
        lower_val = parse(str(lower))
        upper_val = parse(str(upper))
        original_latex = sp.latex(sp.Integral(expr, (var, lower_val, upper_val)))
        problem_type = "Integral Definida"
    else:
        original_latex = sp.latex(sp.Integral(expr, var))
        problem_type = "Integral Indefinida"

    result = SolverResult(problem_type=problem_type, original_expression_latex=original_latex)

    result.add_step(
        title="Integrando",
        expr=expr,
        description="Se identifica la función a integrar respecto de la variable indicada.",
    )

    antiderivative = sp.integrate(expr, var)
    if antiderivative.has(sp.Integral):
        raise SolverError("SymPy no pudo encontrar una antiderivada en forma cerrada para esta función.")

    display_antideriv = antiderivative if is_definite else antiderivative + sp.Symbol("C")
    result.add_step(
        title="Antiderivada (función primitiva)",
        expr=sp.Eq(sp.Integral(expr, var), display_antideriv),
        description="Se calcula la función primitiva F(x) aplicando las reglas de integración "
                    "(potencia, exponencial, trigonométricas, sustitución, etc.).",
    )

    if is_definite:
        eval_upper = antiderivative.subs(var, upper_val)
        eval_lower = antiderivative.subs(var, lower_val)
        result.add_step(
            title="Evaluación con el Teorema Fundamental del Cálculo",
            expr=(
                f"\\Big[{sp.latex(antiderivative)}\\Big]_{{{sp.latex(lower_val)}}}^{{{sp.latex(upper_val)}}} "
                f"= \\left({sp.latex(eval_upper)}\\right) - \\left({sp.latex(eval_lower)}\\right)"
            ),
            description="Se evalúa la antiderivada en el límite superior y se le resta su valor "
                        "en el límite inferior.",
        )
        final = sp.simplify(eval_upper - eval_lower)
        result.result_latex = sp.latex(final)
    else:
        result.result_latex = sp.latex(antiderivative + sp.Symbol("C"))

    return result.to_response()
