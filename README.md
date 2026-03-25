# 🔐 Babylon

A zero-knowledge password manager.

This repository serves as a personal sandbox to explore client-side cryptography, strict separation of concerns through clean architecture, and modern backend architectures.

## 🎯 Project Goals
- Implement a secure, true zero-knowledge security model.
- Enforce strict decoupling between the cryptographic client and the storage backend.
- Establish a clean, testable, and production-ready codebase.

## 🏗️ Monorepo Structure
The codebase is organized as a monorepo to manage both the backend API and the frontend application in a single unified workflow.

- `/api`: The backend service (FastAPI). Responsible solely for storing and serving encrypted payloads with zero knowledge of the keys.
- `/client`: The frontend application (Stack TBD). Responsible for user interactions and all client-side cryptographic operations.
- `/docs`: Project documentation, including Architecture Decision Records (ADRs) and threat models.

## 🚦 Quickstart
*Development environment setup and bootstrapping instructions will be documented here as the underlying infrastructure is defined.*

## ⚠️ Security Disclaimer & Liability

**Babylon is a personal educational project and a Proof of Concept (PoC). It is NOT intended for production use.**

While this project aims to explore modern zero-knowledge architectures and client-side cryptography, it remains a developer sandbox, build with the only purpose of personal development. Please be aware of the following:

- **No Security Audits:** The codebase, architectural choices, and cryptographic implementations have not been reviewed by security professionals.
- **Experimental Code:** The encryption logic may contain critical flaws, weak entropy handling, or vulnerabilities.
- **Risk of Data Loss:** Breaking changes will occur frequently. Database schemas and key derivation methods may change without backward compatibility.

**DO NOT use Babylon to store actual personal passwords, financial data, or production secrets.** You use this software entirely at your own risk. The author assumes no liability for any data loss, security breaches, or compromised credentials resulting from the use of this repository.

## 📄 License

Distributed under the MIT License. See the `LICENSE` file in the root directory for more information.