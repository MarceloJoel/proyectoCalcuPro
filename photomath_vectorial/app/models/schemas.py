"""
schemas.py
----------
Contratos Pydantic. Estos modelos son la "fuente de verdad" del formato
JSON que consumirá la app móvil (Flutter/React Native) para renderizar
con KaTeX/MathJax.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Union, Literal


class StepSchema(BaseModel):
    title: str = Field(..., description="Título corto del paso, ej. 'Regla del producto'")
    latex: str = Field(..., description="Fórmula u operación de este paso, en LaTeX")
    description: str = Field(..., description="Explicación en lenguaje natural del paso")


class SolutionResponse(BaseModel):
    status: Literal["success"] = "success"
    problem_type: str
    original_expression_latex: str
    steps: List[StepSchema]
    result_latex: str


class ErrorResponse(BaseModel):
    status: Literal["error"] = "error"
    message: str


# ---------------------------------------------------------------------------
# Payloads de entrada (request bodies)
# ---------------------------------------------------------------------------

class TextProblemRequest(BaseModel):
    """Entrada genérica de texto, usada por el endpoint /solve (con clasificador automático)."""
    expression: str = Field(..., examples=["\\nabla \\times (y, -x, z)"])
    variable: Optional[str] = "x"


class AlgebraRequest(BaseModel):
    expression: str = Field(..., examples=["3x + 5 = 2x - 7"])
    variable: Optional[str] = "x"


class DerivativeRequest(BaseModel):
    expression: str = Field(..., examples=["x^2 * sin(x)"])
    variable: str = "x"
    order: int = Field(1, ge=1, le=5)


class IntegralRequest(BaseModel):
    expression: str = Field(..., examples=["3x^2 + 2x"])
    variable: str = "x"
    lower: Optional[Union[str, float]] = None
    upper: Optional[Union[str, float]] = None


class GradientRequest(BaseModel):
    expression: str = Field(..., examples=["x^2*y + sin(z)"])
    variables: List[str] = ["x", "y", "z"]


class VectorFieldRequest(BaseModel):
    """Usado por divergencia y rotacional. Componentes separadas por coma: 'P, Q, R'."""
    components: str = Field(..., examples=["y*z, x*z, x*y"])
    variables: List[str] = ["x", "y", "z"]


class DoubleIntegralRequest(BaseModel):
    expression: str = Field(..., examples=["x*y"])
    x_range: List[Union[str, float]] = Field(..., min_length=2, max_length=2)
    y_range: List[Union[str, float]] = Field(..., min_length=2, max_length=2)
    variables: List[str] = ["x", "y"]


class TripleIntegralRequest(BaseModel):
    expression: str = Field(..., examples=["x*y*z"])
    x_range: List[Union[str, float]] = Field(..., min_length=2, max_length=2)
    y_range: List[Union[str, float]] = Field(..., min_length=2, max_length=2)
    z_range: List[Union[str, float]] = Field(..., min_length=2, max_length=2)
    variables: List[str] = ["x", "y", "z"]


class OcrRequest(BaseModel):
    """Imagen codificada en base64, enviada desde la app móvil tras capturar la foto."""
    image_base64: str
    mime_type: str = "image/jpeg"
