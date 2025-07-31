# Unit tests for the financial calculation formulas
import pytest
from src.calculators.financial_formulas import future_value, present_value, fv_annuity, pv_annuity, nper_calculation, rule_of_72


def test_future_value():
    assert future_value(1000, 0.07, 10) == pytest.approx(1967.15, 0.01)


def test_present_value():
    assert present_value(1500, 0.05, 5) == pytest.approx(1170.73, 0.01)


def test_fv_annuity():
    assert fv_annuity(100, 0.05, 12) == pytest.approx(1591.71, 0.01)


def test_pv_annuity():
    assert pv_annuity(100, 0.05, 12) == pytest.approx(886.33, 0.01)


def test_nper_calculation():
    assert nper_calculation(0.05, 100, -500) == pytest.approx(5.90, 0.01)


def test_rule_of_72():
    assert rule_of_72(9) == pytest.approx(8.0, 0.01)

