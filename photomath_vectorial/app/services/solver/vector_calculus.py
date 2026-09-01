"""
vector_calculus.py
-------------------
Núcleo diferenciador de esta app frente a Photomath: operadores del
cálculo vectorial (nabla) e integrales múltiples iteradas.

Convenciones:
  - Un campo escalar f(x, y, z) se recibe como un string: "x**2*y + z".
  - Un campo vectorial F = (P, Q, R) se recibe como lista de strings
    o como un string separado por comas: "y*z, x*z, x*y".
  - El rotacional (curl) solo está definido en R^3.
"""

import sympy as sp
from typing import Sequence, Union
from .base import SolverResult, SolverError
from .algebra import parse

DEFAULT_VARS_3D = ("x", "y", "z")


def _make_symbols(var_names: Sequence[str]):
    return sp.symbols(" ".join(var_names))


def _parse_vector_field(components: Union[str, Sequence[str]], var_names: Sequence[str]):
    symbols = _make_symbols(var_names)
    if len(var_names) == 1:
        symbols = (symbols,)
    local_dict = dict(zip(var_names, symbols))

    parts = [p.strip() for p in components.split(",")] if isinstance(components, str) else list(components)
    F = [parse(p, local_dict) for p in parts]
    return symbols, F


def _vector_latex(components: Sequence[sp.Expr]) -> str:
    rows = r" \\ ".join(sp.latex(c) for c in components)
    return r"\begin{pmatrix}" + rows + r"\end{pmatrix}"


# ---------------------------------------------------------------------------
# 1. GRADIENTE  ∇f
# ---------------------------------------------------------------------------
def solve_gradient(scalar_field_str: str, var_names: Sequence[str] = DEFAULT_VARS_3D) -> dict:
    symbols = _make_symbols(var_names)
    local_dict = dict(zip(var_names, symbols))
    f = parse(scalar_field_str, local_dict)

    result = SolverResult(
        problem_type="Gradiente de un Campo Escalar",
        original_expression_latex=f"\\nabla f \\quad \\text{{donde}} \\quad f({', '.join(var_names)}) = {sp.latex(f)}",
    )

    result.add_step(
        title="Campo escalar dado",
        expr=sp.Eq(sp.Symbol("f"), f),
        description=f"Se define el campo escalar f en función de {', '.join(var_names)}.",
    )

    components = []
    for v in symbols:
        partial = sp.simplify(sp.diff(f, v))
        result.add_step(
            title=f"Derivada parcial respecto de {v}",
            expr=f"\\frac{{\\partial f}}{{\\partial {sp.latex(v)}}} = {sp.latex(partial)}",
            description=f"Se deriva f manteniendo constantes las demás variables, respecto a {v}.",
        )
        components.append(partial)

    grad_latex = _vector_latex(components)
    result.add_step(
        title="Vector gradiente",
        expr=f"\\nabla f = {grad_latex}",
        description="El gradiente se forma agrupando las derivadas parciales como componentes "
                    "de un vector. Apunta en la dirección de máximo crecimiento de f.",
    )

    result.result_latex = f"\\nabla f = {grad_latex}"
    return result.to_response()


# ---------------------------------------------------------------------------
# 2. DIVERGENCIA  ∇ · F
# ---------------------------------------------------------------------------
def solve_divergence(field_components: Union[str, Sequence[str]],
                      var_names: Sequence[str] = DEFAULT_VARS_3D) -> dict:
    symbols, F = _parse_vector_field(field_components, var_names)
    if len(F) != len(symbols):
        raise SolverError(
            f"El campo vectorial debe tener {len(symbols)} componentes para coincidir con "
            f"las variables {var_names}, pero se recibieron {len(F)}."
        )

    labels = ["P", "Q", "R", "S"][: len(F)]
    F_latex = _vector_latex(F)

    result = SolverResult(
        problem_type="Divergencia de un Campo Vectorial",
        original_expression_latex=f"\\nabla \\cdot \\mathbf{{F}} \\quad \\text{{donde}} \\quad "
                                   f"\\mathbf{{F}} = {F_latex}",
    )

    result.add_step(
        title="Campo vectorial dado",
        expr=f"\\mathbf{{F}} = ({', '.join(labels)}) = {F_latex}",
        description=f"Se identifican las componentes {', '.join(labels)} del campo, cada una "
                    f"función de {', '.join(var_names)}.",
    )

    terms = []
    for comp, v, label in zip(F, symbols, labels):
        partial = sp.simplify(sp.diff(comp, v))
        result.add_step(
            title=f"Derivada parcial de {label} respecto de {v}",
            expr=f"\\frac{{\\partial {label}}}{{\\partial {sp.latex(v)}}} = {sp.latex(partial)}",
            description=f"Se deriva la componente {label} = {sp.latex(comp)} únicamente "
                        f"respecto a su variable correspondiente, {v}.",
        )
        terms.append(partial)

    divergence = sp.simplify(sum(terms))
    sum_expr = " + ".join(
        f"\\frac{{\\partial {label}}}{{\\partial {sp.latex(v)}}}" for label, v in zip(labels, symbols)
    )
    result.add_step(
        title="Suma de las derivadas parciales",
        expr=f"\\nabla \\cdot \\mathbf{{F}} = {sum_expr} = {sp.latex(divergence)}",
        description="La divergencia es un escalar: la suma de las derivadas parciales de cada "
                    "componente respecto a su propia variable. Mide la 'expansión' del campo en un punto.",
    )

    result.result_latex = sp.latex(divergence)
    return result.to_response()


# ---------------------------------------------------------------------------
# 3. ROTACIONAL  ∇ × F   (solo R^3)
# ---------------------------------------------------------------------------
def solve_curl(field_components: Union[str, Sequence[str]],
               var_names: Sequence[str] = ("x", "y", "z")) -> dict:
    if len(var_names) != 3:
        raise SolverError("El rotacional solo está definido para campos vectoriales en 3 dimensiones (x, y, z).")

    symbols, F = _parse_vector_field(field_components, var_names)
    if len(F) != 3:
        raise SolverError("El rotacional requiere un campo vectorial con exactamente 3 componentes (P, Q, R).")

    x, y, z = symbols
    P, Q, R = F
    F_latex = _vector_latex(F)

    result = SolverResult(
        problem_type="Rotacional de un Campo Vectorial",
        original_expression_latex=f"\\nabla \\times \\mathbf{{F}} \\quad \\text{{donde}} \\quad "
                                   f"\\mathbf{{F}} = {F_latex}",
    )

    result.add_step(
        title="Campo vectorial dado",
        expr=f"\\mathbf{{F}} = (P, Q, R) = {F_latex}",
        description="Se identifican las componentes P, Q, R del campo vectorial en R³.",
    )

    result.add_step(
        title="Determinante simbólico del rotacional",
        expr=(
            r"\nabla \times \mathbf{F} = \begin{vmatrix} "
            r"\mathbf{i} & \mathbf{j} & \mathbf{k} \\ "
            r"\partial/\partial x & \partial/\partial y & \partial/\partial z \\ "
            f"{sp.latex(P)} & {sp.latex(Q)} & {sp.latex(R)}"
            r" \end{vmatrix}"
        ),
        description="El rotacional se calcula como el 'determinante simbólico' de esta matriz, "
                    "expandiendo por la primera fila.",
    )

    dRdy, dQdz = sp.diff(R, y), sp.diff(Q, z)
    i_comp = sp.simplify(dRdy - dQdz)
    result.add_step(
        title="Componente i (eje x)",
        expr=f"\\frac{{\\partial R}}{{\\partial y}} - \\frac{{\\partial Q}}{{\\partial z}} "
             f"= ({sp.latex(dRdy)}) - ({sp.latex(dQdz)}) = {sp.latex(i_comp)}",
        description="Se calcula la componente i: ∂R/∂y − ∂Q/∂z.",
    )

    dPdz, dRdx = sp.diff(P, z), sp.diff(R, x)
    j_comp = sp.simplify(dPdz - dRdx)
    result.add_step(
        title="Componente j (eje y)",
        expr=f"\\frac{{\\partial P}}{{\\partial z}} - \\frac{{\\partial R}}{{\\partial x}} "
             f"= ({sp.latex(dPdz)}) - ({sp.latex(dRdx)}) = {sp.latex(j_comp)}",
        description="Se calcula la componente j: ∂P/∂z − ∂R/∂x (nótese el signo negativo "
                    "frente a este término en la expansión del determinante).",
    )

    dQdx, dPdy = sp.diff(Q, x), sp.diff(P, y)
    k_comp = sp.simplify(dQdx - dPdy)
    result.add_step(
        title="Componente k (eje z)",
        expr=f"\\frac{{\\partial Q}}{{\\partial x}} - \\frac{{\\partial P}}{{\\partial y}} "
             f"= ({sp.latex(dQdx)}) - ({sp.latex(dPdy)}) = {sp.latex(k_comp)}",
        description="Se calcula la componente k: ∂Q/∂x − ∂P/∂y.",
    )

    curl_latex = _vector_latex([i_comp, j_comp, k_comp])
    result.add_step(
        title="Vector rotacional resultante",
        expr=f"\\nabla \\times \\mathbf{{F}} = {curl_latex}",
        description="Se agrupan las tres componentes. El rotacional mide la tendencia del "
                    "campo a 'rotar' alrededor de un punto.",
    )

    result.result_latex = f"\\nabla \\times \\mathbf{{F}} = {curl_latex}"
    return result.to_response()


# ---------------------------------------------------------------------------
# 4. INTEGRALES MÚLTIPLES ITERADAS
# ---------------------------------------------------------------------------
def solve_double_integral(expr_str: str, x_range, y_range,
                           var_names: Sequence[str] = ("x", "y")) -> dict:
    x_name, y_name = var_names
    x, y = sp.symbols(f"{x_name} {y_name}")
    local_dict = {x_name: x, y_name: y}
    expr = parse(expr_str, local_dict)

    x0, x1 = (parse(str(v), local_dict) for v in x_range)
    y0, y1 = (parse(str(v), local_dict) for v in y_range)

    original_latex = (
        f"\\int_{{{sp.latex(x0)}}}^{{{sp.latex(x1)}}} \\int_{{{sp.latex(y0)}}}^{{{sp.latex(y1)}}} "
        f"{sp.latex(expr)} \\; d{y_name} \\, d{x_name}"
    )

    result = SolverResult(problem_type="Integral Doble Iterada", original_expression_latex=original_latex)

    result.add_step(
        title="Integral iterada planteada",
        expr=original_latex,
        description=f"Se resuelve de adentro hacia afuera: primero respecto de {y_name} "
                    f"(tratando {x_name} como constante), y luego respecto de {x_name}.",
    )

    inner = sp.simplify(sp.integrate(expr, (y, y0, y1)))
    result.add_step(
        title=f"Integración interna respecto de {y_name}",
        expr=f"\\int_{{{sp.latex(y0)}}}^{{{sp.latex(y1)}}} {sp.latex(expr)} \\; d{y_name} = {sp.latex(inner)}",
        description=f"Se integra respecto a {y_name} y se evalúa en sus límites, obteniendo una "
                    f"función que depende únicamente de {x_name}.",
    )

    outer = sp.simplify(sp.integrate(inner, (x, x0, x1)))
    result.add_step(
        title=f"Integración externa respecto de {x_name}",
        expr=f"\\int_{{{sp.latex(x0)}}}^{{{sp.latex(x1)}}} \\left({sp.latex(inner)}\\right) d{x_name} = {sp.latex(outer)}",
        description=f"Se integra el resultado anterior respecto de {x_name} entre sus límites, "
                    "obteniendo el valor numérico/simbólico final.",
    )

    result.result_latex = sp.latex(outer)
    return result.to_response()


def solve_triple_integral(expr_str: str, x_range, y_range, z_range,
                           var_names: Sequence[str] = ("x", "y", "z")) -> dict:
    x_name, y_name, z_name = var_names
    x, y, z = sp.symbols(f"{x_name} {y_name} {z_name}")
    local_dict = {x_name: x, y_name: y, z_name: z}
    expr = parse(expr_str, local_dict)

    x0, x1 = (parse(str(v), local_dict) for v in x_range)
    y0, y1 = (parse(str(v), local_dict) for v in y_range)
    z0, z1 = (parse(str(v), local_dict) for v in z_range)

    original_latex = (
        f"\\int_{{{sp.latex(x0)}}}^{{{sp.latex(x1)}}} \\int_{{{sp.latex(y0)}}}^{{{sp.latex(y1)}}} "
        f"\\int_{{{sp.latex(z0)}}}^{{{sp.latex(z1)}}} {sp.latex(expr)} \\; d{z_name} \\, d{y_name} \\, d{x_name}"
    )

    result = SolverResult(problem_type="Integral Triple Iterada", original_expression_latex=original_latex)

    result.add_step(
        title="Integral iterada planteada",
        expr=original_latex,
        description=f"Se integra en el orden: primero {z_name}, luego {y_name}, y finalmente {x_name}.",
    )

    step1 = sp.simplify(sp.integrate(expr, (z, z0, z1)))
    result.add_step(
        title=f"Integración respecto de {z_name}",
        expr=f"\\int_{{{sp.latex(z0)}}}^{{{sp.latex(z1)}}} {sp.latex(expr)} \\; d{z_name} = {sp.latex(step1)}",
        description=f"Se integra respecto de {z_name}, tratando {x_name} e {y_name} como constantes.",
    )

    step2 = sp.simplify(sp.integrate(step1, (y, y0, y1)))
    result.add_step(
        title=f"Integración respecto de {y_name}",
        expr=f"\\int_{{{sp.latex(y0)}}}^{{{sp.latex(y1)}}} \\left({sp.latex(step1)}\\right) d{y_name} = {sp.latex(step2)}",
        description=f"Se integra el resultado anterior respecto de {y_name}.",
    )

    step3 = sp.simplify(sp.integrate(step2, (x, x0, x1)))
    result.add_step(
        title=f"Integración respecto de {x_name}",
        expr=f"\\int_{{{sp.latex(x0)}}}^{{{sp.latex(x1)}}} \\left({sp.latex(step2)}\\right) d{x_name} = {sp.latex(step3)}",
        description=f"Se integra el resultado anterior respecto de {x_name}, obteniendo el valor final.",
    )

    result.result_latex = sp.latex(step3)
    return result.to_response()
