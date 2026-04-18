# Roadmap: AgentMail

## Phase 1: Core Logic & Cryptography [DONE]
- [x] Create `requirements.txt`.
- [x] Implement `identity.py` for RSA key generation and signing.
- [x] Implement `storage.py` using the Repository Pattern.
- [x] Success Criteria: Independent testing of signing and storage logic passes.

## Phase 2: MCP Integration [DONE]
- [x] Implement `server.py` using `FastMCP`.
- [x] Connect `identity` and `storage` to MCP tools.
- [x] Success Criteria: Server runs via stdio and tools respond correctly.

## Phase 3: Verification & Polish [DONE]
- [x] Create `test_workflow.py` for end-to-end verification.
- [x] Add detailed comments for the "Student" developer.
- [x] Final documentation.

## Phase 4: Milestone v0.2.0 (Sent History & Replying) [DONE]
- [x] Update `storage.py` with dual-persistence (inbox/sent).
- [x] Update `server.py` with `reply_to_id` and `get_sent_history`.
- [x] Verify asynchronous replying logic.
