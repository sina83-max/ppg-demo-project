"""Mock Jibit PPG v3 – behavioral mock of the real gateway.

Same HTTP contract as the real API (docs/api-contracts.md section 1) so the
merchant works against it with zero code changes (ADR-002).
State is kept in memory only (ADR-005).
"""
