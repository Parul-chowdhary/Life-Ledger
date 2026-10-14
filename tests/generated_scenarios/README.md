# Generated LifeLedger scenario corpus

This directory contains deterministic, generated domain scenario vectors used to exercise
LifeLedger's validation, authorization, lifecycle, scheduling, privacy, and API policy surfaces.
Each `scenario_*.py` module stores literal tuples; the corpus is intentionally kept separate
from production code and is not imported automatically at application startup.

Fields: `(case_id, domain, operation, input_summary, expected_policy, severity, shard)`.
These vectors are scaffolding for test expansion, not a claim that every scenario has already
been asserted by an independent test. Connect them to property-based and integration tests
before treating the corpus as test coverage.
