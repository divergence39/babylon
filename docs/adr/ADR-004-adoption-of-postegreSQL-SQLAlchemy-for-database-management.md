# ADR-004: Database management - PostgreSQL and SQLAlchemy

## Status
Accepted

## Context
Since the Babylon backend operates as a Zero-Knowledge password manager, the server acts as an agnostic storage layer: its primary job is to persist encrypted vault blobs, user identity metadata, and complex sharing permissions. This necessitates a database that satisfies our data persistence requirements, and an Object-Relational Mapping (ORM) solution to interface with it. Having decided on Clean Architecture as a core constraint, another critical requirement is the strict decoupling of the domain logic from the persistence implementation.

## Considered Options

### Database
1. **PostgreSQL (RDBMS)**: A strict, relational database that guarantees ACID properties and referential integrity.
2. **MongoDB (Document/NoSQL)**: A flexible, schema-less document store optimized for heterogeneous JSON-like payloads, allowing for seamless horizontal scaling.

### ORMs / Data Access
1. **SQLAlchemy (Data Mapper Pattern)**: An ORM that maps database entities into pure Python objects without modifying the objects themselves, allowing complete decoupling between business logic and the data persistence mechanism.
2. **Active Record ORMs (Django ORM, Tortoise)**: ORMs where domain models inherit from database classes, allowing for rapid implementation at the cost of architectural coupling.

## Decision
The choice made was to proceed with PostgreSQL, interfaced with SQLAlchemy as data mapper.
- Since the server operates in a zero-knowledge context, the shape of the stored data is higly uniform across all users. This property heavily negates the primary benefit of NoSQL databases like MongoDB.
- While the vault contents are opaque, the authentication and authorization mechanism requires a highly structured and relational data organization. PostgreSQL enforces strict Foreign Key constraints, guaranteeing data consistency at the storage level.
- SQLAlchemy's Data Mapper perfectly couples itself with the chosen Clean Architecture methodology, allowing the Python domain layer to remain completely unaware of the database infrastructure.
- To properly integrate SQLAlchemy in the Clean Architecture of Babylon, the Repository Pattern will be adopted, to abstract the ORM's syntax away from the use-case interactors. Alembic will be used for deterministic database migrations.

## Consequences
### Positive
* **Complete Decoupling**: As already mentioned, SQLAlchemy allows a complete decoupled approach, enforcing clean separation between business rules and data persistance.
* **Data Integrity**: PostgreSQL natively guarantees relational data integrity and provides highly reliable operations via ACID compliance.

### Negative / Risks
* **Schema Rigidity**: Unlike NoSQL stores, RDBMS schemas are rigid. Modifying the data structure requires explicit, carefully managed migrations to avoid database locks. However, given the nature of the project, this is remote possibility with low risk. The schema evolution will be nevertheless be safely managed by Alembic.
* **Code Complexity**: SQLAlchemy introduces a steeper learning curve compared to Active Record ORMS, and requires more boilerplate code (because of the explicit mappers). This will be mitigated by the use of the Repository Pattern, as explained before.