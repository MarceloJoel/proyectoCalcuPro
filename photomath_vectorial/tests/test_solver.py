"""
Tests de corrección matemática del motor.
Ejecutar con: pytest tests/ -v
"""

import pytest
from app.services import solver as S


def test_algebra_equation_linear():
    resp = S.solve_algebraic_equation("3*x + 5 = 2*x - 7")
    assert resp["status"] == "success"
    assert "x = -12" in resp["result_latex"]


def test_algebra_quadratic_has_two_solutions():
    resp = S.solve_algebraic_equation("x^2 - 5x + 6 = 0")
    assert "x = 2" in resp["result_latex"]
    assert "x = 3" in resp["result_latex"]


def test_derivative_power_rule():
    resp = S.solve_derivative("x^3", order=1)
    assert resp["result_latex"] == "3 x^{2}"


def test_integral_definite():
    resp = S.solve_integral("x^2", lower=0, upper=3)
    assert resp["result_latex"] == "9"


def test_gradient_dimensions():
    resp = S.solve_gradient("x**2*y + sin(z)")
    assert len(resp["steps"]) == 5  # 1 campo + 3 parciales + 1 vector final


def test_divergence_of_position_field_is_three():
    # div(x, y, z) = 1 + 1 + 1 = 3, resultado clásico de cálculo vectorial
    resp = S.solve_divergence("x, y, z")
    assert resp["result_latex"] == "3"


def test_curl_of_conservative_field_is_zero():
    # F = grad(f) para cualquier f implica rot(F) = 0
    resp = S.solve_curl("y*z, x*z, x*y")
    assert "0" in resp["result_latex"]
    assert resp["result_latex"].count("0") == 3


def test_curl_requires_three_components():
    with pytest.raises(S.SolverError):
        S.solve_curl("x, y")


def test_double_integral_area():
    # Integral de 1 sobre [0,2]x[0,3] = área del rectángulo = 6
    resp = S.solve_double_integral("1", (0, 2), (0, 3))
    assert resp["result_latex"] == "6"


def test_triple_integral_volume():
    # Integral de 1 sobre el cubo unitario = 1
    resp = S.solve_triple_integral("1", (0, 1), (0, 1), (0, 1))
    assert resp["result_latex"] == "1"
