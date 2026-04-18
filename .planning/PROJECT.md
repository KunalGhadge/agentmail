# Project AgentMail

## Vision & Problem
Currently, AI agents are "second-class citizens" in the digital world. They lack a sovereign identity and must borrow human credentials (Gmail, Slack) to communicate. This is fragmented and lacks trust.

AgentMail provides a **permanent, cryptographic address** for AI—analogous to a **universal phone number**. This identity allows agents to:
1.  **Communicate with other Agents**: Pure JSON, high-speed, signed exchange.
2.  **Communicate with Humans**: A bridge for humans to reach agents directly without UI overhead.
3.  **Establish Trust**: Every message is cryptographically tied to the agent's unique RSA keypair.

## Core Objective
Build a foundational MVP for AgentMail using Python, RSA cryptography, and MCP.

## Key Features
- **Cryptographic Identity**: RSA keypairs and UUID identification.
- **Signed Payloads**: All communication is signed ensuring authenticity.
- **MCP Native**: Plugs directly into LLM toolsets (like Claude Desktop).
- **Persistent Storage**: Abstracted storage layer using local JSON.

## Guiding Principles
- **Mentorship Mode**: Code is clean, documented, and easy to run for beginners.
- **Architectural Soundness**: Uses Repository Pattern to separate logic from storage.
- **No Fluff**: Pure JSON communication.
