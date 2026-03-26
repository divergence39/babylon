# ADR-002: Backend - Adoption of Clean Architecture

## Status
Accepted

## Context
A Zero-Knowledge password manager contains highly sensitive business rules (e.g., vault access control, token validation, cryptographic payload constraints). If these rules are tightly coupled with the web framework or the database ORM, the codebase becomes brittle, hard to test in isolation, and extremely difficult to migrate in the future. It arise the need of an architectural pattern that enforces a strict separation of concerns, ensuring that the core domain remains completely agnostic of the delivery mechanism (HTTP) and the persistence layer (Database).

## Considered Options
1. **Traditional Layered/MVC Architecture:** Fast initial development, but the core business is tighly coupled with the 'Data layer'.
2. **Clean Architecture (Ports and Adapters):** Enforces the Dependency Rule and guarantees that inner layers (Entities, Use Cases) have no dependencies on outer layers (Controllers, Gateways, DB), but it is more difficult to implement.

## Decision
The choice made was to strictly adhere to Clean Architecture principles for the server side.
- The system will be divided into concentric layers: `Domain` (Entities), `Application` (Use Cases), `Infrastructure` (External APIs, DB), and `Presentation` (Web Framework).
- All communication across layer boundaries must point inwards (Dependency Rule).
- The code will rely heavily on Dependency Injection (DI) and Interfaces to decouple the use cases from specific infrastructure implementations.

## Consequences
### Positive
* **High Testability:** Core business logic can be unit-tested completely in isolation without mocking HTTP requests or spinning up a test database.
* **Framework Independence:** The web framework or the database engine can be swapped with minimal impact on the `Application` and `Domain` layers. 
* **Complete Decoupling:** The Clean Architecture allows to work on the database side, the web framework or the domain logic independtly from the implementation of the other parts, as long as their contracts are defined through Dependency Injection.

### Negative / Risks
* **High Boilerplate:** Implementing strict boundaries requires creating multiple data transfer objects (DTOs) and mapping between them.
* **Development Overhead:** Simple CRUD operations will require more files and lines of code compared to a standard MVC framework.