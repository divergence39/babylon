# ADR-007: Adoption of Testcontainers and Polyfactory for Integration Testing

## Status
Accepted

## Context
To ensure the reliability of the persistence layer, integration tests must execute against a real PostgreSQL instance. The initial approach was for the test suite to orchestrate an ephemeral database by invoking docker-compose via Python's subprocess module. While functional, this approach proved brittle: it lacked programmatic control over the container lifecycle, relied on static port bindings (which can cause collisions in parallel CI pipelines), and made error handling difficult. Furthermore, the test data factories relied on hardcoded strings and UUIDs, making the tests rigid and vulnerable to overfitting. A robust, programmatic approach to both infrastructure orchestration and data mocking is required.

## Considered Options
### Container Orchestration
1. **subprocess + docker-compose**: The original approach. Simple to conceptualize but brittle, prone to zombie containers, and difficult to debug if the Docker daemon fails to respond.
2. **pytest-docker**: A pytest plugin that wraps docker-compose. It improves lifecycle management but still relies on external YAML files and static port bindings, limiting parallel execution capabilities.
3. **testcontainers-python**: A library that provides programmatic, API-driven control over Docker containers directly within Python. It dynamically binds ports and handles automatic teardown.

### Test Data Generation
1. **Hardcoded Fixtures**: Easy to set up initially, but does not scale. Edge cases (like varying string lengths) are rarely tested, and it requires high maintenance when domain entity signatures change.
2. **Faker + Manual Instantiation**: Utilizing the Faker library to generate random data, but manually mapping it to the User entity and its Value Objects. Requires significant boilerplate in the test files.
3. **polyfactory**: A modern data mocking factory that can automatically inspect Python type hints (including complex Dataclasses or Pydantic models) to generate fully populated, randomized objects with minimal configuration.

## Decision
The solution chosen is to adopt Testcontainers for database orchestration and Polyfactory for test data generation in babylon integration test suite.
- testcontainers.postgres.PostgresContainer will replace docker-compose in the conftest.py setup, spinning up an ephemeral database and exposing a dynamically generated DATABASE_URL to the test suite.
- polyfactory will be used to create a UserFactory that dynamically generates User domain entities and their nested Value Objects (UserId, Username, MasterPasswordSalt, etc.) with randomized but type-safe data.

## Consequences
### Positive
* **Total Isolation & Parallelization**: Dynamic port binding means multiple test suites or CI runners can operate simultaneously on the same host without port conflicts.
* **Resilience**: Testcontainers guarantees container teardown even if the Python test process crashes, preventing resource leaks (zombie containers).
* **Fuzz Testing Capability**: Polyfactory's randomized generation acts as a light form of fuzz testing, potentially exposing edge-case validation errors that hardcoded fixtures would mask.

### Negative / Risks
* **Dependency Overhead**: Introduces two additional heavy dependencies (testcontainers, polyfactory) to the dev dependency tree.
* **Learning Curve**: Polyfactory requires custom configuration hooks to properly instantiate complex Domain-Driven Design (DDD) Value Objects that have strict validation rules.