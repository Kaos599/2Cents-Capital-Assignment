import numpy as np
import math


def future_value(pv, rate, periods):
    """FV = PV × (1 + r)^n"""
    return pv * (1 + rate) ** periods


def present_value(fv, rate, periods):
    """PV = FV / (1 + r)^n"""
    return fv / (1 + rate) ** periods


def fv_annuity(pmt, rate, periods):
    """FV = PMT × [(1 + r)^n – 1] / r"""
    if rate == 0:
        return pmt * periods
    return pmt * ((1 + rate) ** periods - 1) / rate


def pv_annuity(pmt, rate, periods):
    """PV = PMT × [1 – (1 + r)^(–n)] / r"""
    if rate == 0:
        return pmt * periods
    return pmt * (1 - (1 + rate) ** (-periods)) / rate


def nper_calculation(rate, pmt, pv, fv=0):
    """Calculate number of periods using numpy-financial logic"""
    if rate == 0:
        return -(fv + pv) / pmt
    return math.log((-rate * fv + pmt) / (rate * pv + pmt)) / math.log(1 + rate)


def rule_of_72(rate_percent):
    """Years ≈ 72 / rate%"""
    return 72 / rate_percent

