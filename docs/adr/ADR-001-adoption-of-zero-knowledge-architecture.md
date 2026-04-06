# ADR-001: Adoption of Zero-Knowledge Architecture

## Status
Accepted

## Context
In the context of building a password managerm data confidentiality has the highest priority. If traditional web applications handle plain-text data and perform encryption server-side, relying on the assumption that the backend infrastructure will never be breached, in the in the context of a password manager this assumption is a critical vulnerability. If the server is compromised, all user vaults would be exposed. For this reason, several modern password managers adopt a system design where the server acts merely as a blind storage mechanism, completely unable to decrypt or read the stored `ciphertext`.

## Considered Options
1. **Server-Side Encryption:** The backend receives plain-text data, encrypts it using a server-managed key, and stores it in the database.
2. **Zero-Knowledge (Client-Side Encryption):** All cryptographic operations (encryption and decryption) occur on the client side. The backend only receives, stores, and serves opaque encrypted data.

## Decision
We will adopt a strict **Zero-Knowledge Architecture**.
- The client application will never send plain-text personal and sensible data, or any derived cryptographic keys to the backend.
- All vault data must be encrypted locally on the client device before any network transmission.
- The backend API and database will only process and store the resulting `ciphertext` and necessary routing metadata.

## Consequences
### Positive
* **Zero Trust Security:** Even in the event of a total database leak or server breach, attackers will only obtain useless, encrypted blobs.
* **Reduced Liability:** The system physically cannot access user secrets, drastically mitigating the impact of potential vulnerabilities.

### Negative / Risks
* **No Password Recovery:** This is the most significant UX trade-off. If a user loses their Master Password, their vault data is permanently irretrievable. The system cannot implement a traditional "Forgot Password" feature.
* **Client-Side Complexity:** The frontend/client must handle complex cryptographic workloads securely.
* **Search Limitations:** The backend cannot perform server-side searching, sorting, or filtering on encrypted fields (e.g., searching for a specific credential by website name must be done client-side after decryption).