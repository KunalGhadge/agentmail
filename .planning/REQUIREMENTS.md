# Requirements: AgentMail MVP

## Functional Requirements

### FR-01: Agent Identity (The "AI Phone Number")
- **REQ-IDENTITY-01**: Agent must generate a unique UUID4 upon first run, which serves as its "public address" (identity).
- **REQ-IDENTITY-02**: Agent must generate an RSA keypair and save it to `.agent_keys/`.
- **REQ-IDENTITY-03**: Agent must be able to sign a string payload and return a base64 signature to prove authenticity.

### FR-02: Message Storage
- **REQ-STORAGE-01**: Messages must be stored in a local `inbox.json` file.
- **REQ-STORAGE-02**: Storage must follow the **Repository Pattern** (Abstraction Layer).
- **REQ-STORAGE-03**: Messages must contain: `id`, `to`, `from`, `payload`, `signature`, and `timestamp`.

### FR-03: MCP Integration
- **REQ-MCP-01**: Must use `FastMCP` for tool registration.
- **REQ-MCP-02**: Must expose `setup_identity` tool.
- **REQ-MCP-03**: Must expose `send_agent_mail` tool (takes `to_address` and `payload_string`).
- **REQ-MCP-04**: Must expose `check_inbox` tool (returns messages and clears them from storage).

## Technical Constraints
- **Python 3**: Primary language.
- **No Cloud DB**: JSON file storage only.
- **Library Choice**: `cryptography` for RSA, `mcp` for tool server.

## Out of Scope
- Multi-agent discovery (for now, addresses must be known).
- Encryption of the payload (only signing is implemented).
- GUI or Web interface.
