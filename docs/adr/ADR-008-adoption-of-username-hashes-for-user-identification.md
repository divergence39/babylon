# ADR-008: Username hashing identification

## Status
Accepted --> Superseed **ADR 005**.

## Context
The ADR 005 enstablished the rule of using the usernames as a unique identifier for users. Although this enhance the UX with a user-friendly and easy to use identifier, it brings out problems regarding privacy and security of possible sensitive data of the user:
* The username must be transmitted to the server in order to retrieve the proper KDF configuration of that user, augmenting the riks of credential leakage.
* If the database is compromised, an attacker could have free access to a complete list of users usernames, that could also include personal and sensitive data.
A decision must be made in order to mitigate these problems.

## Considered Options
2. **System-Generated UUIDs**: Immune to enumeration and 100% anonymous, but provides a hostile UX, forcing users to memorize or store an unwieldy string alongside their Master Password, canceling out the benefits of the username usage.
3. **Hashed Usernames (Blind Indexing)**: Thsi mechanism brings the benefit of both a user friendly interface, easy to rememeber credentials, and a safe comunication and a privacy safe storage.

## Decision
Babylon will adopt the hashed usernames. The user will still be completely able to use only their user-friendly usernames to identify themselves. The nicknames will then be hashed and send to the server: in this way the real user's username will never leave the client side.

## Consequences
### Positive
* **Maximized Privacy**: Zero PII is collected or stored, reinforcing the Zero-Knowledge mandate, even more than with standard usernames.
* **Safer Communication and API exposure**: In this way, the API request through HTTP will not have the users' usernames in plain sight, exposing only an hashed value.
* **Usable Security**: Users authenticate with a standard, memorable credential.

### Negative / Risks
* **Zero Account Recovery**: As for the standard username, this option will completely discard the possibility of account recovery if usernames or master password are forgotten.


