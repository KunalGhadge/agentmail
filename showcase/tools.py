import os
import json
import shutil
from identity import AgentIdentity
from storage import MailStorage

class AgentMailToolkit:
    """
    A toolkit that provides AgentMail protocol capabilities to an Agno agent.
    Each instance represents a specific agent's 'Mailbox' connection.
    """

    def __init__(self, handle: str):
        self.handle = handle
        # Isolate keys per agent handle to prevent shared memory
        self.base_dir = f".showcase_{handle}"
        os.makedirs(self.base_dir, exist_ok=True)
        
        self.identity = AgentIdentity(
            key_dir=os.path.join(self.base_dir, "keys"),
            id_file=os.path.join(self.base_dir, "id.txt"),
            handle_file=os.path.join(self.base_dir, "handle.txt")
        )
        self.storage = MailStorage()

    def setup_identity(self) -> str:
        """
        Initializes the agent's identity and registers the handle to the Global Post Office.
        Must be called once before sending messages.
        """
        self.identity.init()
        my_uuid = self.identity.get_address()
        
        # Sync with global registry
        success = self.storage.register_handle(self.handle, my_uuid)
        if not success:
            existing_owner = self.storage.resolve_handle(self.handle)
            if existing_owner == my_uuid:
                self.identity.set_handle(self.handle)
                return f"Success! Identity re-initialized as {self.handle}@agentmail"
            return f"Error: Identity conflict. Handle '{self.handle}' belongs to another UUID."
        
        self.identity.set_handle(self.handle)
        return f"Success! Registered Global Identity: {self.identity.get_full_address()}"

    def get_my_address(self) -> str:
        """Returns the current agent's unique AgentMail address."""
        return self.identity.get_full_address()

    def send_agent_mail(self, to_address: str, info_to_send: str) -> str:
        """
        Sends a cryptographically signed message to another agent.
        - to_address: The handle of the recipient (e.g., 'openclaw@agentmail').
        - info_to_send: The text content or JSON-formatted info to send.
        """
        try:
            target_uuid = to_address
            
            # Resolve handle if necessary
            if "@" in to_address:
                handle_part = to_address.split("@")[0]
                resolved = self.storage.resolve_handle(handle_part)
                if not resolved:
                    return f"Error: Could not resolve handle '{to_address}'. Are they registered?"
                target_uuid = resolved

            # Prepare payload (ensure it is a dict for the storage layer)
            payload_dict = {"content": info_to_send}
            payload_json = json.dumps(payload_dict)
            
            # Sign and Sync
            signature = self.identity.sign_payload(payload_json)
            my_uuid = self.identity.get_address()

            # 1. Sync to Recipient's Inbox (This is the 'Global Post Office Relay')
            self.storage.save_message(
                to_addr=target_uuid,
                payload_dict=payload_dict,
                signature=signature,
                from_addr=my_uuid,
                is_sent=False
            )
            
            # 2. Sync to My Sent History (For local audit)
            self.storage.save_message(
                to_addr=target_uuid,
                payload_dict=payload_dict,
                signature=signature,
                from_addr=my_uuid,
                is_sent=True
            )
            
            return f"SENT SUCCESS: Message sent to {to_address}. Status: Synced to Post Office."
        except Exception as e:
            return f"ERROR: Failed to send mail: {str(e)}"

    def check_inbox(self) -> str:
        """
        Checks for new incoming messages from other agents. 
        Returns real-time data from the Global Post Office.
        """
        my_uuid = self.identity.get_address()
        messages = self.storage.get_inbox(my_uuid)
        
        if not messages:
            return "No new messages in your inbox."
            
        # Format for agent readability
        formatted = []
        for msg in messages:
            sender = msg['from_addr']
            # Try to resolve handle for friendlier display
            # (Note: In a real protocol, we'd have a reverse lookup cache)
            content = msg['payload'].get('content', 'No content')
            formatted.append(f"FROM: {sender}\nCONTENT: {content}\nID: {msg['id']}")
            
        return "\n---\n".join(formatted)

    def get_tools(self):
        """Returns the list of tools to be used by Agno agent."""
        return [self.setup_identity, self.get_my_address, self.send_agent_mail, self.check_inbox]
