# ADR-003: Backend Tech Stack - Python and FastAPI

## Status
Accepted

## Context
Having decided on a strict Clean Architecture (ADR-002) for the Zero-Knowledge backend, it arise the need of a runtime and web framework that is capable at handling asynchronous I/O operations, enforce strict data validation, and support modern developer tooling. The system will primarily act as an API acting as a secure conduit for encrypted payloads.

## Considered Options
1. **Python with FastAPI**: Python is an easy language, with ton of libraries as support. FastAPI is modern, specifically designed for handling asynchronous I/O operations fast and ensure strict data validation thanks to pydantic.
2. **Node.js with NestJS**: NestJS natively enforce a modular heavily Dependency Injection-based architecture right out of the box, making Clean Architecture very natural. It has a massive ecosystem.
3. **Go with Gin/Fiber**: Go is statically typed, compiled  and efficient for highly concurrent backend APIs. It has a very small memory footprint.
4. **Rust with Actix-Web**: Rust is statically typed, compiled and ensure memory safety and incredible performances.

## Decision
The choice made was to proceed with Python and FastAPI.
- As already mentioned FastAPI ensure quick responsiveness, data validation and is capable of auto-generate clear documentation directly from the code
- Python is a language already known and, for a solo project, adding too much cognitive load would just increase the risk of bottlenecks.
- Python modules allows for an easy implementation of unit and integration tests, as well as for easy and fast ORM implementation.
- Despite being interpreted, a Zero Knowledge server performs mainly I/O operations, making CPU-bound operations less crucial.

## Consequences
### Positive
* **Faster Development**: Being an interpreted and already kwnown language, Python permits faster code development, allowing to focus on architectural and design problems, rather then on implementation one.
* **FastAPI Robustness and Reliability**: FastAPI allows quick I/O response, ensure data validation and produce well structured API documentation for free.
* **Pythonic Code**: Python allows to write complex and articulated instructions in compacted and readable ways, lightening the codebase size (compensating the boilerplate due to Clean Architecture).

### Negative / Risks
* **Slow Performances**: Being an interpreted language, Python is naturally slower than compiled ones, resulting in reduced performances if compared to the other proposed options.
* **Type Validation**: Python does not esnure authomatic data validation and if FastAPI uses pydantic, the adoption of Clean Architecture prohibits the usage of external libraries inside the inner layers, enforcing the data validation on the test side, with tools such as Mypy.