/-
REI-Ω G2γ Critical Invariant Kernel
Target toolchain: Lean 4.32.2

Scope: the Boolean execution-gate kernel only.
This file does not claim to formally verify the full REI architecture.
-/

def execGate
    (authorized constitutionOK recoveryReady humanVeto scoreOK : Bool) : Bool :=
  authorized &&
  constitutionOK &&
  recoveryReady &&
  (!humanVeto) &&
  scoreOK

theorem authorization_veto
    (constitutionOK recoveryReady humanVeto scoreOK : Bool) :
    execGate false constitutionOK recoveryReady humanVeto scoreOK = false := by
  simp [execGate]

theorem constitution_veto
    (authorized recoveryReady humanVeto scoreOK : Bool) :
    execGate authorized false recoveryReady humanVeto scoreOK = false := by
  cases authorized <;> simp [execGate]

theorem recovery_veto
    (authorized constitutionOK humanVeto scoreOK : Bool) :
    execGate authorized constitutionOK false humanVeto scoreOK = false := by
  cases authorized <;>
  cases constitutionOK <;>
  simp [execGate]

theorem human_veto
    (authorized constitutionOK recoveryReady scoreOK : Bool) :
    execGate authorized constitutionOK recoveryReady true scoreOK = false := by
  cases authorized <;>
  cases constitutionOK <;>
  cases recoveryReady <;>
  simp [execGate]

theorem score_cannot_override_authorization_veto
    (constitutionOK recoveryReady humanVeto : Bool) :
    execGate false constitutionOK recoveryReady humanVeto true = false := by
  simp [execGate]

theorem score_cannot_override_constitution_veto
    (authorized recoveryReady humanVeto : Bool) :
    execGate authorized false recoveryReady humanVeto true = false := by
  cases authorized <;> simp [execGate]

theorem score_cannot_override_recovery_veto
    (authorized constitutionOK humanVeto : Bool) :
    execGate authorized constitutionOK false humanVeto true = false := by
  cases authorized <;>
  cases constitutionOK <;>
  simp [execGate]

theorem score_cannot_override_human_veto
    (authorized constitutionOK recoveryReady : Bool) :
    execGate authorized constitutionOK recoveryReady true true = false := by
  cases authorized <;>
  cases constitutionOK <;>
  cases recoveryReady <;>
  simp [execGate]

theorem all_hard_gates_required
    (authorized constitutionOK recoveryReady humanVeto scoreOK : Bool)
    (h : execGate authorized constitutionOK recoveryReady humanVeto scoreOK = true) :
    authorized = true ∧
    constitutionOK = true ∧
    recoveryReady = true ∧
    humanVeto = false ∧
    scoreOK = true := by
  cases authorized <;>
  cases constitutionOK <;>
  cases recoveryReady <;>
  cases humanVeto <;>
  cases scoreOK <;>
  simp [execGate] at h ⊢
