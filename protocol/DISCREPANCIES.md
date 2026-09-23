# Reconciliation and unresolved points

| Finding | Treatment in this handoff |
|---|---|
| v0.8 implementation appendix opens with “Normative ... v0.3” | Treat as historical blueprint, subordinate to amended main text. Preserve source verbatim. |
| Appendix continuation enum/regimes omit I0b | Require I0, I0b, I1, I2 in every new implementation contract. |
| Appendix t0 outputs lack explicit conditional backup/pool expansion artifacts | Require conditional effects, CoAx reference receipt, power/equivalence analysis and pool-expansion receipt. |
| Freeze-register caption says v0.6; main text includes v0.7 C2C extension | v0.6 rules retained, C2C separate optional extension; v0.8 layout-only. |
| Compute text still refers to K=8 | Follow later explicit precision rule; K remains unset until simulation. |
| “B0” also names a mask-integrity pilot | Use distinct artifact keys mask_integrity and conditional_backup_state. This is naming hygiene, not protocol change. |
| Gate D says <10%; prose labels >10% ambiguous | Exactly 10% cannot pass. Pre-freeze non-pass label at the boundary; do not silently change inequality. |
| Appendix evaluator PASS/FAIL enum cannot express missing evidence | Proposed implementation envelope adds validation_status before evaluation; incomplete inputs do not run the scientific evaluator. |
| Weak/strong backup cutoffs, CoAx benchmark tolerance, pool sizes and paired-power estimator are not completely specified | Explicit open decisions; block corresponding scientific claims. |
| Pilot appendix may describe earlier internal runs | Preserve as reported history, not independently audited run evidence. |
| “M0–M3 without GPU” in supplied chat | Engineering contracts/fixtures can run locally; real 8B replication/t0 audit needs actual model execution and a measured resource plan. |
| “Compute only after external criticism” in supplied chat | Distinguish low-cost engineering and empirical P1/P2 from main adaptation. Paper requires external technical review before full-adaptation freeze, not a blanket ban on all prior compute. |

This package records an implementation interpretation. Any conflict that could change an experimental outcome remains a freeze decision, not an AI-approved correction. External critique and Article 201 are subsequent activities; no outreach is sent.
