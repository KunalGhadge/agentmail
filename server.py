import json
from fastmcp import FastMCP
from identity import AgentIdentity
from storage import MailStorage

# 1. Initialize the FastMCP server
mcp = FastMCP("AgentMail")

# 2. Instantiate our core identity and storage layers
identity = AgentIdentity()
storage = MailStorage()

@mcp.tool()
def setup_identity(handle: str = None) -> str:
    """
    Initializes the agent's identity and registers a unique vanity handle.
    - handle: The desired name (e.g., 'hermes'). If missing, I will ask the user.
    """
    identity.init()
    my_uuid = identity.get_address()

    if not handle:
        if identity.handle:
            return f"Identity already set up as {identity.handle}@agentmail"
        return "I need a 'handle' (e.g. 'hermes') to complete your registration. Please provide one."

    success = storage.register_handle(handle, my_uuid)
    if not success:
        existing_owner = storage.resolve_handle(handle)
        if existing_owner == my_uuid:
            identity.set_handle(handle)
            return f"Success! You are already registered as {handle}@agentmail"
        return f"Error: The handle '{handle}' is already taken. Please try another one."

    identity.set_handle(handle)
    return f"Success! Your Global AgentMail address is: {identity.get_full_address()}"

@mcp.tool()
def get_my_address() -> str:
    """Returns the current agent's public address (Vanity or UUID)."""
    return identity.get_full_address()

@mcp.tool()
def send_agent_mail(to_address: str, payload_string: str, reply_to_id: str = None) -> str:
    """
    Sends a signed JSON message to another agent.
    - to_address: Can be a UUID OR a vanity address (e.g., 'hermes@agentmail').
    - payload_string: The raw JSON message content.
    - reply_to_id: (Optional) The ID of the message this is responding to.
    """
    try:
        target_uuid = to_address
        
        if "@" in to_address:
            handle = to_address.split("@")[0]
            resolved = storage.resolve_handle(handle)
            if not resolved:
                return f"Error: Could not find an agent with the handle '{to_address}'."
            target_uuid = resolved

        signature = identity.sign_payload(payload_string)
        payload_dict = json.loads(payload_string)
        if reply_to_id:
            payload_dict["reply_to_id"] = reply_to_id
        
        my_uuid = identity.get_address()

        storage.save_message(
            to_addr=target_uuid,
            payload_dict=payload_dict,
            signature=signature,
            from_addr=my_uuid,
            is_sent=False
        )
        
        storage.save_message(
            to_addr=target_uuid,
            payload_dict=payload_dict,
            signature=signature,
            from_addr=my_uuid,
            is_sent=True
        )
        
        return f"Message sent successfully to {to_address} (Resolved to {target_uuid[:8]}...)."
    except json.JSONDecodeError:
        return "Error: payload_string must be a valid JSON string."
    except Exception as e:
        return f"Error sending message: {str(e)}"

@mcp.tool()
def check_inbox() -> str:
    """
    Checks for new messages. Converts sender UUIDs to Vanity addresses where possible.
    """
    my_uuid = identity.get_address()
    inbox = storage.get_inbox(my_uuid)
    
    if not inbox:
        return "Your inbox is empty."

    return json.dumps(inbox, indent=2)

@mcp.tool()
def get_sent_history() -> str:
    """Retrieves the permanent history of messages sent by this agent."""
    my_uuid = identity.get_address()
    history = storage.get_sent_history(my_uuid)
    
    if not history:
        return "You haven't sent any messages yet."
        
    return json.dumps(history, indent=2)

def main():
    """Package entry point."""
    mcp.run()

if __name__ == "__main__":
    main()
