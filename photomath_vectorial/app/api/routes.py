"""
routes.py
---------
Capa de API. Cada endpoint es un adaptador delgado: valida el input con
Pydantic, delega el cómputo real a `app.services.solver`, y traduce
`SolverError` a una respuesta de error estandarizada. NO contiene lógica
matemática (esa vive exclusivamente en services/solver/).
"""

# pyrefly: ignore [missing-import]
from fastapi import APIRouter, HTTPException

from app.models.schemas import (
    AlgebraRequest,
    DerivativeRequest,
    IntegralRequest,
    GradientRequest,
    VectorFieldRequest,
    DoubleIntegralRequest,
    TripleIntegralRequest,
    TextProblemRequest,
    OcrRequest,
    SolutionResponse,
    ErrorResponse,
)
from app.services import solver as S
from app.services.classifier import classify, extract_argument, ProblemType
from app.services.ocr_service import image_to_latex, OcrError

router = APIRouter()


def _run_solver(fn, *args, **kwargs) -> dict:
    """Envoltura común: convierte SolverError en HTTP 422 con el contrato de error."""
    try:
        return fn(*args, **kwargs)
    except S.SolverError as exc:
        raise HTTPException(status_code=422, detail=ErrorResponse(message=str(exc)).model_dump())
    except Exception as exc:  # salvaguarda: nunca exponer un stack trace de SymPy al cliente
        raise HTTPException(
            status_code=500,
            detail=ErrorResponse(message=f"Error interno al resolver el problema: {exc}").model_dump(),
        )


# ---------------------------------------------------------------------------
# Álgebra
# ---------------------------------------------------------------------------
@router.post("/solve/algebra", response_model=SolutionResponse)
def solve_algebra(payload: AlgebraRequest):
    return _run_solver(S.solve_algebraic_equation, payload.expression, payload.variable)


# ---------------------------------------------------------------------------
# Cálculo univariable
# ---------------------------------------------------------------------------
@router.post("/solve/derivative", response_model=SolutionResponse)
def solve_derivative(payload: DerivativeRequest):
    return _run_solver(S.solve_derivative, payload.expression, payload.variable, payload.order)


@router.post("/solve/integral", response_model=SolutionResponse)
def solve_integral(payload: IntegralRequest):
    return _run_solver(S.solve_integral, payload.expression, payload.variable, payload.lower, payload.upper)


# ---------------------------------------------------------------------------
# Cálculo vectorial
# ---------------------------------------------------------------------------
@router.post("/solve/vector/gradient", response_model=SolutionResponse)
def solve_gradient(payload: GradientRequest):
    return _run_solver(S.solve_gradient, payload.expression, tuple(payload.variables))


@router.post("/solve/vector/divergence", response_model=SolutionResponse)
def solve_divergence(payload: VectorFieldRequest):
    return _run_solver(S.solve_divergence, payload.components, tuple(payload.variables))


@router.post("/solve/vector/curl", response_model=SolutionResponse)
def solve_curl(payload: VectorFieldRequest):
    return _run_solver(S.solve_curl, payload.components, tuple(payload.variables))


@router.post("/solve/vector/double-integral", response_model=SolutionResponse)
def solve_double_integral(payload: DoubleIntegralRequest):
    return _run_solver(
        S.solve_double_integral,
        payload.expression,
        tuple(payload.x_range),
        tuple(payload.y_range),
        tuple(payload.variables),
    )


@router.post("/solve/vector/triple-integral", response_model=SolutionResponse)
def solve_triple_integral(payload: TripleIntegralRequest):
    return _run_solver(
        S.solve_triple_integral,
        payload.expression,
        tuple(payload.x_range),
        tuple(payload.y_range),
        tuple(payload.z_range),
        tuple(payload.variables),
    )


# ---------------------------------------------------------------------------
# Endpoint genérico: clasifica automáticamente y enruta (usado por texto libre)
# ---------------------------------------------------------------------------
@router.post("/solve", response_model=SolutionResponse)
def solve_generic(payload: TextProblemRequest):
    problem_type = classify(payload.expression)
    argument = extract_argument(payload.expression, problem_type)

    dispatch = {
        ProblemType.ALGEBRA_EQUATION: lambda: S.solve_algebraic_equation(argument, payload.variable),
        ProblemType.ALGEBRA_SIMPLIFY: lambda: S.simplify_expression(argument),
        ProblemType.DERIVATIVE: lambda: S.solve_derivative(argument, payload.variable),
        ProblemType.INTEGRAL: lambda: S.solve_integral(argument, payload.variable),
        ProblemType.GRADIENT: lambda: S.solve_gradient(argument),
        ProblemType.DIVERGENCE: lambda: S.solve_divergence(argument),
        ProblemType.CURL: lambda: S.solve_curl(argument),
    }

    handler = dispatch.get(problem_type)
    if handler is None:
        raise HTTPException(
            status_code=422,
            detail=ErrorResponse(
                message=f"No se pudo clasificar el problema (tipo detectado: '{problem_type.value}'). "
                        f"Intenta usar un endpoint especializado, ej. /solve/vector/double-integral."
            ).model_dump(),
        )

    return _run_solver(handler)


# ---------------------------------------------------------------------------
# OCR: imagen -> LaTeX (no resuelve, solo transcribe; el cliente reenvía
# el LaTeX resultante a /solve o a un endpoint especializado)
# ---------------------------------------------------------------------------
@router.post("/ocr")
async def ocr_to_latex(payload: OcrRequest):
    try:
        latex = await image_to_latex(payload.image_base64, payload.mime_type)
    except OcrError as exc:
        raise HTTPException(status_code=422, detail=ErrorResponse(message=str(exc)).model_dump())
    return {"status": "success", "latex": latex}
