"""
classifier.py
-------------
Clasificador ligero basado en reglas/keywords para el endpoint genérico
`/api/v1/solve`, que recibe texto "crudo" (posiblemente proveniente de OCR)
y debe decidir a qué módulo del motor enrutarlo.

NOTA DE PRODUCCIÓN:
    Esta heurística es suficiente para un MVP. En una v2, esto se
    reemplazaría por (a) un modelo de clasificación de texto entrenado
    sobre miles de ejercicios etiquetados, o (b) delegar la clasificación
    al mismo modelo de visión (GPT-4o/Gemini) que hace el OCR, pidiéndole
    que devuelva el tipo de problema junto con el LaTeX detectado.
"""

from enum import Enum


class ProblemType(str, Enum):
    GRADIENT = "gradient"
    DIVERGENCE = "divergence"
    CURL = "curl"
    DOUBLE_INTEGRAL = "double_integral"
    TRIPLE_INTEGRAL = "triple_integral"
    DERIVATIVE = "derivative"
    INTEGRAL = "integral"
    ALGEBRA_EQUATION = "algebra_equation"
    ALGEBRA_SIMPLIFY = "algebra_simplify"
    UNKNOWN = "unknown"


# Orden importa: los patrones más específicos deben evaluarse primero
# (p. ej. "integral doble" antes que el genérico "integral").
_KEYWORD_MAP: dict[ProblemType, list[str]] = {
    ProblemType.GRADIENT: ["\\nabla f", "grad(", "gradiente", "grad "],
    ProblemType.CURL: ["\\nabla \\times", "rot(", "curl(", "rotacional"],
    ProblemType.DIVERGENCE: ["\\nabla \\cdot", "div(", "divergencia"],
    ProblemType.DOUBLE_INTEGRAL: ["\\iint", "integral doble", "double integral"],
    ProblemType.TRIPLE_INTEGRAL: ["\\iiint", "integral triple", "triple integral"],
    ProblemType.DERIVATIVE: ["\\frac{d}{dx}", "d/dx", "derivada", "derivative", "diff("],
    ProblemType.INTEGRAL: ["\\int", "integral(", "integral "],
}


import re

# Patrones para extraer el argumento "limpio" de un operador vectorial,
# ej. de "\nabla \cdot (x*y, y*z, x*z)" extraer "x*y, y*z, x*z".
_OPERATOR_PATTERNS: dict[ProblemType, list[str]] = {
    ProblemType.DIVERGENCE: [r"\\nabla\s*\\cdot\s*\(?(.*?)\)?$", r"div\((.*)\)"],
    ProblemType.CURL: [r"\\nabla\s*\\times\s*\(?(.*?)\)?$", r"(?:rot|curl)\((.*)\)"],
    ProblemType.GRADIENT: [r"\\nabla\s*(.*)$", r"grad\((.*)\)"],
    ProblemType.DERIVATIVE: [r"\\frac\{d\}\{d\s*\w+\}\s*(.*)$", r"d/d\w+\s*\(?(.*?)\)?$", r"diff\((.*?)(?:,.*)?\)"],
    ProblemType.INTEGRAL: [r"\\int\s*(.*?)\s*\\,?\s*d\w+$", r"integral\((.*?)(?:,.*)?\)"],
}


def extract_argument(input_text: str, problem_type: ProblemType) -> str:
    """
    Si el texto trae el operador incluido (\\nabla \\cdot, div(...), etc.),
    extrae solo el argumento matemático que el solver realmente necesita
    parsear con SymPy. Si no hay coincidencia, devuelve el texto tal cual.
    """
    patterns = _OPERATOR_PATTERNS.get(problem_type, [])
    for pattern in patterns:
        match = re.search(pattern, input_text, flags=re.IGNORECASE)
        if match:
            arg = match.group(1).strip()
            if arg.startswith("(") and arg.endswith(")"):
                arg = arg[1:-1].strip()
            if arg:
                return arg
    return input_text


def classify(input_text: str) -> ProblemType:
    """Devuelve el ProblemType más probable a partir de palabras clave / notación LaTeX."""
    text = input_text.lower()

    for problem_type, keywords in _KEYWORD_MAP.items():
        if any(kw.lower() in text for kw in keywords):
            return problem_type

    if "=" in input_text:
        return ProblemType.ALGEBRA_EQUATION

    # Fallback razonable: si tiene un solo término/expresión, es simplificación.
    return ProblemType.ALGEBRA_SIMPLIFY
