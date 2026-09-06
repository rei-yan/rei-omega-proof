#!/usr/bin/env python3
"""Weyl-Wigner phase-space representation contract for REI.

This module freezes normalization and domain metadata. It does not claim to
numerically solve arbitrary quantum systems.
"""

from __future__ import annotations

import math
from dataclasses import dataclass


SUPPORTED_CONVENTION = "standard_one_dof_2pi_hbar"


@dataclass(frozen=True)
class WeylWignerContract:
    hbar: float
    degrees_of_freedom: int = 1
    convention: str = SUPPORTED_CONVENTION
    quantum_phase_space_task: bool = True

    def validate(self) -> tuple[bool, str]:
        if not self.quantum_phase_space_task:
            return False, "DOMAIN_MISMATCH"
        if not math.isfinite(self.hbar) or self.hbar <= 0:
            return False, "INVALID_HBAR"
        if not isinstance(self.degrees_of_freedom, int) or self.degrees_of_freedom <= 0:
            return False, "INVALID_DEGREES_OF_FREEDOM"
        if self.convention != SUPPORTED_CONVENTION:
            return False, "UNFROZEN_OR_UNSUPPORTED_NORMALIZATION"
        return True, "VALID_CONTRACT"

    @property
    def inverse_prefactor(self) -> float:
        ok, reason = self.validate()
        if not ok:
            raise ValueError(reason)
        return (2.0 * math.pi * self.hbar) ** (-self.degrees_of_freedom)

    @property
    def trace_prefactor(self) -> float:
        ok, reason = self.validate()
        if not ok:
            raise ValueError(reason)
        return (2.0 * math.pi * self.hbar) ** (-self.degrees_of_freedom)

    @property
    def kernel_phase_sign(self) -> int:
        return +1

    @property
    def symbol_phase_sign(self) -> int:
        return -1


def formula_registry(contract: WeylWignerContract) -> dict[str, str | float | int]:
    ok, reason = contract.validate()
    if not ok:
        return {"status": reason}
    return {
        "status": "WEYL_WIGNER_REPRESENTATION_READY",
        "symbol_formula": "A_W(q,p)=integral dxi exp(-i p xi/hbar)<q+xi/2|A|q-xi/2>",
        "inverse_formula": "A=(2*pi*hbar)^(-n) integral dq dp A_W(q,p) Delta(q,p)",
        "trace_formula": "Tr(A B)=(2*pi*hbar)^(-n) integral dq dp A_W(q,p) B_W(q,p)",
        "kernel_formula": "Delta(q,p)=integral dxi exp(+i p xi/hbar)|q+xi/2><q-xi/2|",
        "inverse_prefactor": contract.inverse_prefactor,
        "trace_prefactor": contract.trace_prefactor,
        "symbol_phase_sign": contract.symbol_phase_sign,
        "kernel_phase_sign": contract.kernel_phase_sign,
        "authority": 0,
    }


def _sanity() -> None:
    c = WeylWignerContract(hbar=1.0, degrees_of_freedom=1)
    ok, reason = c.validate()
    assert ok and reason == "VALID_CONTRACT"
    expected = 1.0 / (2.0 * math.pi)
    assert math.isclose(c.inverse_prefactor, expected, rel_tol=1e-15)
    assert math.isclose(c.trace_prefactor, expected, rel_tol=1e-15)
    assert c.symbol_phase_sign == -1
    assert c.kernel_phase_sign == +1

    multi = WeylWignerContract(hbar=1.0, degrees_of_freedom=2)
    assert math.isclose(multi.trace_prefactor, expected**2, rel_tol=1e-15)

    wrong_domain = WeylWignerContract(hbar=1.0, quantum_phase_space_task=False)
    assert wrong_domain.validate()[1] == "DOMAIN_MISMATCH"

    bad_hbar = WeylWignerContract(hbar=0.0)
    assert bad_hbar.validate()[1] == "INVALID_HBAR"

    mixed_convention = WeylWignerContract(hbar=1.0, convention="unspecified")
    assert mixed_convention.validate()[1] == "UNFROZEN_OR_UNSUPPORTED_NORMALIZATION"

    registry = formula_registry(c)
    assert registry["authority"] == 0
    assert registry["status"] == "WEYL_WIGNER_REPRESENTATION_READY"

    print("WEYL_WIGNER_PHASE_SPACE_OPERATOR_READY")
    print("NORMALIZATION_FIREWALL_ACTIVE")
    print("REPRESENTATION_AUTHORITY_ZERO")


if __name__ == "__main__":
    _sanity()
