# Architecture Decision Records (ADRs)

## ADR-001: Layered Architecture

**Status**: Accepted  
**Context**: We need clear separation without over-engineering.  
**Decision**: Use classic layers – API → Service → Repository → DB/Client.  
**Consequences**: Easy to understand, matches the developer’s preferred style, simple to test.

## ADR-002: Single PPGClient for Real + Mock

**Status**: Accepted  
**Context**: Must work with both real Jibit and local mock.  
**Decision**: One `PPGClient` class. Target is controlled only by `PPG_BASE_URL` + credentials.  
**Consequences**: Zero code change to switch environments. Mock must implement the same HTTP contract.

## ADR-003: SQLite for Merchant

**Status**: Accepted  
**Context**: Demo project, zero ops overhead preferred.  
**Decision**: aiosqlite + SQLAlchemy 2.0.  
**Consequences**: Easy local run. Can later swap to PostgreSQL by changing `DATABASE_URL` only.

## ADR-004: Alpine.js + Jinja2 for Dashboard

**Status**: Accepted  
**Context**: Need a usable UI without frontend complexity.  
**Decision**: Server-rendered Jinja2 templates + Alpine.js from CDN.  
**Consequences**: No build step, very small footprint, still interactive enough for the demo.

## ADR-005: In-memory Store for Mock PPG

**Status**: Accepted  
**Context**: Mock only needs to live for the duration of a demo session.  
**Decision**: Simple Python dict / list. No database.  
**Consequences**: Fast to implement, state is lost on restart (acceptable).

## ADR-006: Local Copy of Purchase State

**Status**: Accepted  
**Context**: Dashboard must work even if PPG is temporarily unreachable.  
**Decision**: Persist every purchase locally and update it from callbacks + verify/reverse results.  
**Consequences**: Slight duplication of state, but much better UX and resilience.

## ADR-007: No Authentication on Merchant Dashboard

**Status**: Accepted  
**Context**: This is a technical demonstration, not a production multi-user system.  
**Decision**: Open dashboard.  
**Consequences**: Simpler code. Clearly documented as out of scope for production.
