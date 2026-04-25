# ADR-006: Authentication and Encryption - Key-Splitting Mechanism

## Status
Accepted

## Context
In a strict Zero-Knowledge Architecture, the backend must authenticate the user without ever receiving the user's Master Password or the key used to encrypt the vault. If the client uses the Master Password to derive a single cryptographic key and transmits that key to the  server for authentication, the server becomes capable of decrypting the vault, violating the core zero-knowledge mandate.
Therefore, a mechanism to ensure that the server is able to authenticate the user without every being able to decrypt the vault is required.
**Note**: The specific cryptographic algorithms, iterations, and memory constraints used for these derivations are abstracted from this architectural decision. They will be documented and versioned in a dedicated Cryptographic Specification registry.

## Considered Options
1. **Secure Remote Password (SRP) Protocol**: The server and client verify each other's identity without ever exchanging the password or a hash of the password over the network. It provides mathematically proven zero-knowledge password proof, however it is complex to implement securely from scratch, it requires a massive cryptographic overhead and multiple network round-trips.
2. **Single Hash Transmission**: The client hashes the password and sends it; the server compares it. It is trivial to implement, but the hash is then used for both encryption and authentication, violating the ZK constraints.
3. **Key-Splitting via Client-Side Derivation**: The client derives a primary Master Key from the password and the server-provided salt. The primary key is then securely "split" (derived further) into two independent keys: an Encryption Key (which never leaves client memory) and an Authentication Key (which is transmitted to the server). It satisfy the decoupling from authentication and item encryption, but it requires rigorous client-side memory management to ensure the Encryption Key is never accidentally included in network payloads or persisted in local storage.

## Decision
This project will adopt the Key-Splitting methodology via sequential client-side key derivation.
- Upon receiving the unique salt from the server, the client will derive a primary Master Key.
- The client will then derive an Encryption Key solely for local vault operations.
- The client will separately derive an Authentication Key, which will be transmitted to the backend to generate session tokens.
- The mathematical one-way nature of the chosen derivation algorithms will guarantee that the server (holding only the Authentication Key) cannot reverse-engineer the Encryption Key or the Master Password.

## Consequences
### Positive
* **Preserved Zero-Knowledge**: The server remains mathematically incapable of decrypting user vaults, fulfilling the primary security directive.
* **Crypto-Agility**: By separating the architecture from the implementation, the underlying derivation functions can be independently upgraded in the future without altering this authentication flow.
* **Manageable Complexity**: Achieves robust security without the extreme developmental overhead of implementing full SRP.

### Negative / Risks
* **Client-Side Responsibility**: The security of the system relies heavily on the client application's ability to clear the Encryption Key from memory immediately after use, preventing memory-dump attacks.