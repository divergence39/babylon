# ADR-005: User Identification - Username and Salt Management

## Status
Accepted

## Context
Since Babylon is a ZK Password Manager, it require a mechanism to uniquely identify users and map them to their cryptographic salts.
In traditional platforms, an email address is the standard user identifier but, since Babylon is a portfolio project focused on strictly enforcing a Zero-Knowledge Architecture and Clean Architecture principles, an alternative on the standard email identification mechanism should be investigated, because the application does not feature commercial workflows and the operational overhead of managing an email system conflicts with the core educational scope. Furthermore, storing emails introduces Personally Identifiable Information (PII) into the database, weakening the maximum-privacy posture of the system.

## Considered Options
1. **Email Address (Commercial Standard)**: Familiar UX and supports account recovery, but introduces massive systemic complexity (SMTP, verification pipelines) and stores PII.
2. **System-Generated UUIDs**: Immune to enumeration and 100% anonymous, but provides a hostile UX, forcing users to memorize or store an unwieldy string alongside their Master Password.
3. **User-Chosen Nicknames**: Provides a recognizable, user-friendly identifier without requiring PII or external third-party integrations.

## Decision
Babylon will adopt User-Chosen Nicknames as the primary authentication identifier. Each user's Username will be just a nickname chosen by the users themselves.
- This approach entirely avoids the infrastructure overhead of email delivery and verification, keeping the project strictly scoped to its cryptographic and architectural goals.
- It inherently guarantees maximum privacy, as no verifiable real-world identity is required.

### Salt Management Strategy:
To protect the Master Key, the client-side Key Derivation Function (KDF) requires a cryptographic salt. Since nicknames do not provide sufficient entropy, the server will generate a cryptographically secure, random salt upon user registration and store it mapped to the nickname.
During authentication, the client will execute a pre-flight request containing the nickname to fetch this salt. While nicknames are more guessable than UUIDs, introducing a risk of enumeration, the actual security of the derived Master Key remains fully protected by the server-generated salt and the KDF parameters.

## Consequences
### Positive
* **Maximized Privacy**: Zero PII is collected or stored, reinforcing the Zero-Knowledge mandate.
* **Laser-Focused Scope**: Eliminates external dependencies (SMTP), reducing the attack surface and development time.
* **Usable Security**: Users authenticate with a standard, memorable credential.

### Negative / Risks
* **Zero Account Recovery**: Lacking an out-of-band communication channel (email), there is absolutely no mechanism to assist users with locked accounts.
* **Enumeration Attacks**: An attacker could brute-force the pre-flight salt endpoint to map existing users and harvest salts for offline attacks against captured database blobs.

### Mitigations
To counteract the enumeration risk, the system must implement:
* **Strict Rate Limiting**: Throttling requests to the registration and salt-fetch endpoints.
* **Constant-Time Dummy Responses**: If a salt is requested for a non-existent nickname, the server must simulate a delay and return a deterministic, pseudo-random dummy salt. This prevents attackers from easily distinguishing valid users via response timing or payload length.