# MMI Architect Parser Alignment Patch

**Document ID:** `MMI_ARCHITECT_PARSER_ALIGNMENT_PATCH`

**Status:** §11 SIGNED 2026-06-20 by Matt Nichol. Parser implementation authorized for `scripts/mmi_architect.py` + targeted tests only.

**Amends:** `mmi/MMI_ARCHITECT_BLUEPRINT_CONTRACT.md` (§11 signed 2026-06-20; commit `6f542a4`)

**Scope:** Teach the Architect parser two BUILD CONDITIONS `CHECK:` prefixes only. Nothing else.

**Implementation:** Authorized upon §11 signature below for parser + tests only.

**Authority Domain:** Mutant Monkey Intelligence (MMI)

**Operator Authority:** Matt Nichol §11 sign-off required before parser implementation

---

## 0. Problem statement

The Architect finds `#52`'s Agent Design Contract file on disk (§11 signed at `379d0e6`) but returns `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` because two BUILD CONDITIONS use `sentinel_exact:` and `invariant_present:` prefixes the parser does not recognize.

This patch adds exactly those two prefixes to the Architect parser allowlist. It does not expand Architect authority, candidate selection, lifecycle routing, or build authorization.

---

## 1. Scope

### In scope

- Parser recognition of `sentinel_exact:` BUILD CONDITIONS.
- Parser recognition of `invariant_present:` BUILD CONDITIONS.
- Deterministic blueprint rendering for both prefixes.
- Refusal on unknown prefixes with the unknown prefix named.
- Tests proving the above and preserving read-only / no-invention behavior.

### Out of scope

- New Architect authority beyond parsing these two prefixes.
- Candidate selection or ranking.
- `#52` wrapper build authorization (separate lane).
- Scoreboard / lifecycle reconcile.
- Registry / default dispatch changes.
- Blueprint-of-Record population.
- AUTH-5 unlock.
- Push.
- Any prefix beyond `sentinel_exact:` and `invariant_present:`.

---

## 2. Locked parser semantics

### 2.1 `sentinel_exact:`

**Source form:**

```text
CHECK: sentinel_exact:<field>=<value>
```

**Checkable meaning:** `<field>` matches `<value>` exactly.

**Alternate source form (token-only):**

```text
CHECK: sentinel_exact: <token>
```

When no `=` is present, the token after `sentinel_exact:` is the exact sentinel string that must match (for example `INPUT_INSUFFICIENT_CANNOT_EXPLAIN`).

**Blueprint render (deterministic):**

```text
condition: CHECK:sentinel_exact:<field>=<value>
```

or

```text
condition: CHECK:sentinel_exact:<token>
```

(spaces normalized; original contract text preserved after prefix)

### 2.2 `invariant_present:`

**Source form:**

```text
CHECK: invariant_present:<name>
```

**Checkable meaning:** `<name>` is present (contract-declared invariant name/text).

**Blueprint render (deterministic):**

```text
condition: CHECK:invariant_present:<name>
```

### 2.3 Unknown prefixes

Any BUILD CONDITIONS line whose `CHECK:` payload starts with a prefix not in the signed allowlist must still emit:

```text
INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT
```

with a gap naming the unknown prefix:

```text
unknown_build_condition_prefix: <prefix>
```

Existing allowed prefixes from `MMI_ARCHITECT_BLUEPRINT_CONTRACT.md` §5.2 remain unchanged:

`file_exists:`, `field_present:`, `command_expect:`, `path_exact:`, `format_exact:`, `consumer_named:`

---

## 3. Must preserve

- No-invention rule.
- Selected / candidate-specific contract parsing only.
- Read-only stdout behavior; zero writes.
- No lifecycle or scoreboard mutation by the Architect tool.
- No registry / default dispatch coupling.
- No AUTH-5.
- No Blueprint-of-Record population.

---

## 4. Required tests

| # | Test |
|---|---|
| T1 | `sentinel_exact:` condition renders into a deterministic checkable blueprint line. |
| T2 | `invariant_present:` condition renders into a deterministic checkable blueprint line. |
| T3 | Live `#52` contract blueprints cleanly (exit 0, `BLUEPRINT`) instead of `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` for those prefixes alone. |
| T4 | Unknown prefix still returns `INPUTS_INSUFFICIENT_CANNOT_BLUEPRINT` and names the prefix. |
| T5 | Existing Architect tests still pass. |
| T6 | Zero writes / read-only behavior preserved. |

Target file: `tests/test_mmi_architect.py`

---

## 5. Build Authorization

§11 signature authorizes **only**:

- Parser handling for `sentinel_exact:`
- Parser handling for `invariant_present:`
- Tests proving refusal-on-unknown still works

§11 signature does **not** authorize:

- New Architect authority beyond these prefixes
- Candidate selection
- `#52` build authorization
- Lifecycle / scoreboard mutation
- Registry / default dispatch changes
- AUTH-5
- Blueprint-of-Record population
- Push

---

## §11 Sign-off

SIGNED. This signature locks §2 parser semantics and authorizes the Architect parser alignment implementation + tests only.

> Matt Nichol June 20th 2026
